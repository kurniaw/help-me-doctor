# Help Me Doctor 🏥

> AI-powered Singapore medical and legal triage assistant. Describe your symptoms or situation — multi-agent AI routes your query and connects you with the right healthcare providers.

## Features

- **4-Agent LangGraph Pipeline** — Router → Matcher → Coordinator → Formatter
- **Dual-pathway triage** — handles medical, legal, occupational, and combined cases
- **Streaming chat** — real-time SSE streaming responses
- **Singapore-specific** — CHAS clinics, Singapore General Hospital, KKH, and 50+ hospitals
- **Urgency classification** — CRITICAL / HIGH / MEDIUM with colour-coded badges
- **JWT authentication** — secure registration and login

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker + Docker Compose | Latest | [docker.com](https://www.docker.com) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| Conda | Latest | [miniforge](https://github.com/conda-forge/miniforge) or [Anaconda](https://www.anaconda.com) |
| GCP Account | — | For Vertex AI + Cloud Run |
| MongoDB Atlas | Free tier | [mongodb.com/atlas](https://www.mongodb.com/atlas) |
| Terraform | 1.6+ | [terraform.io](https://www.terraform.io) |

---

## Quick Start (Local Development)

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd help-me-doctor

# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env — set at minimum:
#   JWT_SECRET=<any-random-string>
#   GCP_PROJECT_ID=<your-project-id>  (optional for local dev without Vertex AI)



# Frontend environment
cp frontend/.env.example frontend/.env

cd frontend
npm install
```

### 2. Start services with Docker Compose

```bash
docker compose up --build
```

This starts:
- **MongoDB** on port 27017
- **Backend** (FastAPI) on http://localhost:8000
- **Frontend** (Nuxt.js) on http://localhost:3000

Wait ~30 seconds for all services to be healthy.

### 3. Seed the knowledge bases

In a new terminal:

```bash
cd backend
conda env create -f environment.yml                                                                                                            
conda activate help-me-doctor
python scripts/ingest_mongo.py --data-dir ../data
```

Expected output: ~500 documents inserted across 8 collections.

### 4. Open the app

Navigate to http://localhost:3000, register an account, and start chatting.

**Example queries:**
- `"I have chest pain and difficulty breathing"`
- `"I was assaulted and need medical and legal help"`
- `"My child has a fever of 39°C for 2 days"`
- `"I fell at my workplace and hurt my back"`

---

## Vertex AI Setup (Optional — for semantic symptom search)

Without Vertex AI, symptom matching uses MongoDB keyword search (still functional).
With Vertex AI, semantic similarity gives better results for complex symptom descriptions.

### Prerequisites
- GCP project with billing enabled
- `gcloud` CLI installed and authenticated

### Steps

```bash
# 1. Create GCS bucket (replace YOUR_PROJECT_ID)
gsutil mb -l asia gs://YOUR_PROJECT_ID-hmd-data

# 2. Run embedding ingestion (~15 min, 645 conditions)
cd backend
conda activate help-me-doctor
python scripts/ingest_vertex.py \
  --project YOUR_PROJECT_ID \
  --region asia-southeast1 \
  --bucket YOUR_PROJECT_ID-hmd-data \
  --data-dir ../data

# 3. The script outputs INDEX_ID and ENDPOINT_ID
# Add these to backend/.env:
#   VERTEX_INDEX_ID=...
#   VERTEX_INDEX_ENDPOINT_ID=...
```

> Note: Vertex AI index deployment takes ~30 minutes on first run.

---

## Development

### Backend (FastAPI)

```bash
cd backend
conda env create -f environment.yml   # first time only
conda activate help-me-doctor
cp .env.example .env  # configure your .env

# Run with hot reload
uvicorn app.main:app --reload --port 8000

# API docs
open http://localhost:8000/docs

# Run linting
ruff check .
mypy app/

# Run tests
pytest tests/ -v --asyncio-mode=auto
```

### Frontend (Nuxt.js)

```bash
cd frontend
npm install

# Run dev server
npm run dev

# Lint
npm run lint
npm run lint:fix

# Run tests
npm test
npm run test:watch

# Build for production
npm run build
```

---

## GCP Deployment

### Step 1: Create GCP project and enable billing

```bash
gcloud projects create YOUR_PROJECT_ID
gcloud config set project YOUR_PROJECT_ID
gcloud billing accounts list
gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID

```

### Step 2: Create Terraform state bucket (Optional)

```bash
# gsutil mb -l asia gs://YOUR_PROJECT_ID-tf-state
# gsutil versioning set on gs://YOUR_PROJECT_ID-tf-state
```

### Step 3: Create Secrets in Secret Manager

```bash
# MongoDB Atlas connection string
echo -n "mongodb+srv://user:pass@cluster.mongodb.net/" | \
  gcloud secrets create hmd-mongo-uri --data-file=-

# JWT signing secret
openssl rand -base64 32 | \
  gcloud secrets create hmd-jwt-secret --data-file=-
```

### Step 4: Configure Terraform

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars:
#   project_id = "YOUR_PROJECT_ID"
```

### Step 5: Grant Terraform service account permissions

The service account running Terraform needs project-level roles. Run as a project Owner:

```bash
PROJECT=YOUR_PROJECT_ID
SA="serviceAccount:YOUR_TERRAFORM_SA@YOUR_PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT --member=$SA --role="roles/editor"
gcloud projects add-iam-policy-binding $PROJECT --member=$SA --role="roles/iam.serviceAccountAdmin"
gcloud projects add-iam-policy-binding $PROJECT --member=$SA --role="roles/iam.serviceAccountUser"
gcloud projects add-iam-policy-binding $PROJECT --member=$SA --role="roles/resourcemanager.projectIamAdmin"
gcloud storage buckets add-iam-policy-binding gs://YOUR_PROJECT_ID-tf-state --member=$SA --role="roles/storage.objectAdmin"
```

### Step 6: Apply Terraform (initial — placeholder images)

Install Terraform CLI: [https://developer.hashicorp.com/terraform/install]
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

This first apply creates all infrastructure with a placeholder image so you can get the backend URL:

```bash
cd infrastructure

terraform init \
  -backend-config="bucket=YOUR_PROJECT_ID-tf-state" \
  -backend-config="prefix=hmd/terraform.tfstate"

terraform apply
```

Note the outputs — especially `backend_url`, `vertex_index_id` and `vertex_endpoint_id`.

### Step 7: Build and push Docker images

> **Important:** Always build with `--platform linux/amd64` — Cloud Run does not support ARM images (e.g. Apple Silicon builds).

```bash
# Authenticate Docker to Artifact Registry
gcloud auth configure-docker asia-southeast1-docker.pkg.dev

REGISTRY=asia-southeast1-docker.pkg.dev/YOUR_PROJECT_ID/hmd-images

# Build and push backend
docker build --platform linux/amd64 -t $REGISTRY/backend:latest ./backend
docker push $REGISTRY/backend:latest

# Build and push frontend (embeds the backend URL at build time)
BACKEND_URL=$(cd infrastructure && terraform output -raw backend_url)
docker build --platform linux/amd64 --build-arg NUXT_PUBLIC_API_BASE=$BACKEND_URL -t $REGISTRY/frontend:latest ./frontend
docker push $REGISTRY/frontend:latest
```

### Step 8: Deploy real images to Cloud Run

```bash
cd infrastructure
terraform apply \
  -var="backend_image=$REGISTRY/backend:latest" \
  -var="frontend_image=$REGISTRY/frontend:latest"

gcloud run deploy hmd-backend --image=$REGISTRY/backend:latest --region=asia-southeast1 --project=ntu-data-science-ai
gcloud run deploy hmd-frontend --image=$REGISTRY/frontend:latest --region=asia-southeast1 --project=ntu-data-science-ai
  
```

### Step 9: Seed production data

```bash
MONGO_URI=$(gcloud secrets versions access latest --secret=hmd-mongo-uri)

cd backend
conda activate help-me-doctor
MONGO_URI=$MONGO_URI python scripts/ingest_mongo.py \
  --data-dir ../data \
  --mongo-uri "$MONGO_URI"
```

### Step 10: Open & verify the live app

```bash
cd infrastructure
echo "Frontend: $(terraform output -raw frontend_url)"
echo "Backend:  $(terraform output -raw backend_url)"
```

---

## GitHub Actions CI/CD

### Setup Workload Identity Federation (one-time)

```bash
PROJECT_ID=YOUR_PROJECT_ID
REPO=YOUR_GITHUB_ORG/help-me-doctor

# Create Workload Identity Pool
gcloud iam workload-identity-pools create github-pool \
  --project=$PROJECT_ID \
  --location=global \
  --display-name="GitHub Actions Pool"

# Create provider
gcloud iam workload-identity-pools providers create-oidc github-provider --project=$PROJECT_ID --location=global --workload-identity-pool=github-pool --display-name="GitHub Provider" --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" --attribute-condition="attribute.repository=='$REPO'" --issuer-uri="https://token.actions.githubusercontent.com"

# Create service account
gcloud iam service-accounts create github-actions-sa \
  --project=$PROJECT_ID \
  --display-name="GitHub Actions Service Account"

# Grant required roles
for ROLE in \
  roles/run.admin \
  roles/artifactregistry.writer \
  roles/storage.admin \
  roles/secretmanager.secretAccessor \
  roles/aiplatform.admin \
  roles/iam.serviceAccountAdmin \
  roles/iam.serviceAccountUser \
  roles/resourcemanager.projectIamAdmin; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role=$ROLE
done

# Allow the GitHub repo to impersonate this service account
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --project=$PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO"

# Get the provider name (needed for GitHub secret)
gcloud iam workload-identity-pools providers describe github-provider \
  --project=$PROJECT_ID \
  --location=global \
  --workload-identity-pool=github-pool \
  --format="value(name)"
```

### GitHub repository configuration

Add these **Secrets** in your GitHub repo settings (`Settings → Secrets and variables → Actions`):

| Secret | Value |
|---|---|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Output of the `describe` command above |
| `GCP_SERVICE_ACCOUNT` | `github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | Your GCP project ID |
| `MONGO_URI` | Your MongoDB Atlas connection string |
| `JWT_SECRET` | Strong random secret (same as in Secret Manager) |

Add this **Variable** (under the Variables tab, not Secrets):

| Variable | Value |
|---|---|
| `BACKEND_URL` | Cloud Run backend URL from `terraform output -raw backend_url` |

> `BACKEND_URL` is baked into the frontend image at build time. Update it if the backend URL ever changes, then redeploy.

### Workflows

| Workflow | Trigger | What it does |
|---|---|---|
| **CI** | Push or PR to `main` | Lint (ruff, mypy, ESLint), test (pytest, Vitest), Docker build verification |
| **Deploy** | Push to `main` | Build & push images to Artifact Registry, `terraform apply`, health check |
| **Seed Data** | Manual (`workflow_dispatch`) | Ingest CSVs into MongoDB; optionally run Vertex AI embedding ingestion |

### Trigger a deployment

```bash
git push origin main
```

CI runs first (lint + tests). If it passes, Deploy runs automatically:
1. Build and push Docker images to Artifact Registry (tagged with git SHA + `latest`)
2. `terraform apply` with the new image tags
3. Health check on both services

### Seed data via GitHub Actions

Go to **Actions → Seed Data (One-time) → Run workflow**.

Options:
- `drop_collections`: Check to clear existing data before inserting
- `run_vertex`: Check to also run Vertex AI embedding ingestion

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `MONGO_URI` | Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | No | `helpmedoctor` | Database name |
| `JWT_SECRET` | Yes | — | JWT signing secret (min 32 chars) |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_EXPIRE_MINUTES` | No | `60` | Token expiry in minutes |
| `GCP_PROJECT_ID` | Yes (prod) | — | GCP project ID |
| `GCP_REGION` | No | `asia-southeast1` | GCP region |
| `VERTEX_INDEX_ID` | No | — | Vertex AI index resource ID |
| `VERTEX_INDEX_ENDPOINT_ID` | No | — | Vertex AI endpoint resource ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | Dev only | — | Path to service account JSON |
| `DATA_DIR` | No | `../data` | Path to CSV data directory |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `NUXT_PUBLIC_API_BASE` | Yes | `http://localhost:8000` | Backend API base URL |

---

## Project Structure

```
help-me-doctor/
├── .github/workflows/      # CI/CD pipelines
├── data/                   # 8 CSV knowledge base files
├── backend/
│   ├── app/
│   │   ├── agents/         # LangGraph 4-agent pipeline
│   │   ├── api/v1/         # FastAPI endpoints
│   │   ├── auth/           # JWT + bcrypt
│   │   ├── db/             # MongoDB connection
│   │   ├── models/         # Beanie ODM documents
│   │   ├── rag/            # Vertex AI integration
│   │   └── schemas/        # Pydantic schemas
│   ├── scripts/
│   │   ├── ingest_mongo.py  # CSV → MongoDB
│   │   └── ingest_vertex.py # Embeddings → Vertex AI
│   └── tests/
├── frontend/
│   ├── components/         # Vue components
│   ├── pages/              # Nuxt pages
│   ├── stores/             # Pinia stores
│   ├── types/              # TypeScript types
│   └── tests/              # Vitest tests
└── infrastructure/         # Terraform (GCP)
    └── modules/
        ├── artifact_registry/
        ├── cloud_run/
        ├── vertex_ai/
        └── storage/
```

---

## Troubleshooting

### Docker Compose: backend fails to start
```bash
# Check MongoDB is healthy
docker compose logs mongo

# Restart just the backend
docker compose restart backend
```

### `ingest_mongo.py` fails
```bash
# Check MongoDB connection
mongosh mongodb://localhost:27017 --eval "db.runCommand({ping: 1})"

# Check data directory
ls -la data/
```

### Vertex AI: "endpoint not configured"
This is expected if `VERTEX_INDEX_ENDPOINT_ID` is not set. The system falls back to MongoDB keyword search automatically.

### Frontend: 401 Unauthorized on chat
Your JWT token may have expired (60 min default). Log out and log in again.

### Cloud Run: cold start latency
Cloud Run scales to zero by default. The first request after idle takes ~5–10 seconds. Set `min_instance_count = 1` in Terraform for always-on (adds ~$5/month).

---

## Emergency Contacts (Singapore)

The system recommends these when appropriate:
- 🚨 **999** — Police / Emergency
- 🚑 **995** — Ambulance only
- 🏥 **SingHealth**: 6222 3322
- 💬 **Crisis hotline**: 1800-221-4444

---

## License

MIT
