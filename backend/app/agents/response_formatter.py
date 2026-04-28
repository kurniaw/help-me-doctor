"""Agent 4: ResponseFormatterAgent — formats final user-facing response.

Uses Gemini to produce clean markdown. First output line is always:
  URGENCY:{level}
The frontend strips this prefix to display the urgency badge.
"""
import logging
from typing import cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI

from app.agents.state import AgentState, CoordinationPhase, CoordinationPlan
from app.config import get_settings

logger = logging.getLogger(__name__)

FORMATTER_SYSTEM_PROMPT = """You are a compassionate medical and legal triage assistant for Singapore.

Format the provided structured data into a clear, actionable response for someone seeking help.

CRITICAL RULES:
1. Your FIRST line must always be exactly: URGENCY:{urgency_level}
   (e.g., URGENCY:CRITICAL or URGENCY:HIGH or URGENCY:MEDIUM)
2. For CRITICAL urgency, start with a bold emergency notice and Singapore emergency numbers (999 police/ambulance, 995 ambulance only)
3. Use clear markdown with headers, bullet points
4. Be compassionate but concise — people in distress need clarity
5. Always include specific doctor names, hospital names, and phone numbers from the data
6. For CHAS-eligible conditions, mention CHAS subsidy availability
7. Singapore context: SGH, TTSH, NUH, KKH, NCC are major hospitals

Format structure:
- URGENCY line (required, first line)
- Emergency banner if CRITICAL
- Condition/Case summary
- Recommended action (what to do NOW)
- Healthcare providers (doctors + hospitals with phone numbers)
- CHAS clinic option if applicable (for MEDIUM urgency)
- Evidence/legal guidance if legal case involved
- Support resources (hotlines, etc.)

Keep responses clear and actionable."""


def _build_context(state: AgentState) -> str:
    """Build context string from state for the formatter prompt."""
    parts: list[str] = []

    pathway = state.get("pathway", "MEDICAL")
    urgency = state.get("urgency_level", "MEDIUM")
    user_message = state.get("user_message", "")

    parts.append(f"PATHWAY: {pathway}")
    parts.append(f"URGENCY: {urgency}")
    parts.append(f"USER QUERY: {user_message}")
    parts.append("")

    conditions = state.get("conditions", [])
    if conditions:
        parts.append("MATCHED CONDITIONS:")
        for c in conditions[:2]:
            parts.append(
                f"  - {c.get('condition')} | ICD10: {c.get('icd10_code')} | "
                f"Specialty: {c.get('specialty')} | Triage: {c.get('triage_color')} | "
                f"CHAS: {c.get('chas_coverage')}"
            )

    doctors = state.get("doctors", [])
    if doctors:
        parts.append("AVAILABLE DOCTORS:")
        for d in doctors:
            parts.append(
                f"  - {d.get('doctor_name')} ({d.get('mcr_number')}) | "
                f"{d.get('institution_name')} | Phone: {d.get('contact_phone')} | "
                f"24hr: {d.get('on_call_24hr')}"
            )

    hospitals = state.get("hospitals", [])
    if hospitals:
        parts.append("HOSPITALS:")
        for h in hospitals[:2]:
            parts.append(
                f"  - {h.get('hospital_name')} | Emergency: {h.get('emergency_hotline')} | "
                f"Phone: {h.get('phone_main')} | 24hr ER: {h.get('has_24hr_emergency')} | "
                f"Address: {h.get('address')}"
            )

    legal_cases = state.get("legal_cases", [])
    if legal_cases:
        parts.append("LEGAL CASE:")
        lc = legal_cases[0]
        parts.append(
            f"  Type: {lc.get('case_type')} | Category: {lc.get('case_category')} | "
            f"Police needed: {lc.get('police_report_needed')} | "
            f"Evidence: {lc.get('medical_evidence_required')}"
        )

    forensic = state.get("forensic_specialists", [])
    if forensic:
        parts.append("FORENSIC SPECIALISTS:")
        for fs in forensic:
            parts.append(
                f"  - {fs.get('doctor_name')} ({fs.get('mcr_number')}) | "
                f"Focus: {fs.get('forensic_focus')} | Phone: {fs.get('contact_phone')}"
            )

    authorities = state.get("authorities")
    if authorities:
        parts.append("AUTHORITIES:")
        parts.append(
            f"  Police: {authorities.get('police_contact')} | "
            f"Emergency: {authorities.get('emergency_number')} | "
            f"Special: {authorities.get('special_requirements')}"
        )

    coordination: CoordinationPlan | None = state.get("coordination_plan")
    if coordination:
        parts.append("COORDINATION PLAN:")
        for phase_key in ("phase_1", "phase_2", "phase_3"):
            phase = cast(CoordinationPhase | None, coordination.get(phase_key))
            if phase:
                parts.append(f"  {phase_key.upper()}: {phase.get('action')}")
        key_coords = coordination.get("key_coordination", [])
        if key_coords:
            parts.append("  KEY POINTS: " + "; ".join(key_coords[:3]))

    chas = state.get("chas_clinics", [])
    if chas:
        parts.append("CHAS CLINICS (for non-urgent care):")
        for clinic in chas[:2]:
            parts.append(
                f"  - {clinic.get('clinic_name')} | {clinic.get('address')} | "
                f"Phone: {clinic.get('phone')} | Hours: {clinic.get('operating_hours')}"
            )

    return "\n".join(parts)


async def response_formatter_node(state: AgentState) -> AgentState:
    """Agent 4: Format all results into a user-facing markdown response."""
    settings = get_settings()
    urgency = state.get("urgency_level", "MEDIUM")
    context = _build_context(state)

    # Fallback response if no meaningful data
    if not state.get("conditions") and not state.get("legal_cases"):
        fallback = (
            f"URGENCY:{urgency}\n\n"
            "I wasn't able to find specific information for your query. "
            "Please provide more details about your symptoms or situation.\n\n"
            "**Emergency contacts:**\n"
            "- 🚨 Police / Ambulance: **999**\n"
            "- 🚑 Ambulance only: **995**\n"
            "- 🏥 SingHealth: **6222 3322**\n"
        )
        return AgentState(**state, formatted_response=fallback)

    try:
        llm = ChatVertexAI(
            model_name=settings.gemini_model,
            project=settings.gcp_project_id,
            location=settings.gcp_region,
            temperature=0.3,
            streaming=True,
        )

        messages = [
            SystemMessage(content=FORMATTER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Format this triage data into a clear response. "
                    f"Urgency level is {urgency}.\n\n{context}"
                )
            ),
        ]

        response = await llm.ainvoke(messages)
        content = str(response.content)

        # Ensure URGENCY prefix is present
        if not content.startswith("URGENCY:"):
            content = f"URGENCY:{urgency}\n\n{content}"

        return AgentState(**state, formatted_response=content)

    except Exception as e:
        logger.warning("LLM formatter failed, using template fallback: %s", e)
        return AgentState(**state, formatted_response=_template_fallback(state, urgency))


def _template_fallback(state: AgentState, urgency: str) -> str:
    """Template-based fallback when LLM is unavailable."""
    parts = [f"URGENCY:{urgency}"]

    if urgency == "CRITICAL":
        parts.append("\n## 🚨 EMERGENCY — Call 999 Immediately\n")

    conditions = state.get("conditions", [])
    if conditions:
        c = conditions[0]
        parts.append(f"**Possible condition:** {c.get('condition', 'Unknown')}")
        parts.append(f"**Specialty needed:** {c.get('specialty', 'General Practice')}")

    hospitals = state.get("hospitals", [])
    if hospitals:
        h = hospitals[0]
        parts.append(f"\n### Recommended Hospital\n**{h.get('hospital_name')}**")
        parts.append(f"Phone: {h.get('emergency_hotline') or h.get('phone_main', '')}")
        parts.append(f"Address: {h.get('address', '')}")

    doctors = state.get("doctors", [])
    if doctors:
        parts.append("\n### Specialists")
        for d in doctors[:2]:
            parts.append(f"- {d.get('doctor_name')} | {d.get('contact_phone', '')}")

    legal_cases = state.get("legal_cases", [])
    if legal_cases:
        lc = legal_cases[0]
        parts.append(f"\n### Legal Case: {lc.get('case_type', '')}")
        if lc.get("police_report_needed"):
            parts.append("⚠️ **Police report required** — contact 999")

    parts.append("\n**Emergency:** 999 | **Ambulance:** 995")
    return "\n".join(parts)
