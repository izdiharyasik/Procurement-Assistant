from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.models.schemas import JobStatus, ProcessingMode
from app.services.ai_service import ai_service
from app.services.document_service import (
    build_bilingual_docx,
    build_bilingual_pdf,
    chunk_segments,
    parse_docx_segments,
)
from app.utils.job_store import job_store


class PipelineService:
    def __init__(self) -> None:
        self.storage_root = Path(settings.storage_path)
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def process_file(self, job_id: str, file_name: str, content: bytes, mode: ProcessingMode) -> None:
        out_dir = self.storage_root / job_id
        out_dir.mkdir(parents=True, exist_ok=True)

        job_store.update_file(job_id, file_name, status=JobStatus.processing, progress=5)
        _, segments = parse_docx_segments(content)
        if not segments:
            raise ValueError("No readable text found in document")

        translations: dict[int, str] = {}
        bilingual_rows: list[tuple[str, str]] = []
        translated_text = None

        if mode in (ProcessingMode.translation_only, ProcessingMode.combined):
            term_memory: dict[str, str] = {}
            chunks = chunk_segments(segments, settings.max_chunk_chars)
            total = len(chunks)
            for idx, chunk in enumerate(chunks, start=1):
                chunk_result = ai_service.translate_chunk(chunk, term_memory)
                translations.update(chunk_result)
                progress = 10 + int((idx / total) * 55)
                job_store.update_file(job_id, file_name, progress=progress)

            bilingual_rows = [(seg.original, translations.get(seg.index, "")) for seg in segments]
            translated_text = "\n".join(t for _, t in bilingual_rows)

            docx_path = out_dir / f"{Path(file_name).stem}_bilingual.docx"
            pdf_path = out_dir / f"{Path(file_name).stem}_bilingual.pdf"
            build_bilingual_docx(bilingual_rows, docx_path)
            build_bilingual_pdf(bilingual_rows, pdf_path)

            job_store.update_file(
                job_id,
                file_name,
                bilingual_docx=f"/download/{job_id}/{docx_path.name}",
                bilingual_pdf=f"/download/{job_id}/{pdf_path.name}",
                progress=75,
            )

        if mode in (ProcessingMode.review_only, ProcessingMode.combined):
            original_text = "\n".join(seg.original for seg in segments)
            review = ai_service.review_document(original_text, translated_text)
            report_path = out_dir / f"{Path(file_name).stem}_review.md"
            report_path.write_text(review, encoding="utf-8")
            job_store.update_file(
                job_id,
                file_name,
                review_report=f"/download/{job_id}/{report_path.name}",
                progress=95,
            )

        job_store.update_file(job_id, file_name, status=JobStatus.completed, progress=100)


pipeline_service = PipelineService()
