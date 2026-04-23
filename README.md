# Procurement AI Suite (Simple Streamlit Mode)

This repo now has one primary way to run the app locally: **Streamlit**.

## Quick Start (3 steps)

```bash
cp .env.example .env
# edit .env for either OpenAI or Ollama
./run_streamlit.sh
```

Open: `http://localhost:8501`

---

## Environment setup

Use one provider in `.env`:

### Option A: OpenAI

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

### Option B: Ollama (local, use what you already installed)

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:latest
```

No new model download is required. Use any local model from:

```bash
ollama list
```

Examples from existing installs:
- `gemma3:latest`
- `phi:latest`

---

## What the app does

- Upload `.docx` procurement/legal files
- Run translation, review, or both
- Generate bilingual `.docx`/`.pdf` outputs
- Generate a structured markdown review report
- Download results directly from the UI

---

## Legacy full-stack mode (optional)

The old React + FastAPI stack still exists (`frontend/`, `backend/`, `docker-compose.yml`) but is no longer required for the default workflow.
