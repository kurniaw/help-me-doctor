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
2. Detect urgency signal: MEDIUM / HIGH / CRITICAL
3. Classify pathway: MEDICAL / LEGAL / DUAL
4. Prepare search queries

**Input:** Raw user text
**Output:** Structured data with routing decision

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