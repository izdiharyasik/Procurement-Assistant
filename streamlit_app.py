from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import streamlit as st
from tenacity import RetryError

# Ensure backend package imports work when launching from repo root.
sys.path.insert(0, str(Path(__file__).parent / "backend"))
os.environ.setdefault("PYTHONPATH", "backend")

# Streamlit Cloud stores API keys in st.secrets, not .env files.
if "AI_PROVIDER" in st.secrets and st.secrets["AI_PROVIDER"]:
    os.environ["AI_PROVIDER"] = str(st.secrets["AI_PROVIDER"]).lower()
if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if "OPENAI_MODEL" in st.secrets and st.secrets["OPENAI_MODEL"]:
    os.environ["OPENAI_MODEL"] = st.secrets["OPENAI_MODEL"]
if "OLLAMA_BASE_URL" in st.secrets and st.secrets["OLLAMA_BASE_URL"]:
    os.environ["OLLAMA_BASE_URL"] = str(st.secrets["OLLAMA_BASE_URL"])
if "OLLAMA_MODEL" in st.secrets and st.secrets["OLLAMA_MODEL"]:
    os.environ["OLLAMA_MODEL"] = str(st.secrets["OLLAMA_MODEL"])
if "MAX_CHUNK_CHARS" in st.secrets and st.secrets["MAX_CHUNK_CHARS"]:
    os.environ["MAX_CHUNK_CHARS"] = str(st.secrets["MAX_CHUNK_CHARS"])

from app.models.schemas import ProcessingMode  # noqa: E402
from app.services.ai_service import AIService  # noqa: E402
from app.services.document_service import (  # noqa: E402
    build_bilingual_docx,
    build_bilingual_pdf,
    chunk_segments,
    parse_docx_segments,
)

st.set_page_config(page_title="Procurement AI Suite", page_icon="⚖️", layout="wide")

st.title("🎯 Procurement AI Suite")
st.caption("Bilingual legal translator + procurement document reviewer")

st.sidebar.header("AI Configuration")
provider = st.sidebar.radio(
    "Provider",
    options=["openai", "ollama"],
    index=0 if os.getenv("AI_PROVIDER", "openai").lower() == "openai" else 1,
    horizontal=True,
)
os.environ["AI_PROVIDER"] = provider

if provider == "openai":
    openai_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Required for Streamlit Cloud unless set in Secrets.",
    )
    openai_model = st.sidebar.text_input("OpenAI Model", value=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    os.environ["OPENAI_API_KEY"] = openai_key.strip()
    os.environ["OPENAI_MODEL"] = openai_model.strip() or "gpt-4.1-mini"
else:
    ollama_url = st.sidebar.text_input("Ollama Base URL", value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_model = st.sidebar.text_input("Ollama Model", value=os.getenv("OLLAMA_MODEL", "gemma3:latest"))
    os.environ["OLLAMA_BASE_URL"] = ollama_url.strip() or "http://localhost:11434"
    os.environ["OLLAMA_MODEL"] = ollama_model.strip() or "gemma3:latest"
    st.info("Using local Ollama provider (no OpenAI API key required).")

ai_service = AIService()
api_ready = provider == "ollama" or bool(os.getenv("OPENAI_API_KEY") or getattr(ai_service, "client", None))

if not api_ready:
    st.error("OPENAI_API_KEY is not configured. Add it in the sidebar or Streamlit Secrets.")
    st.code('AI_PROVIDER = "openai"\nOPENAI_API_KEY = "sk-..."\nOPENAI_MODEL = "gpt-4.1-mini"', language="toml")

mode_map = {
    "Translation Only": ProcessingMode.translation_only,
    "Review Only": ProcessingMode.review_only,
    "Translate + Review": ProcessingMode.combined,
}

mode_label = st.radio("Mode", list(mode_map.keys()), horizontal=True)
mode = mode_map[mode_label]

uploads = st.file_uploader(
    "Upload one or more .docx files",
    type=["docx"],
    accept_multiple_files=True,
)

run = st.button("Start Processing", type="primary", disabled=not uploads or not api_ready)

if run and uploads:
    overall = st.progress(0, text="Preparing files...")

    for file_index, uploaded in enumerate(uploads, start=1):
        st.markdown(f"---\n### 📄 {uploaded.name}")
        file_status = st.empty()
        file_progress = st.progress(0)

        file_status.info("Parsing document...")
        _, segments = parse_docx_segments(uploaded.getvalue())
        if not segments:
            file_status.error("No readable content found.")
            continue

        translations: dict[int, str] = {}
        bilingual_rows: list[tuple[str, str]] = []
        translated_text: str | None = None

        if mode in (ProcessingMode.translation_only, ProcessingMode.combined):
            file_status.info("Translating document in chunks...")
            term_memory: dict[str, str] = {}
            chunks = chunk_segments(segments, max_chars=int(os.getenv("MAX_CHUNK_CHARS", "3200")))

            try:
                for idx, chunk in enumerate(chunks, start=1):
                    chunk_translated = ai_service.translate_chunk(chunk, term_memory)
                    translations.update(chunk_translated)
                    progress = int((idx / len(chunks)) * 65)
                    file_progress.progress(progress)
            except RetryError:
                file_status.error(
                    "Translation failed after multiple retries. Check API key/quota/rate limits and try again."
                )
                continue
            except Exception as exc:  # noqa: BLE001
                file_status.error(f"Translation failed: {exc}")
                continue

            bilingual_rows = [(seg.original, translations.get(seg.index, "")) for seg in segments]
            translated_text = "\n".join(t for _, t in bilingual_rows)

            with tempfile.TemporaryDirectory() as td:
                temp_dir = Path(td)
                docx_path = temp_dir / f"{Path(uploaded.name).stem}_bilingual.docx"
                pdf_path = temp_dir / f"{Path(uploaded.name).stem}_bilingual.pdf"

                build_bilingual_docx(bilingual_rows, docx_path)
                build_bilingual_pdf(bilingual_rows, pdf_path)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download Bilingual DOCX",
                        data=docx_path.read_bytes(),
                        file_name=docx_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                with col2:
                    st.download_button(
                        "Download Bilingual PDF",
                        data=pdf_path.read_bytes(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                    )

        if mode in (ProcessingMode.review_only, ProcessingMode.combined):
            file_status.info("Running procurement/legal risk review...")
            original_text = "\n".join(seg.original for seg in segments)
            try:
                review_report = ai_service.review_document(original_text, translated_text)
            except RetryError:
                file_status.error(
                    "Review failed after multiple retries. Check API key/quota/rate limits and try again."
                )
                continue
            except Exception as exc:  # noqa: BLE001
                file_status.error(f"Review failed: {exc}")
                continue

            st.subheader("Review Report")
            st.markdown(review_report)
            st.download_button(
                "Download Review Report (.md)",
                data=review_report.encode("utf-8"),
                file_name=f"{Path(uploaded.name).stem}_review.md",
                mime="text/markdown",
            )

        st.subheader("Bilingual Preview")
        if bilingual_rows:
            preview_data = [
                {"Original": original, "English": english}
                for original, english in bilingual_rows[:50]
            ]
            st.dataframe(preview_data, use_container_width=True)

        file_progress.progress(100)
        file_status.success("Completed")
        overall.progress(int((file_index / len(uploads)) * 100), text="Processing files...")

    overall.progress(100, text="All files processed")
