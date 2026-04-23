# Procurement AI Suite (Simple Streamlit Mode)

This repo now has one primary way to run the app locally: **Streamlit**.

## Quick Start

### Windows (Command Prompt)

```bat
copy .env.example .env
REM edit .env for OpenAI or Ollama
run_streamlit.bat
```

If you see `Python was not found`, install Python 3.10+ and reopen Command Prompt.

### macOS / Linux

```bash
cp .env.example .env
# edit .env for OpenAI or Ollama
./run_streamlit.sh
```

Open: `http://localhost:8501`

---

## Streamlit Community Cloud note

On Streamlit Cloud, `OLLAMA_BASE_URL=http://localhost:11434` will **not** reach your local PC.
Use one of these options:

1. Set provider to **OpenAI** and add your API key in the sidebar, or
2. Configure Streamlit **Secrets** with `OPENAI_API_KEY`.

If you run locally on your own machine, Ollama works normally.

---

## Important: `.env` vs terminal variable syntax

In **Windows Command Prompt**, this is invalid and will fail:

```bat
AI_PROVIDER=ollama
```

Use either:

```bat
set AI_PROVIDER=ollama
set OLLAMA_BASE_URL=http://localhost:11434
set OLLAMA_MODEL=gemma3:latest
```

Or (recommended) just put these in `.env` and run `run_streamlit.bat`.

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

## Legacy full-stack mode (optional)

The old React + FastAPI stack still exists (`frontend/`, `backend/`, `docker-compose.yml`) but is no longer required for the default workflow.
