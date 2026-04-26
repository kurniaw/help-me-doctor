from langgraph.graph import END, StateGraph

from app.agents.coordinator import coordinator_node
from app.agents.input_router import input_router_node
from app.agents.knowledge_matcher import knowledge_matcher_node
from app.agents.response_formatter import response_formatter_node
from app.agents.state import AgentState


def _should_coordinate(state: AgentState) -> str:
    """Conditional edge: route to coordinator only for DUAL pathway."""
    pathway = state.get("pathway", "MEDICAL")
    return "coordinator" if pathway == "DUAL" else "formatter"


def build_graph() -> StateGraph:
    graph: StateGraph = StateGraph(AgentState)

    graph.add_node("router", input_router_node)
    graph.add_node("matcher", knowledge_matcher_node)
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("formatter", response_formatter_node)

    graph.set_entry_point("router")
    graph.add_edge("router", "matcher")
    graph.add_conditional_edges(
        "matcher",
        _should_coordinate,
        {"coordinator": "coordinator", "formatter": "formatter"},
    )
    graph.add_edge("coordinator", "formatter")
    graph.add_edge("formatter", END)

    return graph


# Singleton compiled graph
_compiled_graph = None


def get_compiled_graph():  # type: ignore[return]
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph().compile()
    return _compiled_graph
