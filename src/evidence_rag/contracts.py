import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Role = Literal["reader", "maintainer"]
RetrievalMode = Literal["bm25", "dense", "hybrid", "hybrid_rerank"]
GenerationMode = Literal["extractive", "local"]
JobStatus = Literal["queued", "running", "succeeded", "failed", "cancelled", "interrupted"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorDetail(StrictModel):
    code: str
    message: str
    request_id: str


class ApiError(StrictModel):
    error: ErrorDetail


class LoginInput(StrictModel):
    code: str = Field(min_length=1, max_length=256)


class SessionView(StrictModel):
    user_id: str
    role: Role
    csrf_token: str


class QuestionRequest(StrictModel):
    question: str = Field(min_length=1, max_length=500)
    retrieval_mode: RetrievalMode = "hybrid_rerank"
    generation_mode: GenerationMode = "extractive"


class Citation(StrictModel):
    chunk_id: str
    document_id: str
    version_id: str
    title: str
    version_label: str
    effective_date: str
    section_id: str
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    quote: str


class CitationView(Citation):
    section_text: str
    section_start_char: int
    highlight_start: int
    highlight_end: int


class Answer(StrictModel):
    request_id: str
    execution_profile: Literal["fixture", "local"]
    retrieval_mode: RetrievalMode
    generation_mode: GenerationMode
    answer: str
    abstained: bool
    reason: str | None
    citations: list[Citation]
    timings_ms: dict[str, float]


class VersionInput(StrictModel):
    title: str = Field(min_length=1, max_length=120)
    min_role: Role = "reader"
    label: str = Field(min_length=1, max_length=40)
    effective_date: str
    markdown: str = Field(min_length=1)

    @field_validator("effective_date")
    @classmethod
    def valid_date(cls, value: str) -> str:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError("Use ISO date")
        return value

    @field_validator("markdown")
    @classmethod
    def plain_markdown(cls, value: str) -> str:
        if (
            not value.strip()
            or len(value.encode("utf-8")) > 256 * 1024
            or "\x00" in value
            or re.search(r"<\s*script\b", value, re.IGNORECASE)
        ):
            raise ValueError("Invalid Markdown or document exceeds 256 KiB")
        if not re.match(r"^#{1,6}\s+\S", value):
            raise ValueError("Start with a heading")
        return value


class ImportInput(VersionInput):
    pass


class ReplaceInput(VersionInput):
    expected_revision: int = Field(ge=1)


class RebuildInput(StrictModel):
    pass


class DocumentSummary(StrictModel):
    id: str
    title: str
    version_id: str
    version_label: str
    effective_date: str
    revision: int


class DocumentView(DocumentSummary):
    text: str


class JobView(StrictModel):
    id: str
    status: JobStatus
    error_code: str | None
    created_at: str
    updated_at: str


class JobAccepted(StrictModel):
    job_id: str
