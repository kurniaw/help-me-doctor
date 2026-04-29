import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agents.state import AgentState
from app.config import get_settings
from app.schemas.agent import RouterOutput

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """You are an expert medical and legal triage router for Singapore.

Analyze the user's message and respond with a JSON object containing:
- pathway: one of MEDICAL, LEGAL, DUAL, OCCUPATIONAL
  - MEDICAL: health symptoms, illness, injury needing medical care
  - LEGAL: crime, assault, abuse, accident needing legal action
  - DUAL: both medical AND legal (e.g., assault causing injury)
  - OCCUPATIONAL: workplace injury (may need both MOM reporting + medical)
- urgency: one of CRITICAL, HIGH, MEDIUM, LOW
  - CRITICAL: life-threatening (chest pain, stroke, severe bleeding, unconscious, can't breathe, overdose, active assault, suicide)
  - HIGH: serious but not immediately life-threatening (severe or worsening pain, trauma, high fever, acute illness needing same-day care)
  - MEDIUM: needs a clinic/GP visit but not urgent (mild-to-moderate symptoms, routine concern, minor legal query, symptoms present for days, seeking a specific health service such as "find a clinic", "recommend a doctor", "where can I get tested", "blood test", "health screening")
  - LOW: pure informational queries with no intent to seek care (e.g. "what is diabetes?", "how does aspirin work?", "is it normal to feel tired sometimes?", post-recovery follow-up questions). Do NOT classify as LOW if the user is asking where to go, what service to use, or wants a recommendation.
- medical_keywords: list of medical terms extracted (symptoms, body parts, conditions)
- legal_keywords: list of legal terms extracted (crime type, perpetrator, circumstances)
- reasoning: brief explanation of your classification

Singapore context: CHAS clinics for non-urgent; SGH, TTSH, NUH, KKH for hospitals; 999 for police/emergency, 995 for ambulance.

Always output valid JSON matching the schema."""

# Keyword fallback heuristics
CRITICAL_SIGNALS = [
    "chest pain", "heart attack", "stroke", "can't breathe", "not breathing",
    "unconscious", "severe bleeding", "bleeding heavily", "stabbed", "shot",
    "overdose", "suicide", "rape", "sexual assault", "child abuse",
]
HIGH_SIGNALS = [
    "severe", "emergency", "urgent", "pain", "injury", "trauma", "accident",
    "assault", "attacked", "punched", "hit", "broken", "fracture",
]
LOW_SIGNALS = [
    "what is", "how does", "can you explain", "general question",
    "curious", "wondering", "information about", "just asking",
    "is it normal", "follow up", "follow-up",
    "preventive", "prevention", "vaccine",
]
# Signals that override LOW back to MEDIUM — user wants a service, not just information
MEDIUM_OVERRIDE_SIGNALS = [
    "recommend", "find", "nearest", "nearby", "where can", "where to",
    "clinic", "hospital", "doctor", "testing", "test for", "screening",
    "appointment", "book", "visit",
]
LEGAL_WORDS = [
    "assault", "rape", "abuse", "punch", "stab", "knife", "police",
    "accident", "workplace", "injury", "crime", "attacked", "robbed",
    "harassed", "molest", "domestic violence", "arrested",
]
MEDICAL_WORDS = [
    "pain", "fever", "cough", "symptom", "condition", "disease", "injury",
    "bleeding", "headache", "dizzy", "nausea", "vomit", "rash", "swelling",
    "breathing", "heart", "chest", "stomach", "back", "leg", "arm", "head",
]


def _keyword_fallback(user_message: str) -> dict[str, Any]:
    """Keyword-based heuristic classification when LLM fails."""
    lower = user_message.lower()

    medical_kw = [w for w in MEDICAL_WORDS if w in lower]
    legal_kw = [w for w in LEGAL_WORDS if w in lower]

    has_medical = bool(medical_kw)
    has_legal = bool(legal_kw)

    if has_medical and has_legal:
        pathway = "DUAL"
    elif has_legal:
        pathway = "LEGAL"
        if "workplace" in lower or "work" in lower:
            pathway = "OCCUPATIONAL"
    else:
        pathway = "MEDICAL"

    if any(sig in lower for sig in CRITICAL_SIGNALS):
        urgency = "CRITICAL"
    elif any(sig in lower for sig in HIGH_SIGNALS):
        urgency = "HIGH"
    elif any(sig in lower for sig in LOW_SIGNALS) and not any(sig in lower for sig in MEDIUM_OVERRIDE_SIGNALS):
        urgency = "LOW"
    else:
        urgency = "MEDIUM"

    return {
        "pathway": pathway,
        "urgency": urgency,
        "medical_keywords": medical_kw[:5],
        "legal_keywords": legal_kw[:5],
        "reasoning": "Keyword-based fallback classification",
    }


async def input_router_node(state: AgentState) -> AgentState:
    """Agent 1: Parse user input, detect urgency, classify pathway."""
    user_message = state.get("user_message", "")
    settings = get_settings()

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.1,
        )
        structured_llm = llm.with_structured_output(RouterOutput)

        messages = [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        result = await structured_llm.ainvoke(messages)

        if isinstance(result, RouterOutput):
            return AgentState(
                **state,
                pathway=result.pathway.value,
                urgency_level=result.urgency.value,
                medical_keywords=result.medical_keywords,
                legal_keywords=result.legal_keywords,
            )
    except Exception as e:
        logger.warning("LLM router failed, using keyword fallback: %s", e)

    # Keyword fallback
    fallback = _keyword_fallback(user_message)
    return AgentState(
        **state,
        pathway=fallback["pathway"],
        urgency_level=fallback["urgency"],
        medical_keywords=fallback["medical_keywords"],
        legal_keywords=fallback["legal_keywords"],
    )
