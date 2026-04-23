# Procurement AI Suite (Streamlit Edition)

A production-oriented procurement/legal AI app with a simplified Streamlit interface.

## What it does

- Upload multiple `.docx` legal/procurement files
- Choose mode:
  - `Translation Only`
  - `Review Only`
  - `Translate + Review`
- Generate bilingual outputs (`.docx` + `.pdf`) in two-column layout
- Generate structured procurement/legal review report (`.md`)
- Download all generated outputs directly from the UI

## AI Provider Options

You can run this app in two ways:

1. **OpenAI (paid API)**
2. **Ollama (local, no API key cost)**

Set this with `AI_PROVIDER` in `.env` or Streamlit secrets.

## 1-Minute Quick Start (OpenAI)

```bash
cp .env.example .env
# edit .env and set AI_PROVIDER=openai + OPENAI_API_KEY
./run_streamlit.sh
```

Then open `http://localhost:8501`.

## 1-Minute Quick Start (No OpenAI key, using Ollama)

```bash
# install ollama first: https://ollama.com/download
ollama pull llama3.1:8b
cp .env.example .env
# edit .env:
# AI_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.1:8b
./run_streamlit.sh
```

---

## Manual Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
# set AI_PROVIDER and relevant keys/urls
set -a; source .env; set +a
streamlit run streamlit_app.py
```

---

## Streamlit Community Cloud Deployment

If deploying on Streamlit Community Cloud, keep these files at repo root:

- `streamlit_app.py`
- `requirements.txt` (Streamlit-specific dependencies only)
- `runtime.txt` (pins Python version)

### Streamlit Secrets (Cloud)

OpenAI mode:

```toml
AI_PROVIDER = "openai"
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4.1-mini"
MAX_CHUNK_CHARS = 3200
```

Ollama mode (only works if Ollama endpoint is reachable from deployment environment):

```toml
AI_PROVIDER = "ollama"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"
MAX_CHUNK_CHARS = 3200
```

## Docker (Optional)

The previous React + FastAPI docker-compose setup remains in this repo if needed.

```bash
cp .env.example .env
docker compose up --build
```

- FastAPI: `http://localhost:8000`
- React UI: `http://localhost:5173`

---

## Reliability / Anti-throttle controls

- Chunked translation for long docs
- Exponential backoff retries for AI calls
- Low temperature for legal consistency
- Term memory dictionary carried across chunks

---

## Notes

- Best for legal/procurement `.docx` documents with clauses, numbering, and tables.
- For completely free/local inference, use `AI_PROVIDER=ollama`.
