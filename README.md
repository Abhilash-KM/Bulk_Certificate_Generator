\# Bulk Certificate Generator



A FastAPI-based backend API for generating certificates in bulk from a predefined certificate template.



\## Features



\- Create a bulk certificate generation job

\- Validate recipient data using Pydantic

\- Generate one PDF certificate per valid recipient

\- Process multiple recipients in a single API request

\- Track job progress and generation status

\- Isolate individual certificate failures

\- Retrieve generated certificate metadata

\- Download individual generated certificates

\- Automated tests using Pytest



\## Technology Stack



\- Python 3.11

\- FastAPI

\- SQLAlchemy

\- SQLite

\- Pydantic

\- ReportLab

\- Pytest

\- HTTPX



\## Project Structure



```text

Bulk Certificate Generator/

├── app/

│   ├── api/

│   │   ├── jobs.py

│   │   └── certificates.py

│   ├── db/

│   │   └── database.py

│   ├── models/

│   │   ├── job.py

│   │   └── recipient.py

│   ├── schemas/

│   │   └── job.py

│   ├── services/

│   │   ├── certificate\_generator.py

│   │   └── job\_service.py

│   └── main.py

├── tests/

│   ├── conftest.py

│   ├── test\_jobs.py

│   └── test\_certificate\_generator.py

├── generated/

│   └── .gitkeep

├── .gitignore

├── requirements.txt

└── README.md

##Setup

1. Clone the repository

    git clone <repository-url>
    cd "Bulk Certificate Generator"

2. Create a virtual environment
    python -m venv .venv

    Activate it on Windows:
    .venv\Scripts\Activate.ps1

3. Install dependencies
    pip install -r requirements.txt

Run the Application
Start the FastAPI server:
    uvicorn app.main:app --reload

The API will be available at:
http://127.0.0.1:8000

Interactive API documentation:
http://127.0.0.1:8000/docs

API Endpoints
Create a Generation Job
POST /jobs

Example request:
{
  "event_name": "Python Workshop 2026",
  "recipients": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "course": "Python Programming",
      "completion_date": "2026-10-07"
    },
    {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "course": "Python Programming",
      "completion_date": "2026-10-07"
    }
  ]
}

The API creates a job and starts certificate generation in the background.
Example response:
{
  "id": 1,
  "event_name": "Python Workshop 2026",
  "status": "pending",
  "total": 2,
  "successful": 0,
  "failed": 0
}

Get Job Status
GET /jobs/{job_id}

Example:
{
  "id": 1,
  "event_name": "Python Workshop 2026",
  "status": "completed",
  "total": 2,
  "successful": 2,
  "failed": 0
}

Get Certificates for a Job
GET /jobs/{job_id}/certificates

This returns the generation status and file information for each recipient.
Download a Certificate
GET /certificates/{certificate_id}

The endpoint returns the generated PDF file.