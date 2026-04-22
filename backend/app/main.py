from __future__ import annotations

from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import JobStatus, ProcessingMode
from app.services.pipeline import pipeline_service
from app.utils.job_store import job_store

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/jobs")
async def create_job(
    background_tasks: BackgroundTasks,
    mode: ProcessingMode = Form(...),
    files: list[UploadFile] = File(...),
):
    valid = [f for f in files if f.filename.endswith(".docx")]
    if not valid:
        raise HTTPException(status_code=400, detail="At least one .docx file is required")

    payloads = [(f.filename, await f.read()) for f in valid]
    job = job_store.create_job(mode, [name for name, _ in payloads])
    job_store.update_job_status(job.job_id, JobStatus.processing)

    def runner() -> None:
        has_failure = False
        for file_name, content in payloads:
            try:
                pipeline_service.process_file(job.job_id, file_name, content, mode)
            except Exception as exc:  # noqa: BLE001
                has_failure = True
                job_store.update_file(
                    job.job_id,
                    file_name,
                    status=JobStatus.failed,
                    message=str(exc),
                    progress=100,
                )

        if has_failure:
            job_store.update_job_status(job.job_id, JobStatus.failed)
        else:
            job_store.update_job_status(job.job_id, JobStatus.completed)

    background_tasks.add_task(runner)
    return job


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/download/{job_id}/{file_name}")
def download(job_id: str, file_name: str):
    path = Path(settings.storage_path) / job_id / file_name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
