# Multi-Agent RAG System
## 3-4 Agents for Deployment

---

## 🎯 ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────┐
│        SIMPLIFIED MULTI-AGENT RAG SYSTEM (3-4 Agents)        │
└──────────────────────────────────────────────────────────────┘

                         USER INPUT
                             ↓
                 ┌───────────────────────┐
                 │  AGENT 1: INPUT &     │
                 │  ROUTER AGENT         │
                 │ (Parse + Classify)    │
                 └───────────────────────┘
                             ↓
                 ┌───────────────────────┐
                 │  AGENT 2: KNOWLEDGE   │
                 │  MATCHER AGENT        │
                 │ (Database Search)     │
                 └───────────────────────┘
                             ↓
              ┌──────────────────────────────┐
              │ (OPTIONAL) AGENT 3:          │
              │ COORDINATOR AGENT            │
              │ (For dual medical+legal)     │
              └──────────────────────────────┘
                             ↓
                 ┌───────────────────────┐
                 │  FINAL AGENT:         │
                 │  RESPONSE FORMATTER   │
                 │ (Output & Contacts)   │
                 └───────────────────────┘
                             ↓
                        USER OUTPUT
```

---

## 🤖 AGENT 1: INPUT & ROUTER AGENT

**Purpose:** Single entry point for parsing & routing

**Responsibilities:**
1. Parse user input (extract keywords, entities, context)
2. Detect urgency signals
3. Classify pathway: MEDICAL / LEGAL / DUAL
4. Prepare search queries

**Input:** Raw user text
**Output:** Structured data with routing decision

**Logic:**
```python
class InputRouterAgent:
    
    def process(self, user_input):
        # Step 1: Extract keywords and entities
        keywords = extract_keywords(user_input)
        urgency = detect_urgency(keywords)
        
        # Step 2: Classify pathway
        medical_indicators = detect_medical(keywords)
        legal_indicators = detect_legal(keywords)
        
        if legal_indicators and 'assault' in keywords:
            pathway = 'LEGAL'
        elif legal_indicators and 'workplace' in keywords:
            pathway = 'OCCUPATIONAL'
        elif legal_indicators:
            pathway = 'LEGAL'
        else:
            pathway = 'MEDICAL'
        
        # Step 3: Check for dual pathway
        if medical_indicators and legal_indicators:
            pathway = 'DUAL'
        
        # Step 4: Prepare search queries
        search_queries = {
            'medical_search': keywords if pathway in ['MEDICAL', 'DUAL'] else None,
            'legal_search': keywords if pathway in ['LEGAL', 'OCCUPATIONAL', 'DUAL'] else None,
            'urgency': urgency,
            'pathway': pathway
        }
        
        return search_queries

    def detect_urgency(self, keywords):
        critical = ['chest pain', 'stroke', 'bleeding', 'unconscious', 'can\'t breathe']
        high = ['severe', 'emergency', 'pain', 'injury', 'trauma']
        
        if any(c in keywords for c in critical):
            return 'CRITICAL'
        elif any(h in keywords for h in high):
            return 'HIGH'
        return 'MEDIUM'
    
    def detect_legal(self, keywords):
        legal_words = ['assault', 'rape', 'abuse', 'punch', 'stab', 'police', 
                       'accident', 'workplace', 'injury', 'crime']
        return any(word in keywords for word in legal_words)
    
    def detect_medical(self, keywords):
        medical_words = ['pain', 'fever', 'cough', 'symptom', 'condition', 
                        'disease', 'injury', 'bleeding', 'headache']
        return any(word in keywords for word in medical_words)
```

---

## 🔍 AGENT 2: KNOWLEDGE MATCHER AGENT

**Purpose:** Single unified database search agent

**Responsibilities:**
1. Search medical conditions (if MEDICAL pathway)
2. Search legal cases (if LEGAL pathway)
3. Find matching doctors/hospitals
4. Find matching forensic specialists
5. Return consolidated results

**Input:** Search queries from Agent 1
**Output:** All matches from all databases in single response

**Logic:**
```python
class KnowledgeMatcherAgent:
    
    def search(self, search_queries):
        results = {}
        
        # MEDICAL SEARCH
        if search_queries['medical_search']:
            results['conditions'] = self.search_conditions(
                search_queries['medical_search'],
                search_queries['urgency']
            )
            
            if results['conditions']:
                results['doctors'] = self.search_doctors(
                    results['conditions']['specialty'],
                    search_queries['urgency']
                )
                results['hospitals'] = self.search_hospitals(
                    results['conditions']['specialty']
                )
        
        # LEGAL SEARCH
        if search_queries['legal_search']:
            results['case_type'] = self.search_cases(
                search_queries['legal_search']
            )
            
            if results['case_type']:
                results['forensic_specialists'] = self.search_forensic(
                    results['case_type']['case_type']
                )
                results['authorities'] = self.search_authorities(
                    results['case_type']['case_type']
                )
        
        return results
    
    def search_conditions(self, keywords, urgency):
        # Query: medical_condition_knowledge_base.csv
        matches = []
        for condition in medical_conditions:
            if any(kw in condition['symptoms'] for kw in keywords):
                score = calculate_match_score(keywords, condition)
                matches.append((condition, score))
        
        # Return top match
        if matches:
            best = max(matches, key=lambda x: x[1])
            return {
                'condition': best[0]['condition'],
                'specialty': best[0]['specialty'],
                'urgency': best[0]['urgency'],
                'triage': best[0]['triage_color'],
                'chas_eligible': best[0]['chas_coverage']
            }
    
    def search_doctors(self, specialty, urgency):
        # Query: singapore_doctors_database.csv
        doctors = []
        for doctor in doctor_database:
            if doctor['specialty'] == specialty and doctor['registration_status'] == 'Active':
                if urgency == 'CRITICAL' and not doctor['on_call_24hr']:
                    continue
                doctors.append(doctor)
        
        # Return top 2-3
        return sorted(doctors, 
                     key=lambda x: (-x['years_in_practice'], x['on_call_24hr']),
                     limit=3)
    
    def search_hospitals(self, specialty):
        # Query: singapore_hospitals_database.csv
        hospitals = []
        for hospital in hospital_database:
            if specialty in hospital['departments']:
                hospitals.append(hospital)
        
        # Return top 3 by emergency capability
        return sorted(hospitals,
                     key=lambda x: x['24hr_emergency'],
                     limit=3)
    
    def search_cases(self, keywords):
        # Query: legal_medicine_knowledge_base.csv
        matches = []
        for case in legal_cases:
            if any(kw in case['case_type'].lower() for kw in keywords):
                matches.append(case)
        
        # Return best match
        if matches:
            return {
                'case_type': matches[0]['case_type'],
                'evidence_required': matches[0]['medical_evidence_required'],
                'police_needed': matches[0]['police_report_needed'],
                'turnaround': matches[0]['procedure_time_minutes']
            }
    
    def search_forensic(self, case_type):
        # Query: legal_medicine_specialists_directory.csv
        specialists = []
        for specialist in forensic_database:
            if case_type.lower() in specialist['forensic_focus'].lower():
                if specialist['court_experience'] and specialist['expert_witness']:
                    specialists.append(specialist)
        
        return specialists[:2]  # Top 2
    
    def search_authorities(self, case_type):
        # Query: master_legal_medicine_knowledge_base.csv
        for case in legal_master:
            if case['case_type'] == case_type:
                return {
                    'police_contact': case['police_contact'],
                    'hospital_contact': case['hospital_contact'],
                    'emergency_number': case['emergency_number'],
                    'special_requirements': case['special_requirements']
                }
```

**Databases Used:**
- medical_condition_knowledge_base.csv
- singapore_doctors_database.csv
- singapore_hospitals_database.csv
- legal_medicine_knowledge_base.csv
- legal_medicine_specialists_directory.csv
- master_legal_medicine_knowledge_base.csv

---

## 🔀 AGENT 3: COORDINATOR AGENT (OPTIONAL - For Dual Cases Only)

**Purpose:** Handle complex dual pathway cases (medical + legal)

**Responsibilities:**
1. Coordinate medical & legal results
2. Resolve conflicts/overlaps
3. Determine sequence of actions
4. Flag special requirements

**Input:** Results from Agent 2 (if pathway = DUAL)
**Output:** Coordinated action plan

**Logic:**
```python
class CoordinatorAgent:
    
    def coordinate(self, medical_results, legal_results, urgency):
        # Only invoked if pathway = DUAL
        
        plan = {
            'phase_1': self.get_emergency_phase(urgency),
            'phase_2': self.get_hospital_phase(medical_results),
            'phase_3': self.get_legal_phase(legal_results),
            'key_coordination': self.get_coordination_points(
                medical_results, legal_results
            )
        }
        
        return plan
    
    def get_emergency_phase(self, urgency):
        if urgency == 'CRITICAL':
            return {
                'action': 'Call 999',
                'reason': 'CRITICAL medical + criminal case',
                'preserve_evidence': True
            }
    
    def get_hospital_phase(self, medical_results):
        doctor = medical_results['doctors'][0]
        hospital = medical_results['hospitals'][0]
        
        return {
            'location': hospital['name'],
            'phone': hospital['phone'],
            'request': f"Ask for {doctor['doctor_name']} ({doctor['mcr']})",
            'note': 'Inform hospital of legal case - evidence preservation'
        }
    
    def get_legal_phase(self, legal_results):
        specialist = legal_results['forensic_specialists'][0]
        authorities = legal_results['authorities']
        
        return {
            'forensic_specialist': specialist['doctor_name'],
            'police_contact': authorities['police_contact'],
            'coordination': 'Police will coordinate with hospital'
        }
    
    def get_coordination_points(self, medical_results, legal_results):
        # Evidence collection happens during medical exam
        return [
            'Photographs taken during medical assessment',
            'Evidence kit (PASE/DNA) collected by hospital',
            'Police present for evidence chain',
            'Medical report becomes legal evidence'
        ]
```

---

## 📤 FINAL AGENT: RESPONSE FORMATTER

**Purpose:** Format all results into user-friendly output

**Responsibilities:**
1. Prioritize information based on urgency
2. Format for readability
3. Include emergency numbers prominently
4. Structure by action phases

**Input:** Results from Agent 2 or Agent 3
**Output:** User-facing recommendations

**Logic:**
```python
class ResponseFormatterAgent:
    
    def format_response(self, pathway, results, urgency):
        
        if pathway == 'MEDICAL':
            return self.format_medical(results, urgency)
        elif pathway == 'LEGAL':
            return self.format_legal(results)
        else:  # DUAL
            return self.format_dual(results, urgency)
    
    def format_medical(self, results, urgency):
        condition = results['conditions']
        doctors = results['doctors']
        hospitals = results['hospitals']
        
        if urgency == 'CRITICAL':
            output = f"""
🚨 MEDICAL EMERGENCY
Call 999 immediately

CONDITION: {condition['condition']}
Specialty needed: {condition['specialty']}

NEAREST HOSPITAL:
{hospitals[0]['name']}
Phone: {hospitals[0]['phone']}
Address: {hospitals[0]['address']}

SPECIALISTS:
{', '.join([f"{d['doctor_name']} ({d['mcr']})" for d in doctors])}
Phone: {doctors[0]['phone']}

WHAT TO DO:
1. Call 999
2. Describe symptoms: {condition['symptoms'][:50]}...
3. Go to nearest hospital
4. Request specialist
            """
        else:
            output = f"""
URGENT MEDICAL APPOINTMENT NEEDED

Possible condition: {condition['condition']}
Recommended specialist: {condition['specialty']}

HOSPITALS WITH THIS SPECIALTY:
{self.format_hospital_list(hospitals)}

AVAILABLE DOCTORS:
{self.format_doctor_list(doctors)}

RECOMMENDED NEXT STEPS:
1. Call {doctors[0]['phone']}
2. Request {doctors[0]['doctor_name']}
3. Book urgent appointment
4. Expected wait: {self.get_wait_time(condition['urgency'])}
            """
        
        return output
    
    def format_legal(self, results):
        case = results['case_type']
        specialists = results['forensic_specialists']
        authorities = results['authorities']
        
        output = f"""
⚖️ LEGAL CASE: {case['case_type']}

IMMEDIATE ACTIONS:
{self.format_critical_actions(case)}

AUTHORITIES TO CONTACT:
Police: {authorities['police_contact']}
Emergency: {authorities['emergency_number']}

FORENSIC SPECIALISTS:
{self.format_specialist_list(specialists)}

EVIDENCE REQUIREMENTS:
{', '.join(case['evidence_required'].split(',')[:3])}...

EXPECTED TURNAROUND: {case['turnaround']} minutes
        """
        
        return output
    
    def format_dual(self, results, urgency):
        medical = results['conditions']
        legal = results['case_type']
        doctors = results['doctors']
        authorities = results['authorities']
        
        output = f"""
🚨 EMERGENCY: Medical + Legal Case
{legal['case_type']} causing {medical['condition']}

IMMEDIATE (Call 999):
1. Report: {legal['case_type']}
2. Need: Medical emergency + Police
3. Location: Will go to {results['hospitals'][0]['name']}

HOSPITAL:
{results['hospitals'][0]['name']}
Phone: {results['hospitals'][0]['phone']}
Request: {doctors[0]['doctor_name']} (trained in {legal['case_type']})

KEY COORDINATION:
- Police coordinates with hospital
- Medical exam = Evidence collection
- Hospital files incident report
- Medical report becomes legal evidence

SUPPORT SERVICES:
Crisis hotline: 1800-221-4444
Legal aid: Available after medical care
        """
        
        return output
```

---

## 📊 COMPLETE WORKFLOW (3-4 Agents)

### Example: "My son have been abused and assaulted, need emergency medical care"

```
USER INPUT
    ↓
[AGENT 1: INPUT & ROUTER]
  ├─ Parse: keywords=[abuse, assault, trauma]
  ├─ Detect urgency: CRITICAL
  ├─ Detect legal indicators: YES (abuse, assault)
  ├─ Detect medical indicators: YES (trauma)
  └─ Output: {pathway: DUAL, urgency: CRITICAL, 
              medical_search: [trauma],
              legal_search: [abuse, assault]}
    ↓
[AGENT 2: KNOWLEDGE MATCHER]
  ├─ Medical search:
  │  ├─ Match: Assult trauma + abuse injury
  │  ├─ Specialty: Forensic examiners + Emergency Medicine
  │  ├─ Find: Dr Olivia Ng (KK Hospital)
  │  └─ Hospital: KK Women's and Children's Hospital
  │
  └─ Legal search:
     ├─ Match: Abuse assault case
     ├─ Find: Dr Olivia Ng (also forensic trained!)
     └─ Authorities: Police (999), Specialist Centre (6258-4333)
    ↓
[AGENT 3: COORDINATOR] (OPTIONAL, for DUAL)
  ├─ Phase 1: Call 999 (emergency + legal)
  ├─ Phase 2: Hospital coordination (medical exam = evidence)
  ├─ Phase 3: Police + victim support
  └─ Key point: Evidence collected during medical examination
    ↓
[RESPONSE FORMATTER]
  └─ Output: Emergency checklist + legal guidance + hotlines
    ↓
USER OUTPUT
    🚨 CALL 999 IMMEDIATELY
       Go to KK Women's Hospital
       Ask for Dr Olivia Ng
       Do NOT bathe/shower
       Preserve evidence
       Legal support: 1800-221-4444
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Agent 1: Input & Router
- [x] Parse keywords from user input
- [x] Detect urgency signals (CRITICAL/HIGH/MEDIUM)
- [x] Classify pathway (MEDICAL/LEGAL/DUAL)
- [x] Prepare search queries for Agent 2

### Agent 2: Knowledge Matcher
- [x] Search medical_condition_knowledge_base.csv
- [x] Search singapore_doctors_database.csv
- [x] Search singapore_hospitals_database.csv
- [x] Search legal_medicine_knowledge_base.csv
- [x] Search legal_medicine_specialists_directory.csv
- [x] Return consolidated results

### Agent 3: Coordinator (Optional)
- [x] Coordinate medical + legal results (DUAL cases only)
- [x] Determine action sequence
- [x] Flag evidence preservation needs

### Response Formatter
- [x] Format for MEDICAL cases
- [x] Format for LEGAL cases
- [x] Format for DUAL cases
- [x] Highlight emergency numbers

---

## 🚀 EXAMPLE QUERIES & AGENT FLOW

### Query 1: "Chest pain and breathing difficulty"

```
Input & Router → MEDICAL pathway, CRITICAL urgency
    ↓
Knowledge Matcher → Condition: Acute Chest Pain
                    Specialty: Cardiology
                    Doctor: Dr Tan Wei Ming (National Heart Centre)
    ↓
Response Formatter → "Call 999 → Go to National Heart Centre"
                      Phone: 67222928
Cost: 2 API calls
```

### Query 2: "I fell from stairs and my back hurts"

```
Input & Router → MEDICAL pathway, HIGH urgency
                 Could also be OCCUPATIONAL
    ↓
Knowledge Matcher → Condition: Herniated Disc / Back Injury
                    Specialty: Orthopaedic Surgery / Neurosurgery
                    Doctor: Dr Jian Hao Loh (SGH)
                    Case: Workplace injury (may need MOM reporting)
    ↓
Coordinator (Optional) → If workplace: Note MOM reporting after medical care
    ↓
Response Formatter → "Go to SGH Emergency"
                      "Request Dr Jian Hao Loh"
                      "Report to MOM within 24 hours"
Cost: 2-3 API calls
```

### Query 3: "I was punched in the face"

```
Input & Router → DUAL pathway (medical + legal), CRITICAL urgency
    ↓
Knowledge Matcher → Medical: Facial trauma + eye injury
                             Specialist: Emergency Medicine + Trauma
                    Legal: Assault case
                           Evidence: Photographs, injury documentation
                           Authorities: Police (999)
    ↓
Coordinator → Phase 1: Call 999 (emergency + police)
              Phase 2: Hospital (medical exam = evidence photos)
              Phase 3: Police statement with support
    ↓
Response Formatter → "CALL 999 IMMEDIATELY"
                      "Go to SGH Emergency"
                      "Request trauma team"
                      "Police will coordinate"
                      "Legal rights protected"
Cost: 3 API calls
```

---

## 🔧 CODE STRUCTURE

```python
class SimplifiedRAGSystem:
    
    def __init__(self):
        self.agent_1 = InputRouterAgent()
        self.agent_2 = KnowledgeMatcherAgent()
        self.agent_3 = CoordinatorAgent()
        self.formatter = ResponseFormatterAgent()
    
    def process(self, user_input):
        # Step 1: Parse & Route
        search_queries = self.agent_1.process(user_input)
        pathway = search_queries['pathway']
        urgency = search_queries['urgency']
        
        # Step 2: Search all databases
        results = self.agent_2.search(search_queries)
        
        # Step 3: Coordinate (if DUAL)
        if pathway == 'DUAL':
            results['coordination'] = self.agent_3.coordinate(
                results.get('conditions'),
                results.get('case_type'),
                urgency
            )
        
        # Step 4: Format output
        output = self.formatter.format_response(
            pathway, results, urgency
        )
        
        return output

# Usage
rag = SimplifiedRAGSystem()
output = rag.process("I have chest pain")
print(output)
```

---

## 📊 AGENT RESPONSIBILITIES MATRIX

```
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│ Responsibility      │ Agent 1      │ Agent 2      │ Agent 3      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Parse input         │ ✓            │              │              │
│ Detect urgency      │ ✓            │              │              │
│ Route pathway       │ ✓            │              │              │
│ Search databases    │              │ ✓            │              │
│ Match conditions    │              │ ✓            │              │
│ Find doctors        │              │ ✓            │              │
│ Find hospitals      │              │ ✓            │              │
│ Coordinate dual     │              │              │ ✓            │
│ Resolve conflicts   │              │              │ ✓            │
│ Format output       │              │              │ Response     │
│                     │              │              │ Formatter    │
└─────────────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 💾 DATA FLOW

```
medical_condition_knowledge_base.csv  ─┐
singapore_doctors_database.csv        ─┤
singapore_hospitals_database.csv      ─┤
legal_medicine_knowledge_base.csv     ─┤
legal_medicine_specialists_directory  ─┤─→ [AGENT 2: KNOWLEDGE MATCHER] ─┐
master_legal_medicine_knowledge_base  ─┘                                 ├─→ [AGENT 3]─┐
                                                                          │             │
[USER INPUT] ──→ [AGENT 1: INPUT & ROUTER] ────────────────────────────┤             │
                                                                          ├─→ [RESPONSE FORMATTER] ──→ [OUTPUT]
                                                                          │
Templates (for formatting) ────────────────────────────────────────────┘
```

---

## ✨ BENEFITS OF THE APPROACH

✅ **Faster response** - Parallel database queries in single agent
✅ **Simpler maintenance** - Only 3-4 agents to manage
✅ **Easier debugging** - Fewer agent interactions
✅ **Works with free tier** - Optimized for limited API credits
✅ **Same accuracy** - All database lookups still comprehensive
✅ **Scalable** - Can add agents later if needed