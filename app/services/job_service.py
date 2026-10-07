from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models import GenerationJob, Recipient
from app.schemas.job import JobCreate
from app.services.certificate_generator import generate_certificate


def create_generation_job(
    db: Session,
    job_data: JobCreate,
) -> GenerationJob:
    job = GenerationJob(
        event_name=job_data.event_name,
        status="pending",
        total=len(job_data.recipients),
        successful=0,
        failed=0,
    )

    db.add(job)
    db.flush()

    for recipient_data in job_data.recipients:
        recipient = Recipient(
            job_id=job.id,
            name=recipient_data.name,
            email=recipient_data.email,
            course=recipient_data.course,
            completion_date=recipient_data.completion_date,
            status="pending",
        )

        db.add(recipient)

    db.commit()
    db.refresh(job)

    return job


def process_generation_job(
    job_id: int,
    db: Session | None = None,
) -> None:
    owns_session = db is None

    if owns_session:
        db = SessionLocal()

    try:
        job = db.get(GenerationJob, job_id)

        if job is None:
            return

        job.status = "processing"
        db.commit()

        recipients = db.scalars(
            select(Recipient).where(
                Recipient.job_id == job_id
            )
        ).all()

        for recipient in recipients:
            recipient.status = "processing"
            db.commit()

            try:
                file_path = generate_certificate(
                    job,
                    recipient,
                )

                recipient.status = "success"
                recipient.file_path = file_path
                recipient.error_message = None

            except Exception as exc:
                recipient.status = "failed"
                recipient.file_path = None
                recipient.error_message = str(exc)

            db.commit()

        successful = db.scalar(
            select(func.count())
            .select_from(Recipient)
            .where(
                Recipient.job_id == job_id,
                Recipient.status == "success",
            )
        ) or 0

        failed = db.scalar(
            select(func.count())
            .select_from(Recipient)
            .where(
                Recipient.job_id == job_id,
                Recipient.status == "failed",
            )
        ) or 0

        job = db.get(GenerationJob, job_id)

        job.successful = successful
        job.failed = failed

        if failed == 0:
            job.status = "completed"
        else:
            job.status = "completed_with_errors"

        job.completed_at = datetime.now(timezone.utc)

        db.commit()

    finally:
        if owns_session:
            db.close()