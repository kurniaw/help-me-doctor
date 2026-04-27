import json
import logging
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.agents.graph import get_compiled_graph
from app.agents.state import AgentState
from app.dependencies import get_current_user
from app.models.chat import ChatSessionDocument
from app.models.user import UserDocument
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


async def _stream_response(
    user_message: str,
    session_id: str,
    user_id: str,
) -> AsyncGenerator[str, None]:
    """Run the LangGraph pipeline and stream SSE events."""
    graph = get_compiled_graph()

    initial_state = AgentState(
        user_message=user_message,
        session_id=session_id,
    )

    try:
        full_response = ""
        urgency = "MEDIUM"
        pathway = "MEDICAL"

        # Stream events from LangGraph
        async for event in graph.astream_events(initial_state, version="v2"):
            kind = event.get("event", "")

            # Capture on_chat_model_stream events from the formatter node
            if kind == "on_chat_model_stream" and event.get("name") == "formatter":
                chunk_data = event.get("data", {})
                chunk = chunk_data.get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    content = str(chunk.content)
                    # Strip the URGENCY: prefix line from the stream
                    if content.startswith("URGENCY:"):
                        line, _, rest = content.partition("\n")
                        urgency = line.replace("URGENCY:", "").strip()
                        content = rest
                    full_response += content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content, 'urgency': urgency, 'pathway': pathway})}\n\n"

            # Capture final state when graph completes
            elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                output = event.get("data", {}).get("output", {})
                urgency = output.get("urgency_level", urgency)
                pathway = output.get("pathway", pathway)

                # If formatter didn't stream (fallback path), emit full response
                formatted = output.get("formatted_response", "")
                if formatted and not full_response:
                    # Strip URGENCY prefix
                    if formatted.startswith("URGENCY:"):
                        first_line, _, rest = formatted.partition("\n")
                        urgency = first_line.replace("URGENCY:", "").strip()
                        formatted = rest.lstrip("\n")
                    full_response = formatted
                    yield f"data: {json.dumps({'type': 'chunk', 'content': formatted, 'urgency': urgency, 'pathway': pathway})}\n\n"

                # Persist conversation to MongoDB
                try:
                    session = await ChatSessionDocument.find_one(
                        ChatSessionDocument.user_id == user_id
                        if session_id == "new"
                        else ChatSessionDocument.id == session_id  # type: ignore[attr-defined]
                    )
                    if not session:
                        session = ChatSessionDocument(user_id=user_id, messages=[])
                        await session.insert()

                    session.messages.append(
                        {
                            "role": "user",
                            "content": user_message,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    )
                    session.messages.append(
                        {
                            "role": "assistant",
                            "content": full_response,
                            "urgency": urgency,
                            "pathway": pathway,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    )
                    await session.save()
                except Exception as db_err:
                    logger.warning("Failed to persist chat session: %s", db_err)

        yield f"data: {json.dumps({'type': 'done', 'content': '', 'urgency': urgency, 'pathway': pathway})}\n\n"

    except Exception as e:
        logger.error("Graph execution error: %s", e)
        yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred. Please try again.', 'urgency': 'MEDIUM', 'pathway': 'MEDICAL'})}\n\n"


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: UserDocument = Depends(get_current_user),
) -> StreamingResponse:
    session_id = payload.session_id or str(uuid.uuid4())

    return StreamingResponse(
        _stream_response(
            user_message=payload.message,
            session_id=session_id,
            user_id=str(current_user.id),
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
