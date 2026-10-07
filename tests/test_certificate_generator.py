from datetime import date
from pathlib import Path

from app.models import GenerationJob, Recipient
from app.services.certificate_generator import generate_certificate


def test_generate_certificate(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.certificate_generator.GENERATED_DIR",
        tmp_path,
    )

    job = GenerationJob(
        id=1,
        event_name="Test Workshop",
    )

    recipient = Recipient(
        id=1,
        job_id=1,
        name="Test User",
        email="test@example.com",
        course="Python Backend Development",
        completion_date=date(2026, 10, 8),
    )

    file_path = generate_certificate(job, recipient)

    path = Path(file_path)

    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0