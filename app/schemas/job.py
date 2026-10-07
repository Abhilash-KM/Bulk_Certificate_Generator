from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    course: str = Field(min_length=1, max_length=255)
    completion_date: date


class JobCreate(BaseModel):
    event_name: str = Field(min_length=1, max_length=255)
    recipients: list[RecipientCreate] = Field(min_length=1)


class RecipientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    course: str
    completion_date: date
    status: str
    file_path: str | None = None
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    id: int
    event_name: str
    status: str
    total: int
    successful: int
    failed: int

    model_config = ConfigDict(from_attributes=True)


class CertificateResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    course: str
    status: str
    file_path: str | None = None
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)