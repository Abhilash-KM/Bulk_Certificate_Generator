from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import GenerationJob
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import (
    create_generation_job,
    process_generation_job,
)

from app.models import GenerationJob, Recipient
from app.schemas.job import (
    CertificateResponse,
    JobCreate,
    JobResponse,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = create_generation_job(
        db,
        job_data,
    )

    background_tasks.add_task(
        process_generation_job,
        job.id,
    )

    return job


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(GenerationJob, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job

@router.get(
    "/{job_id}/certificates",
    response_model=list[CertificateResponse],
)
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(GenerationJob, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    recipients = (
        db.query(Recipient)
        .filter(Recipient.job_id == job_id)
        .all()
    )

    return recipients