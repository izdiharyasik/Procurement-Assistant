from __future__ import annotations

from datetime import datetime
from threading import Lock
from uuid import uuid4

from app.models.schemas import FileResult, JobResponse, JobStatus, ProcessingMode


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobResponse] = {}
        self._lock = Lock()

    def create_job(self, mode: ProcessingMode, file_names: list[str]) -> JobResponse:
        with self._lock:
            job_id = str(uuid4())
            job = JobResponse(
                job_id=job_id,
                mode=mode,
                status=JobStatus.queued,
                created_at=datetime.utcnow(),
                files=[
                    FileResult(file_name=name, status=JobStatus.queued, progress=0)
                    for name in file_names
                ],
            )
            self._jobs[job_id] = job
            return job

    def get(self, job_id: str) -> JobResponse | None:
        return self._jobs.get(job_id)

    def update_job_status(self, job_id: str, status: JobStatus) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = status

    def update_file(self, job_id: str, file_name: str, **updates) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for file_result in job.files:
                if file_result.file_name == file_name:
                    for key, value in updates.items():
                        setattr(file_result, key, value)
                    break


job_store = InMemoryJobStore()
