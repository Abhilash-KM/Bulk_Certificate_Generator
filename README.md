# Bulk Certificate Generator

A FastAPI-based backend API for generating certificates in bulk from a predefined certificate template.

The system accepts a list of recipients in a single request, creates a generation job, processes certificates in the background, tracks the status of each recipient, and allows generated certificates to be retrieved individually.

---

## Features

- Create a bulk certificate generation job
- Process multiple recipients in a single API request
- Validate recipient data using Pydantic
- Generate one PDF certificate per recipient
- Use a predefined certificate template
- Track job status and generation progress
- Track individual recipient status
- Isolate failures between individual certificate generations
- Retrieve certificates belonging to a generation job
- Download individual generated certificates
- Automated test suite using Pytest
- Interactive API documentation using Swagger/OpenAPI

---

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python 3.11 | Programming language |
| FastAPI | REST API framework |
| SQLAlchemy | Database ORM |
| SQLite | Local relational database |
| Pydantic | Request validation and serialization |
| ReportLab | PDF certificate generation |
| Pytest | Automated testing |
| HTTPX | API testing |

---

## Project Structure

```text
Bulk Certificate Generator/
│
├── app/
│   ├── __init__.py
│
│   ├── api/
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   └── certificates.py
│
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py
│   │   └── recipients.py
│
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── job.py
│
│   ├── services/
│   │   ├── __init__.py
│   │   ├── certificate_generator.py
│   │   └── job_service.py
│
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_certificate_generator.py
│   └── test_jobs.py
│
├── generated/
│   └── .gitkeep
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Abhilash-KM/Bulk_Certificate_Generator.git
cd Bulk_Certificate_Generator
```

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## 1. Create a Generation Job

```http
POST /jobs
```

This endpoint accepts an event name and a list of recipients.

Multiple certificates are submitted through a **single API request**.

### Example Request

```json
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
```

### Example Response

```json
{
  "id": 1,
  "event_name": "Python Workshop 2026",
  "status": "pending",
  "total": 2,
  "successful": 0,
  "failed": 0
}
```

The job is created first, and certificate generation is then scheduled as a background task.

Depending on when the client checks the job, the status may be `pending` or `processing`.

---

## 2. Get Job Status

```http
GET /jobs/{job_id}
```

Returns the current status and progress of a generation job.

### Example Response

```json
{
  "id": 1,
  "event_name": "Python Workshop 2026",
  "status": "completed",
  "total": 2,
  "successful": 2,
  "failed": 0
}
```

The client can repeatedly call this endpoint to determine whether processing has completed.

The `total`, `successful`, and `failed` fields provide the current generation progress.

---

## 3. Get Certificates for a Job

```http
GET /jobs/{job_id}/certificates
```

Returns the recipients associated with a job along with their certificate generation status.

### Example Response

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "course": "Python Programming",
    "status": "success",
    "file_path": "generated/certificate_1.pdf",
    "error_message": null
  },
  {
    "id": 2,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "course": "Python Programming",
    "status": "success",
    "file_path": "generated/certificate_2.pdf",
    "error_message": null
  }
]
```

---

## 4. Download a Generated Certificate

```http
GET /certificates/{certificate_id}
```

Returns the generated PDF certificate.

For example:

```http
GET /certificates/1
```

The API returns the generated PDF file as the response.

---

# Input Validation

Recipient data is validated using Pydantic before a generation job is created.

The following fields are validated:

| Field | Validation |
| --- | --- |
| `name` | Required, 1–255 characters |
| `email` | Required and must be a valid email address |
| `course` | Required, 1–255 characters |
| `completion_date` | Must be a valid date |
| `recipients` | At least one recipient is required |
| `event_name` | Required, 1–255 characters |

Invalid requests are rejected by the API before certificate generation starts.

### Example Invalid Request

```json
{
  "event_name": "Python Workshop 2026",
  "recipients": [
    {
      "name": "John Doe",
      "email": "invalid-email",
      "course": "Python Programming",
      "completion_date": "2026-10-07"
    }
  ]
}
```

FastAPI/Pydantic returns a validation error instead of creating the job.

---

# Job and Recipient Status

## Job Statuses

A generation job can have the following statuses:

### `pending`

The job has been created but processing has not started yet.

### `processing`

Certificate generation is currently in progress.

### `completed`

All certificates were generated successfully.

### `completed_with_errors`

Processing finished, but one or more certificates failed.

---

## Recipient Statuses

Each recipient has an independent status:

```text
pending
processing
success
failed
```

This allows the system to identify exactly which certificates were successfully generated and which ones failed.

---

# Failure Isolation

One of the important requirements of the system is that **failure of one certificate should not stop the remaining certificates from being generated**.

The system processes each recipient independently.

The generation flow is:

```text
Recipient 1
    │
    ├── Generate certificate
    │
    └── Success / Failure
             │
             ▼
         Continue

Recipient 2
    │
    ├── Generate certificate
    │
    └── Success / Failure
             │
             ▼
         Continue

Recipient 3
    │
    ├── Generate certificate
    │
    └── Success / Failure
```

Each certificate generation is wrapped in its own error handling.

If one certificate fails:

1. The recipient is marked as `failed`.
2. The error message is stored in the database.
3. Processing continues for the remaining recipients.
4. Successful certificates remain available.
5. The final job status becomes `completed_with_errors`.

### Example

Suppose a job contains 3 recipients:

```text
Recipient 1 → Success
Recipient 2 → Failed
Recipient 3 → Success
```

The final job status will be:

```json
{
  "total": 3,
  "successful": 2,
  "failed": 1,
  "status": "completed_with_errors"
}
```

The failure of Recipient 2 does not prevent Recipient 3 from being processed.

---

# Background Processing Design

The application uses **FastAPI BackgroundTasks** for certificate generation.

The reason for choosing background processing is that generating multiple PDF files can take time. The API does not need to keep the client waiting for every certificate to finish before returning the initial job response.

## Request Flow

```text
Client
   │
   │ POST /jobs
   ▼
Create Generation Job
   │
   ├── Store job in database
   ├── Store recipients
   └── Return job information
          │
          ▼
   Background Task
          │
          ▼
   Process Recipients
          │
          ├── Generate Certificate 1
          ├── Generate Certificate 2
          ├── Generate Certificate 3
          └── ...
          │
          ▼
   Update Job Status
          │
          ▼
   Client checks:
   GET /jobs/{job_id}
```

The client can use the job ID to check the current progress while certificate generation is running.

---

## Why BackgroundTasks?

For this assignment, FastAPI `BackgroundTasks` provides a simple way to demonstrate background job processing without introducing additional infrastructure.

Advantages:

- Simple implementation
- No external message broker required
- Easy to run locally
- Allows the initial API request to return without waiting for the complete generation process
- Separates request handling from certificate generation

For the scale of this assignment, this approach is sufficient.

`BackgroundTasks` runs within the application process, so it is not intended to replace a distributed task queue for large-scale production workloads.

---

## Production Scaling

For a production system handling a large number of certificates, FastAPI `BackgroundTasks` would not be the ideal long-term solution.

The processing layer could be replaced with a distributed task queue such as:

```text
FastAPI
   │
   ▼
Message Queue
   │
   ▼
Worker Processes
   │
   ├── Certificate 1
   ├── Certificate 2
   ├── Certificate 3
   └── ...
```

Possible technologies include:

- Celery
- Redis
- RabbitMQ
- Cloud-based queue services

The current implementation keeps certificate generation inside the service layer so that it can later be moved to worker processes without significantly changing the API layer.

---

# Database Design

SQLite is used for this assignment because it is lightweight and does not require a separate database server.

SQLAlchemy is used as the ORM.

This keeps database operations separate from the API and makes it easier to migrate to PostgreSQL in a production environment.

---

## GenerationJob

The `GenerationJob` entity stores information about the overall bulk generation request.

It contains:

- Job ID
- Event name
- Job status
- Total recipient count
- Successful count
- Failed count
- Creation time
- Completion time

---

## Recipient

The `Recipient` entity stores information about each individual certificate recipient.

It contains:

- Recipient ID
- Job ID
- Name
- Email
- Course
- Completion date
- Generation status
- Generated file path
- Error message
- Creation time

The relationship is:

```text
GenerationJob
      │
      ├── Recipient
      ├── Recipient
      ├── Recipient
      └── ...
```

This allows a single job to contain many recipients.

---

# Certificate Generation

Certificates are generated using **ReportLab**.

The application uses a predefined certificate template containing:

- Certificate title
- Recipient name
- Course name
- Event name
- Completion date
- Certificate border
- Footer

A separate PDF file is generated for every successfully processed recipient.

Example:

```text
generated/
├── certificate_1.pdf
├── certificate_2.pdf
└── certificate_3.pdf
```

The database stores the path of each generated certificate.

---

# Certificate Storage

Generated PDF files are stored locally in:

```text
generated/
```

The database stores the path of each generated file.

The generated PDF files are excluded from Git using `.gitignore`.

For a production deployment, generated certificates could be stored in object storage such as:

- Amazon S3
- Google Cloud Storage
- Azure Blob Storage

This would make certificate storage more suitable for distributed deployments.

---

# Service Layer Design

The application separates HTTP/API logic from business logic.

```text
API Layer
   │
   ▼
Service Layer
   │
   ├── Job Processing
   │
   └── Certificate Generation
          │
          ▼
      Database / Files
```

## API Layer

Responsible for:

- Receiving HTTP requests
- Returning HTTP responses
- Request validation
- HTTP error handling

Located in:

```text
app/api/
```

## Service Layer

Responsible for:

- Creating generation jobs
- Processing recipients
- Generating certificates
- Updating generation status
- Handling individual failures

Located in:

```text
app/services/
```

## Models

Represent database entities.

Located in:

```text
app/models/
```

## Schemas

Define request and response structures using Pydantic.

Located in:

```text
app/schemas/
```

## Database Layer

Handles:

- SQLAlchemy engine
- Database sessions
- Database configuration

Located in:

```text
app/db/
```

---

# Testing

The project uses **Pytest** for automated testing.

Run the complete test suite:

```bash
pytest
```

Current test coverage includes:

- Creating a generation job
- Input validation
- Invalid email validation
- Missing required fields
- Empty recipient list validation
- Certificate generation
- Job status
- Job progress
- Individual certificate failure
- Failure isolation
- Certificate retrieval

Current test result:

```text
8 passed
```

A test database is used during testing so that tests do not modify the application's actual SQLite database.

Generated test certificates are also written to a temporary directory.

---

# Design Decisions

## Why FastAPI?

FastAPI was selected because it provides:

- REST API support
- Automatic request validation
- Pydantic integration
- Automatic OpenAPI/Swagger documentation
- Dependency injection
- Background task support
- Good performance for API workloads

---

## Why SQLAlchemy?

SQLAlchemy provides an ORM abstraction between the application and the database.

This makes the code easier to maintain and allows SQLite to be replaced with PostgreSQL later with minimal changes to the application logic.

---

## Why SQLite?

SQLite was selected for the assignment because:

- It requires no separate database server
- It is easy to set up
- It is sufficient for local development and demonstration
- SQLAlchemy keeps the application portable to a production database

For production, PostgreSQL would be a more appropriate choice.

---

## Why ReportLab?

ReportLab provides programmatic PDF generation and allows the certificate template to be generated dynamically with recipient-specific information.

---

## Why BackgroundTasks?

`BackgroundTasks` allows certificate generation to be scheduled as background work after the API request has been accepted.

This prevents the initial API request from waiting for every certificate to be generated.

For a production-scale system, a distributed task queue would be preferred because it provides more reliable and scalable background processing.

---

## Why Separate the Service Layer?

The service layer keeps business logic independent from HTTP routes.

This provides:

- Better testability
- Cleaner API routes
- Easier maintenance
- Easier migration to background workers
- Better separation of responsibilities

---

# Error Handling

The API handles common errors such as:

- Job not found
- Certificate not found
- Certificate generation failure
- Invalid recipient data
- Missing generated certificate file

Example:

```http
GET /jobs/999
```

returns:

```json
{
  "detail": "Job not found"
}
```

If a certificate was not generated successfully, the download endpoint does not return a file.

---

# Future Improvements

For a production deployment, the following improvements could be considered:

- PostgreSQL instead of SQLite
- Celery/Redis or another distributed task queue
- Cloud object storage
- Authentication and authorization
- Configurable certificate templates
- Template upload support
- Bulk ZIP download
- Retry mechanism for failed certificates
- Job cancellation
- Job progress percentage
- Structured logging
- Monitoring and metrics
- Docker containerization
- Cloud deployment
- Rate limiting
- API versioning

---

# Example End-to-End Flow

```text
1. Client submits recipient list
          │
          ▼
2. FastAPI validates request
          │
          ▼
3. Generation job is created
          │
          ▼
4. Recipients are stored
          │
          ▼
5. Background processing starts
          │
          ▼
6. Certificates are generated individually
          │
          ├───────────────┐
          ▼               ▼
      Success           Failure
          │               │
          ▼               ▼
    Store PDF        Store error
          │               │
          └───────┬───────┘
                  ▼
7. Job counters are updated
                  │
                  ▼
8. Client checks job status
                  │
                  ▼
9. Client retrieves certificate
                  │
                  ▼
10. PDF is returned
```
