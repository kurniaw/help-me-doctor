import asyncio
import logging
import re
from typing import Any

from app.agents.state import (
    AgentState,
    AuthoritiesInfo,
    ChasClinicMatch,
    ConditionMatch,
    DoctorMatch,
    ForensicSpecialistMatch,
    HospitalMatch,
    LegalCaseMatch,
)
from app.db.mongo import get_database
from app.rag.vertex_search import semantic_search_conditions

logger = logging.getLogger(__name__)


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("yes", "true", "1", "y")
    return bool(value)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


async def _search_medical_conditions(
    keywords: list[str],
    vertex_ids: list[str],
) -> list[ConditionMatch]:
    """Search medical_conditions collection."""
    db = get_database()
    collection = db["medical_conditions"]

    results: list[ConditionMatch] = []

    # First try Vertex AI semantic results
    if vertex_ids:
        try:
            docs = await collection.find(
                {"_vertex_id": {"$in": vertex_ids}}
            ).limit(5).to_list(5)
            for doc in docs:
                results.append(
                    ConditionMatch(
                        condition=doc.get("Condition", ""),
                        icd10_code=doc.get("ICD10_Code", ""),
                        specialty=doc.get("Recommended_Specialty", ""),
                        sub_specialty=doc.get("Sub_Specialty", ""),
                        urgency=doc.get("Urgency_Level", "MEDIUM"),
                        triage_color=doc.get("Triage_Color", "GREEN"),
                        chas_coverage=doc.get("CHAS_Coverage", "No"),
                        hospital_type=doc.get("Hospital_Type", ""),
                        vertex_id=doc.get("_vertex_id", ""),
                    )
                )
        except Exception as e:
            logger.warning("Vertex ID lookup failed: %s", e)

    # Fallback: keyword text search
    if not results and keywords:
        try:
            keyword_pattern = "|".join(re.escape(kw) for kw in keywords)
            docs = await collection.find(
                {"Symptoms": {"$regex": keyword_pattern, "$options": "i"}}
            ).limit(5).to_list(5)
            for doc in docs:
                results.append(
                    ConditionMatch(
                        condition=doc.get("Condition", ""),
                        icd10_code=doc.get("ICD10_Code", ""),
                        specialty=doc.get("Recommended_Specialty", ""),
                        sub_specialty=doc.get("Sub_Specialty", ""),
                        urgency=doc.get("Urgency_Level", "MEDIUM"),
                        triage_color=doc.get("Triage_Color", "GREEN"),
                        chas_coverage=doc.get("CHAS_Coverage", "No"),
                        hospital_type=doc.get("Hospital_Type", ""),
                    )
                )
        except Exception as e:
            logger.warning("Condition keyword search failed: %s", e)

    return results


async def _search_doctors(specialty: str, urgency: str) -> list[DoctorMatch]:
    """Search doctors by specialty, prioritise 24hr for CRITICAL."""
    db = get_database()
    collection = db["doctors"]

    query: dict[str, Any] = {
        "Specialty": {"$regex": specialty, "$options": "i"},
        "Registration_Status": "Active",
    }
    if urgency == "CRITICAL":
        query["On_Call_24Hr"] = True

    try:
        docs = await collection.find(query).sort(
            [("On_Call_24Hr", -1), ("Years_In_Practice", -1)]
        ).limit(3).to_list(3)

        results: list[DoctorMatch] = []
        for doc in docs:
            results.append(
                DoctorMatch(
                    mcr_number=doc.get("MCR_Number", ""),
                    doctor_name=doc.get("Doctor_Name", ""),
                    specialty=doc.get("Specialty", ""),
                    institution_name=doc.get("Institution_Name", ""),
                    contact_phone=doc.get("Contact_Phone", ""),
                    on_call_24hr=_safe_bool(doc.get("On_Call_24Hr")),
                    chas_accredited=_safe_bool(doc.get("CHAS_Accredited")),
                    years_in_practice=_safe_int(doc.get("Years_In_Practice")),
                )
            )
        return results
    except Exception as e:
        logger.warning("Doctor search failed: %s", e)
        return []


async def _search_hospitals(specialty: str) -> list[HospitalMatch]:
    """Search hospitals with the given specialty department."""
    db = get_database()
    collection = db["hospitals"]

    try:
        docs = await collection.find(
            {
                "$or": [
                    {"Departments": {"$regex": specialty, "$options": "i"}},
                    {"Key_Specialties": {"$regex": specialty, "$options": "i"}},
                ]
            }
        ).sort([("24Hr_Emergency", -1)]).limit(3).to_list(3)

        results: list[HospitalMatch] = []
        for doc in docs:
            results.append(
                HospitalMatch(
                    hospital_id=doc.get("Hospital_ID", ""),
                    hospital_name=doc.get("Hospital_Name", ""),
                    hospital_type=doc.get("Hospital_Type", ""),
                    address=doc.get("Address", ""),
                    phone_main=doc.get("Phone_Main", ""),
                    emergency_hotline=doc.get("Emergency_Hotline", ""),
                    has_24hr_emergency=_safe_bool(doc.get("24Hr_Emergency")),
                    icu_available=_safe_bool(doc.get("ICU_Available")),
                    key_specialties=doc.get("Key_Specialties", ""),
                )
            )
        return results
    except Exception as e:
        logger.warning("Hospital search failed: %s", e)
        return []


async def _search_legal_cases(keywords: list[str]) -> list[LegalCaseMatch]:
    """Search legal cases by keyword."""
    db = get_database()
    collection = db["legal_cases"]

    try:
        keyword_pattern = "|".join(re.escape(kw) for kw in keywords)
        docs = await collection.find(
            {"Case_Type": {"$regex": keyword_pattern, "$options": "i"}}
        ).limit(3).to_list(3)

        results: list[LegalCaseMatch] = []
        for doc in docs:
            results.append(
                LegalCaseMatch(
                    case_type=doc.get("Case_Type", ""),
                    case_category=doc.get("Case_Category", ""),
                    medical_evidence_required=doc.get("Medical_Evidence_Required", ""),
                    police_report_needed=_safe_bool(doc.get("Police_Report_Needed")),
                    urgent_examination=_safe_bool(doc.get("Urgent_Examination")),
                    procedure_time_minutes=_safe_int(doc.get("Procedure_Time_Minutes")),
                    evidence_preservation=doc.get("Evidence_Preservation", ""),
                )
            )
        return results
    except Exception as e:
        logger.warning("Legal case search failed: %s", e)
        return []


async def _search_forensic_specialists(case_type: str) -> list[ForensicSpecialistMatch]:
    """Search forensic specialists for a given case type."""
    db = get_database()
    collection = db["forensic_specialists"]

    try:
        docs = await collection.find(
            {
                "Forensic_Focus": {"$regex": case_type, "$options": "i"},
                "Expert_Witness": True,
            }
        ).sort([("Available_24Hr", -1)]).limit(2).to_list(2)

        # Fallback: relax filter
        if not docs:
            docs = await collection.find(
                {"Expert_Witness": True}
            ).limit(2).to_list(2)

        results: list[ForensicSpecialistMatch] = []
        for doc in docs:
            results.append(
                ForensicSpecialistMatch(
                    doctor_name=doc.get("Doctor_Name", ""),
                    mcr_number=doc.get("MCR_Number", ""),
                    forensic_focus=doc.get("Forensic_Focus", ""),
                    expert_witness=_safe_bool(doc.get("Expert_Witness")),
                    available_24hr=_safe_bool(doc.get("Available_24Hr")),
                    consultation_fee_sgd=_safe_float(doc.get("Consultation_Fee_SGD")),
                    contact_phone=doc.get("Contact_Phone", ""),
                )
            )
        return results
    except Exception as e:
        logger.warning("Forensic specialist search failed: %s", e)
        return []


async def _search_authorities(case_type: str) -> AuthoritiesInfo | None:
    """Search legal master for contact authorities."""
    db = get_database()
    collection = db["legal_master"]

    try:
        doc = await collection.find_one(
            {"Case_Type": {"$regex": case_type, "$options": "i"}}
        )
        if doc:
            return AuthoritiesInfo(
                police_contact=doc.get("Police_Contact", "999"),
                hospital_contact=doc.get("Hospital_Contact", ""),
                emergency_number=doc.get("Emergency_Number", "999"),
                special_requirements=doc.get("Special_Requirements", ""),
                turnaround_time=doc.get("Turnaround_Time", ""),
            )
    except Exception as e:
        logger.warning("Authorities search failed: %s", e)

    return AuthoritiesInfo(
        police_contact="999",
        hospital_contact="",
        emergency_number="999",
        special_requirements="",
        turnaround_time="",
    )


async def _search_chas_clinics() -> list[ChasClinicMatch]:
    """Return nearby CHAS clinics (for MEDIUM urgency)."""
    db = get_database()
    collection = db["chas_clinics"]

    try:
        docs = await collection.find({}).limit(3).to_list(3)
        results: list[ChasClinicMatch] = []
        for doc in docs:
            results.append(
                ChasClinicMatch(
                    clinic_id=doc.get("Clinic_ID", ""),
                    clinic_name=doc.get("Clinic_Name", ""),
                    division=doc.get("Division", ""),
                    address=doc.get("Address", ""),
                    phone=doc.get("Phone", ""),
                    operating_hours=doc.get("Operating_Hours", ""),
                )
            )
        return results
    except Exception as e:
        logger.warning("CHAS clinic search failed: %s", e)
        return []


async def knowledge_matcher_node(state: AgentState) -> AgentState:
    """Agent 2: Query all relevant databases in parallel."""
    pathway = state.get("pathway", "MEDICAL")
    urgency = state.get("urgency_level", "MEDIUM")
    medical_keywords = state.get("medical_keywords", [])
    legal_keywords = state.get("legal_keywords", [])

    is_medical = pathway in ("MEDICAL", "DUAL", "OCCUPATIONAL")
    is_legal = pathway in ("LEGAL", "DUAL", "OCCUPATIONAL")

    # Build parallel tasks
    tasks: dict[str, Any] = {}

    if is_medical:
        query_text = " ".join(medical_keywords) or state.get("user_message", "")
        try:
            vertex_ids = await semantic_search_conditions(query_text)
        except Exception as e:
            logger.warning("Semantic search raised unexpectedly: %s", e)
            vertex_ids = []
        tasks["conditions"] = _search_medical_conditions(medical_keywords, vertex_ids)

    if is_legal:
        tasks["legal_cases"] = _search_legal_cases(legal_keywords)

    if urgency == "MEDIUM":
        tasks["chas_clinics"] = _search_chas_clinics()

    # Execute all DB queries in parallel
    task_keys = list(tasks.keys())
    task_results = await asyncio.gather(*[tasks[k] for k in task_keys], return_exceptions=True)
    results: dict[str, Any] = {}
    for key, result in zip(task_keys, task_results, strict=False):
        if isinstance(result, Exception):
            logger.error("Task %s failed: %s", key, result)
            results[key] = []
        else:
            results[key] = result

    # Dependent queries (need specialty from conditions)
    conditions: list[ConditionMatch] = results.get("conditions", [])
    doctors: list[DoctorMatch] = []
    hospitals: list[HospitalMatch] = []

    if is_medical and conditions:
        specialty = conditions[0].get("specialty", "General Practice")
        doctors, hospitals = await asyncio.gather(
            _search_doctors(specialty, urgency),
            _search_hospitals(specialty),
        )

    # Legal dependent queries
    legal_cases: list[LegalCaseMatch] = results.get("legal_cases", [])
    forensic_specialists: list[ForensicSpecialistMatch] = []
    authorities: AuthoritiesInfo | None = None

    if is_legal and legal_cases:
        case_type = legal_cases[0].get("case_type", "assault")
        forensic_specialists, authorities = await asyncio.gather(
            _search_forensic_specialists(case_type),
            _search_authorities(case_type),
        )
    elif is_legal:
        authorities = await _search_authorities(" ".join(legal_keywords))

    return AgentState(
        **state,
        conditions=conditions,
        doctors=doctors,
        hospitals=hospitals,
        legal_cases=legal_cases,
        forensic_specialists=forensic_specialists,
        authorities=authorities,
        chas_clinics=results.get("chas_clinics", []),
    )
