from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class ProcessingMode(str, Enum):
    translation_only = "translation_only"
    review_only = "review_only"
    combined = "combined"


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class FileResult(BaseModel):
    file_name: str
    status: JobStatus
    progress: int
    message: str = ""
    bilingual_docx: str | None = None
    bilingual_pdf: str | None = None
    review_report: str | None = None


class JobResponse(BaseModel):
    job_id: str
    mode: ProcessingMode
    status: JobStatus
    created_at: datetime
    files: list[FileResult]
