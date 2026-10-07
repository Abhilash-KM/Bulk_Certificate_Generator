from app.models import GenerationJob, Recipient, job
from app.services.job_service import process_generation_job
from datetime import date

def test_job_processing_tracks_success_and_failure(db_session, monkeypatch):
    job = GenerationJob(
        event_name="Test Workshop",
        status="pending",
        total=3,
        successful=0,
        failed=0,
    )

    db_session.add(job)
    db_session.flush()

    recipients = [
        Recipient(
            job_id=job.id,
            name="Success User 1",
            email="success1@example.com",
            course="Python",
            completion_date=date(2026, 10, 8),
            status="pending",
        ),
        Recipient(
            job_id=job.id,
            name="Fail User",
            email="fail@example.com",
            course="Python",
            completion_date=date(2026, 10, 8),
            status="pending",
        ),
        Recipient(
            job_id=job.id,
            name="Success User 2",
            email="success2@example.com",
            course="Python",
            completion_date=date(2026, 10, 8),
            status="pending",
        ),
    ]

    db_session.add_all(recipients)
    db_session.commit()

    def fake_generate_certificate(job, recipient):
        if recipient.name == "Fail User":
            raise RuntimeError("Simulated certificate generation failure")

        return f"generated/certificate_{recipient.id}.pdf"

    monkeypatch.setattr(
        "app.services.job_service.generate_certificate",
        fake_generate_certificate,
    )

    process_generation_job(job.id, db_session)
    db_session.refresh(job)

    assert job.status == "completed_with_errors"
    assert job.total == 3
    assert job.successful == 2
    assert job.failed == 1

    recipients = (
        db_session.query(Recipient)
        .filter(Recipient.job_id == job.id)
        .all()
    )

    assert recipients[0].status == "success"
    assert recipients[1].status == "failed"
    assert recipients[2].status == "success"

    assert recipients[1].error_message == (
        "Simulated certificate generation failure"
    )

def test_create_job(client):
    payload = {
        "event_name": "Test Workshop",
        "recipients": [
            {
                "name": "Test User",
                "email": "test@example.com",
                "course": "Python",
                "completion_date": "2026-10-08",
            },
            {
                "name": "Another User",
                "email": "another@example.com",
                "course": "Python",
                "completion_date": "2026-10-08",
            },
        ],
    }

    response = client.post(
        "/jobs",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_name"] == "Test Workshop"
    assert data["status"] in ["pending", "processing", "completed"]
    assert data["total"] == 2

def test_create_job_rejects_invalid_email(client):
    payload = {
        "event_name": "Test Workshop",
        "recipients": [
            {
                "name": "Test User",
                "email": "not-an-email",
                "course": "Python",
                "completion_date": "2026-10-08",
            }
        ],
    }

    response = client.post(
        "/jobs",
        json=payload,
    )

    assert response.status_code == 422

def test_create_job_rejects_missing_name(client):
    payload = {
        "event_name": "Test Workshop",
        "recipients": [
            {
                "email": "test@example.com",
                "course": "Python",
                "completion_date": "2026-10-08",
            }
        ],
    }

    response = client.post(
        "/jobs",
        json=payload,
    )

    assert response.status_code == 422

def test_create_job_rejects_empty_recipient_list(client):
    payload = {
        "event_name": "Test Workshop",
        "recipients": [],
    }

    response = client.post(
        "/jobs",
        json=payload,
    )

    assert response.status_code == 422

def test_get_job_status(client, db_session):
    payload = {
        "event_name": "Status Test",
        "recipients": [
            {
                "name": "Test User",
                "email": "test@example.com",
                "course": "Python",
                "completion_date": "2026-10-08",
            }
        ],
    }

    response = client.post("/jobs", json=payload)

    assert response.status_code == 201

    job_id = response.json()["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job_id
    assert data["event_name"] == "Status Test"
    assert data["total"] == 1
    assert data["successful"] >= 0
    assert data["failed"] >= 0
    assert data["successful"] + data["failed"] <= data["total"]

def test_retrieve_generated_certificate(client):
    payload = {
        "event_name": "Certificate Retrieval Test",
        "recipients": [
            {
                "name": "Test User",
                "email": "test@example.com",
                "course": "Python Backend Development",
                "completion_date": "2026-10-08",
            }
        ],
    }

    response = client.post("/jobs", json=payload)

    assert response.status_code == 201

    job_id = response.json()["id"]

    certificates_response = client.get(
        f"/jobs/{job_id}/certificates"
    )

    assert certificates_response.status_code == 200

    certificates = certificates_response.json()

    assert len(certificates) == 1

    certificate_id = certificates[0]["id"]

    certificate_response = client.get(
        f"/certificates/{certificate_id}"
    )

    assert certificate_response.status_code == 200
    assert certificate_response.headers["content-type"] == "application/pdf"
    assert len(certificate_response.content) > 0