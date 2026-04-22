# Procurement AI Suite

Production-oriented web application for bilingual legal translation and procurement document review.

## Architecture

- **Frontend**: React + Tailwind + react-dropzone
- **Backend**: FastAPI + python-docx + reportlab + OpenAI API
- **Pipeline**:
  1. Upload `.docx` files
  2. Parse paragraphs and table cells
  3. Chunk text with glossary memory
  4. Translate to formal legal English (optional)
  5. Generate bilingual outputs (`.docx` + `.pdf`)
  6. Run procurement review analysis (optional)
  7. Return downloadable artifacts

## Core Modes

- `translation_only`
- `review_only`
- `combined` (translate + review original and translated versions)

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:5173`.

## Docker Deployment

```bash
cp .env.example .env
# set OPENAI_API_KEY in .env
docker compose up --build
```

## Production Deployment Guide

1. Deploy backend as a container service (AWS ECS/Fargate, GCP Cloud Run, Azure Container Apps).
2. Use object storage (S3/GCS/Blob) for artifacts instead of local filesystem.
3. Replace in-memory job store with Redis + Postgres for persistence and horizontal scale.
4. Add background queue (Celery/RQ/Arq) for long-running document jobs.
5. Configure API gateway + WAF + rate limiting + auth (OIDC/JWT).
6. Add observability (OpenTelemetry, structured logs, alerting).
7. Enforce encrypted secrets management (Vault/SM/KMS).

## Throttling / Reliability Controls

- Exponential backoff retries on OpenAI calls (`tenacity`, up to 5 attempts)
- Configurable chunk size (`MAX_CHUNK_CHARS`) to reduce context overload
- Low temperature + JSON-constrained translation format for consistency
- Per-file progress and failure isolation in batch jobs

## Legal Formatting Notes

- Translation preserves segment order and numbering text as parsed.
- Output is rendered in a two-column legal layout (Original / English).
- Supports paragraph and table-cell extraction from `.docx`.

## Roadmap

- Term memory persistence per organization
- User auth, workspace history, and billing
- Version comparison/redline and audit trails
- Multi-language expansion
