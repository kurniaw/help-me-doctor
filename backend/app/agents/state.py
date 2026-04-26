from typing import Optional, TypedDict


class ConditionMatch(TypedDict, total=False):
    condition: str
    icd10_code: str
    specialty: str
    sub_specialty: str
    urgency: str
    triage_color: str
    chas_coverage: str
    hospital_type: str
    vertex_id: str


class DoctorMatch(TypedDict, total=False):
    mcr_number: str
    doctor_name: str
    specialty: str
    institution_name: str
    contact_phone: str
    on_call_24hr: bool
    chas_accredited: bool
    years_in_practice: int


class HospitalMatch(TypedDict, total=False):
    hospital_id: str
    hospital_name: str
    hospital_type: str
    address: str
    phone_main: str
    emergency_hotline: str
    has_24hr_emergency: bool
    icu_available: bool
    key_specialties: str


class LegalCaseMatch(TypedDict, total=False):
    case_type: str
    case_category: str
    medical_evidence_required: str
    police_report_needed: bool
    urgent_examination: bool
    procedure_time_minutes: int
    evidence_preservation: str


class ForensicSpecialistMatch(TypedDict, total=False):
    doctor_name: str
    mcr_number: str
    forensic_focus: str
    expert_witness: bool
    available_24hr: bool
    consultation_fee_sgd: float
    contact_phone: str


class AuthoritiesInfo(TypedDict, total=False):
    police_contact: str
    hospital_contact: str
    emergency_number: str
    special_requirements: str
    turnaround_time: str


class CoordinationPhase(TypedDict, total=False):
    action: str
    reason: str
    location: str
    phone: str
    contact: str
    note: str


class CoordinationPlan(TypedDict, total=False):
    phase_1: CoordinationPhase
    phase_2: CoordinationPhase
    phase_3: CoordinationPhase
    key_coordination: list[str]


class ChasClinicMatch(TypedDict, total=False):
    clinic_id: str
    clinic_name: str
    division: str
    address: str
    phone: str
    operating_hours: str


class AgentState(TypedDict, total=False):
    # Inputs (set at graph invocation, immutable)
    user_message: str
    session_id: str

    # Agent 1 — InputRouter output
    pathway: str  # MEDICAL | LEGAL | DUAL | OCCUPATIONAL
    urgency_level: str  # CRITICAL | HIGH | MEDIUM
    medical_keywords: list[str]
    legal_keywords: list[str]

    # Agent 2 — KnowledgeMatcher output
    conditions: list[ConditionMatch]
    doctors: list[DoctorMatch]
    hospitals: list[HospitalMatch]
    legal_cases: list[LegalCaseMatch]
    forensic_specialists: list[ForensicSpecialistMatch]
    authorities: Optional[AuthoritiesInfo]
    chas_clinics: list[ChasClinicMatch]

    # Agent 3 — Coordinator output (DUAL cases only)
    coordination_plan: Optional[CoordinationPlan]

    # Agent 4 — ResponseFormatter output
    formatted_response: str

    # Error state
    error: Optional[str]
