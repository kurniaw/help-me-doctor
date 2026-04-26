# HelpMeDoctor — Implementation Plan

## Overview

A Singapore medical/legal triage RAG system using a 4-agent LangGraph pipeline. Users describe symptoms or incidents; agents route, search knowledge bases, coordinate responses, and stream recommendations for nearby clinics or specific hospital specialists.

---

## Architecture

```
User Query (Chat UI)
       │
       ▼
[FastAPI SSE Endpoint]
       │
       ▼
┌─────────────────────────────────────────────────────┐
│              LangGraph State Machine                  │
│                                                       │
│  ┌─────────────┐    ┌──────────────────┐             │
│  │  Agent 1    │───▶│    Agent 2        │             │
│  │ InputRouter │    │ KnowledgeMatcher  │             │
│  │ (Gemini LLM)│    │ (MongoDB +        │             │
│  │ pathway +   │    │  Vertex AI)       │             │
│  │ urgency     │    │ parallel queries  │             │
│  └─────────────┘    └──────────────────┘             │
│                             │                         │
│              ┌──────────────┴───────────┐             │
│              ▼ (DUAL only)              ▼             │
│     ┌──────────────────┐    ┌─────────────────────┐  │
│     │   Agent 3        │    │     Agent 4          │  │
│     │  Coordinator     │───▶│ ResponseFormatter    │  │
│     │  (deterministic) │    │ (Gemini streaming)   │  │
│     └──────────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────┘
       │
       ▼ (SSE stream)
[Nuxt.js Chat UI — streaming markdown]
```

### Pathways
| Pathway | Trigger | Agents Used |
|---|---|---|
| MEDICAL | Symptoms only | 1 → 2 → 4 |
| LEGAL | Crime/legal only | 1 → 2 → 4 |
| DUAL | Both medical + legal | 1 → 2 → 3 → 4 |
| OCCUPATIONAL | Workplace injury | 1 → 2 → 4 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Nuxt.js 3, Vue 3, TypeScript (strict), Pinia, PrimeVue 4 (Aura theme) |
| Frontend Testing | Vitest, @vue/test-utils, happy-dom |
| Backend | FastAPI 0.115+, Python 3.12, LangGraph 0.2+, Beanie ODM |
| AI/LLM | Gemini 1.5 Flash (router + formatter), textembedding-gecko@003 (768-dim) |
| Database | MongoDB (Motor async driver), Vertex AI Vector Search |
| Infrastructure | GCP: Cloud Run, Artifact Registry, Cloud Storage, Vertex AI, Secret Manager |
| IaC | Terraform 1.6+ |
| CI/CD | GitHub Actions with Workload Identity Federation |
| Dev | Docker Compose |

---

## Project Structure

```
help-me-doctor/
├── .github/workflows/
│   ├── ci.yml          # PR checks: lint, test, build verify
│   ├── deploy.yml      # Push to main: build → push → terraform → health check
│   └── seed.yml        # Manual: data ingestion (MongoDB + Vertex AI)
├── data/               # 8 CSV knowledge bases (read-only)
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory + lifespan
│   │   ├── config.py               # pydantic-settings BaseSettings
│   │   ├── dependencies.py         # JWT get_current_user dependency
│   │   ├── api/v1/
│   │   │   ├── auth.py             # POST /auth/register, /auth/login
│   │   │   └── chat.py             # POST /chat/stream (SSE)
│   │   ├── auth/                   # JWT + bcrypt utilities
│   │   ├── db/                     # Motor client + collection constants
│   │   ├── models/                 # Beanie ODM documents
│   │   ├── agents/
│   │   │   ├── state.py            # AgentState TypedDict
│   │   │   ├── graph.py            # LangGraph StateGraph
│   │   │   ├── input_router.py     # Agent 1
│   │   │   ├── knowledge_matcher.py # Agent 2
│   │   │   ├── coordinator.py      # Agent 3 (DUAL only)
│   │   │   └── response_formatter.py # Agent 4 (streaming)
│   │   ├── rag/
│   │   │   ├── vertex_search.py    # Vertex AI find_neighbors()
│   │   │   └── embedder.py         # textembedding-gecko@003
│   │   └── schemas/                # Pydantic request/response schemas
│   └── scripts/
│       ├── ingest_mongo.py         # CSV → MongoDB (run once)
│       └── ingest_vertex.py        # Embeddings → Vertex AI (run once)
├── frontend/
│   ├── types/                      # auth.ts, chat.ts TypeScript types
│   ├── stores/                     # Pinia: auth.ts, chat.ts
│   ├── components/
│   │   ├── auth/                   # RegisterForm.vue, LoginForm.vue
│   │   └── chat/                   # ChatWindow, MessageBubble, ChatInput, etc.
│   ├── pages/                      # index, register, login, chat
│   ├── layouts/                    # default.vue, auth.vue
│   ├── middleware/auth.ts
│   └── tests/                      # Vitest component + store tests
└── infrastructure/                 # Terraform modules
    └── modules/
        ├── artifact_registry/
        ├── cloud_run/
        ├── vertex_ai/
        └── storage/
```

---

## MongoDB Collections

| Collection | Source CSV | Documents | Purpose |
|---|---|---|---|
| `medical_conditions` | medical_condition_knowledge_base.csv | 645 | Symptom → specialty matching |
| `doctors` | singapore_doctors_database.csv | 67 | Doctor directory |
| `hospitals` | singapore_hospitals_database.csv | 50 | Hospital directory |
| `legal_cases` | legal_medicine_knowledge_base.csv | 62 | Legal case procedures |
| `forensic_specialists` | legal_medicine_specialists_directory.csv | 50 | Forensic doctors |
| `legal_master` | master_legal_medicine_knowledge_base.csv | 39 | Authorities + contacts |
| `medical_master` | master_medical_knowledge_base.csv | 82 | Master medical routing |
| `chas_clinics` | chas_clinics_singapore.csv | 56 | CHAS clinic locations |
| `users` | — | — | Auth (Beanie ODM) |
| `chat_sessions` | — | — | Chat history (Beanie ODM) |

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Health check |
| POST | `/api/v1/auth/register` | None | Create account → JWT |
| POST | `/api/v1/auth/login` | None | Authenticate → JWT |
| POST | `/api/v1/chat/stream` | Bearer JWT | SSE chat stream |

### SSE Event Format
```
data: {"type": "chunk", "content": "...", "urgency": "CRITICAL", "pathway": "DUAL"}\n\n
data: {"type": "done",  "content": "",    "urgency": "CRITICAL", "pathway": "DUAL"}\n\n
data: {"type": "error", "content": "...", "urgency": "MEDIUM",   "pathway": "MEDICAL"}\n\n
```

### Response Urgency Prefix
The formatter's first line is always: `URGENCY:{CRITICAL|HIGH|MEDIUM}`
The frontend strips this to display the urgency badge.

---

## Agent Descriptions

### Agent 1: InputRouter (`app/agents/input_router.py`)
- **Input:** `user_message` (raw text)
- **LLM:** `gemini-1.5-flash` with `with_structured_output(RouterOutput)`
- **Output:** `pathway`, `urgency_level`, `medical_keywords`, `legal_keywords`
- **Fallback:** Keyword heuristics if LLM fails

### Agent 2: KnowledgeMatcher (`app/agents/knowledge_matcher.py`)
- **No LLM** — pure database queries
- Runs `asyncio.gather()` for parallel queries:
  - MEDICAL: Vertex AI semantic search → conditions → doctors → hospitals
  - LEGAL: MongoDB text search → legal cases → forensic specialists → authorities
  - MEDIUM urgency: CHAS clinics lookup
- **Output:** `conditions`, `doctors`, `hospitals`, `legal_cases`, `forensic_specialists`, `authorities`, `chas_clinics`

### Agent 3: Coordinator (`app/agents/coordinator.py`)
- **Only invoked when `pathway == "DUAL"`**
- **No LLM** — deterministic sequencing logic
- Produces 3-phase action plan: emergency → hospital → police
- **Output:** `coordination_plan` with `phase_1`, `phase_2`, `phase_3`, `key_coordination[]`

### Agent 4: ResponseFormatter (`app/agents/response_formatter.py`)
- **LLM:** `gemini-1.5-flash` with streaming (`astream()`)
- Receives all state data → produces markdown response
- First line always: `URGENCY:{level}`
- Falls back to template if LLM unavailable
- **Output:** `formatted_response` (streamed via SSE)

---

## LangGraph State Flow

```python
class AgentState(TypedDict, total=False):
    # Inputs
    user_message: str
    session_id: str
    # Agent 1
    pathway: str         # MEDICAL | LEGAL | DUAL | OCCUPATIONAL
    urgency_level: str   # CRITICAL | HIGH | MEDIUM
    medical_keywords: list[str]
    legal_keywords: list[str]
    # Agent 2
    conditions: list[ConditionMatch]
    doctors: list[DoctorMatch]
    hospitals: list[HospitalMatch]
    legal_cases: list[LegalCaseMatch]
    forensic_specialists: list[ForensicSpecialistMatch]
    authorities: Optional[AuthoritiesInfo]
    chas_clinics: list[ChasClinicMatch]
    # Agent 3 (DUAL only)
    coordination_plan: Optional[CoordinationPlan]
    # Agent 4
    formatted_response: str
    # Error handling
    error: Optional[str]
```

---

## GCP Infrastructure (Terraform)

| Resource | SKU | Config | Est. Monthly Cost |
|---|---|---|---|
| Artifact Registry | Docker repo | `hmd-images`, asia-southeast1 | $0 (10GB free) |
| Cloud Run — backend | Container | 0–2 instances, 512MB, 1vCPU | $0 (2M req/mo free) |
| Cloud Run — frontend | Container | 0–2 instances, 256MB, 0.5vCPU | $0 |
| Cloud Storage | Standard | ~100MB data | $0 (5GB free) |
| Vertex AI Vector Search | Tree-AH | 645 vectors, 768-dim | ~$0–10 |
| Vertex AI Gemini Flash | LLM | ~100 req/day | $0 (free quota) |
| MongoDB Atlas M0 | Free tier | 512MB | $0 |
| Secret Manager | Secrets | 5 secrets | $0 |
| **Total** | | | **$0–$18/month** |

---

## CI/CD Pipelines

### `ci.yml` — on every PR
1. `lint-backend` — ruff + mypy
2. `lint-frontend` — ESLint
3. `test-backend` — pytest (with MongoDB service container)
4. `test-frontend` — Vitest
5. `build-verify` — docker build (no push)

### `deploy.yml` — on push to main
1. `build-and-push` — auth via Workload Identity Federation, push to Artifact Registry
2. `terraform-apply` — `terraform init` (GCS backend) → plan → apply
3. `health-check` — curl backend `/health` + frontend URL

### `seed.yml` — manual `workflow_dispatch`
- `seed-mongo` — CSV ingestion to MongoDB
- `seed-vertex` — embedding ingestion to Vertex AI (optional)

### GitHub Secrets Required
| Secret | Description |
|---|---|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload Identity pool provider resource name |
| `GCP_SERVICE_ACCOUNT` | Service account email for CI/CD |
| `GCP_PROJECT_ID` | GCP project ID |
| `MONGO_URI` | MongoDB Atlas connection string |
| `JWT_SECRET` | Strong random JWT signing secret |

### GitHub Variables
| Variable | Description |
|---|---|
| `BACKEND_URL` | Cloud Run backend URL (set after first deploy) |

---

## Implementation Sequence

Start from scratch, each step is independently testable:

1. `docker compose up` → verify all 3 services start
2. MongoDB + Beanie models → verify `helpmedoctor` database created
3. `python scripts/ingest_mongo.py --drop` → verify 8 collections, spot-check data
4. Auth endpoints → `curl -X POST /api/v1/auth/register`
5. Frontend auth pages → login flow in browser
6. LangGraph graph with mocked agents → verify SSE streaming works
7. Real Agent 2 MongoDB queries → replace mocks
8. `python scripts/ingest_vertex.py` → real semantic search in Agent 2
9. Agent 1 + 4 Gemini LLM → real routing and formatting
10. Frontend chat UI → full E2E: register → login → chat
11. Terraform → `terraform apply` for GCP resources
12. GitHub Actions → push to main → verify auto-deploy

---

## Test Scenarios

| Query | Expected Pathway | Expected Urgency |
|---|---|---|
| "I have chest pain and difficulty breathing" | MEDICAL | CRITICAL |
| "I was punched in the face" | DUAL | CRITICAL |
| "I have a mild headache" | MEDICAL | MEDIUM → CHAS clinic |
| "I fell at work and hurt my back" | OCCUPATIONAL | HIGH |
| "My child was abused" | DUAL | CRITICAL |
| "I need a routine checkup" | MEDICAL | MEDIUM → CHAS clinic |
