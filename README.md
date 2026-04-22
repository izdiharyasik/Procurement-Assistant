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

## 1-Minute Quick Start (Easiest)

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
./run_streamlit.sh
```

Then open `http://localhost:8501`.

---

## Manual Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
# edit .env and set OPENAI_API_KEY
set -a; source .env; set +a
streamlit run streamlit_app.py
```

---


## Streamlit Community Cloud Deployment

If deploying on Streamlit Community Cloud, keep these files at repo root:

- `streamlit_app.py`
- `requirements.txt` (this repo now includes one that points to `backend/requirements.txt`)
- `runtime.txt` (pins Python version)

This is required so non-Streamlit dependencies (like `pydantic`, `openai`, `python-docx`, `reportlab`) are installed before app startup.

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
- Exponential backoff retries for OpenAI calls
- Low temperature for legal consistency
- Term memory dictionary carried across chunks

---

## Notes

- Best for legal/procurement `.docx` documents with clauses, numbering, and tables.
- If `OPENAI_API_KEY` is missing, the app will still load but processing will fail until configured.
