"""Agent 3: CoordinatorAgent — deterministic dual-case coordination (no LLM call).

Only invoked when pathway == DUAL. Sequences medical + legal actions based on urgency.
"""
from app.agents.state import AgentState, CoordinationPhase, CoordinationPlan


async def coordinator_node(state: AgentState) -> AgentState:
    """Coordinate medical + legal results for DUAL pathway cases."""
    urgency = state.get("urgency_level", "HIGH")
    hospitals = state.get("hospitals", [])
    doctors = state.get("doctors", [])
    legal_cases = state.get("legal_cases", [])
    forensic_specialists = state.get("forensic_specialists", [])
    authorities = state.get("authorities")

    # Phase 1: Emergency / first action
    if urgency == "CRITICAL":
        phase_1 = CoordinationPhase(
            action="Call 999 immediately",
            reason="CRITICAL medical emergency with criminal case — ambulance and police required",
            note="Preserve all evidence — do NOT bathe, shower, or change clothes",
        )
    elif urgency == "LOW":
        phase_1 = CoordinationPhase(
            action="Visit a GP or CHAS clinic at your convenience if needed",
            reason="No immediate danger — a general health consultation is sufficient",
            note="Telehealth services are also available if you prefer",
        )
    else:  # HIGH or MEDIUM
        phase_1 = CoordinationPhase(
            action="Proceed to hospital emergency department or nearest GP",
            reason="Medical assessment needed first; evidence collected during examination",
            note="Bring a trusted person for support if possible",
        )

    # Phase 2: Hospital / medical
    if hospitals and doctors:
        hospital = hospitals[0]
        doctor = doctors[0]
        phase_2 = CoordinationPhase(
            action=f"Go to {hospital.get('hospital_name', 'nearest hospital')}",
            phone=hospital.get("emergency_hotline") or hospital.get("phone_main", ""),
            contact=f"Request {doctor.get('doctor_name', 'on-call specialist')} ({doctor.get('mcr_number', '')})",
            note="Inform hospital this is a legal case — they will initiate evidence preservation protocol",
        )
    else:
        phase_2 = CoordinationPhase(
            action="Go to nearest hospital emergency department",
            phone="995",
            note="Inform hospital this is a legal case",
        )

    # Phase 3: Legal / police
    police_contact = "999"
    if authorities:
        police_contact = authorities.get("police_contact", "999")
    specialist_name = forensic_specialists[0].get("doctor_name", "") if forensic_specialists else ""

    phase_3 = CoordinationPhase(
        action=f"Contact police: {police_contact}",
        contact=specialist_name,
        note="Police will coordinate with hospital for evidence chain of custody. Medical report becomes legal evidence.",
    )

    # Key coordination points
    key_coordination = [
        "Medical examination and evidence collection happen simultaneously at hospital",
        "Do NOT bathe, shower, or change clothes before examination",
        "Hospital will document injuries with photographs",
        "Police will coordinate with hospital for chain of custody",
        "Medical report becomes primary legal evidence",
    ]

    if legal_cases:
        case_type = legal_cases[0].get("case_type", "")
        if "sexual" in case_type.lower():
            key_coordination.append("PASE (Police Assault Sexual Evidence) kit will be collected")
        if "child" in case_type.lower():
            key_coordination.append("Child welfare services will be notified automatically")

    plan = CoordinationPlan(
        phase_1=phase_1,
        phase_2=phase_2,
        phase_3=phase_3,
        key_coordination=key_coordination,
    )

    return AgentState(**state, coordination_plan=plan)
