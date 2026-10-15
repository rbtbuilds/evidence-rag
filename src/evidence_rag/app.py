import asyncio
import logging
import sqlite3
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from evidence_rag.answers.publish import PublicationGate
from evidence_rag.answers.service import AnswerService
from evidence_rag.api import admin, documents, questions
from evidence_rag.api.guard import Guard
from evidence_rag.api.session import router
from evidence_rag.config import Settings
from evidence_rag.contracts import ApiError
from evidence_rag.db.repository import Repository
from evidence_rag.documents.chunking import Chunk
from evidence_rag.documents.jobs import JobService
from evidence_rag.errors import DomainError
from evidence_rag.models.runner import ModelRunner
from evidence_rag.retrieval.service import build_index
from evidence_rag.retrieval.types import IndexDraft


def create_app(settings: Settings) -> FastAPI:
    logging.getLogger("uvicorn.access").disabled = True
    repo = Repository(settings.database)
    lock = asyncio.Lock()
    jobs = JobService(repo, lock)
    if settings.profile == "local":
        model_jobs = ModelRunner(settings.root)

        def local_builder(chunks: tuple[Chunk, ...]) -> IndexDraft:
            with model_jobs.session("document indexing", timeout=600) as session:
                return build_index(chunks, session)

        jobs.builder = local_builder
        jobs.cancel_models = model_jobs.cancel

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        jobs.start()
        try:
            yield
        finally:
            answers.runner.cancel()
            await jobs.stop()

    app = FastAPI(
        title="Evidence RAG",
        version="0.1.0",
        lifespan=lifespan,
        responses={
            status: {"model": ApiError}
            for status in (400, 401, 403, 404, 409, 413, 422, 429, 500, 503, 504)
        },
    )
    answers = AnswerService(repo, settings)
    app.state.answers = answers
    app.state.jobs = jobs
    app.state.settings = settings
    app.state.repo = repo
    app.state.publication_lock = lock

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException) -> JSONResponse:
        code = (
            "not_found"
            if error.status_code == 404
            else "method_not_allowed"
            if error.status_code == 405
            else "request_failed"
        )
        return JSONResponse(
            DomainError(error.status_code, code).payload(str(request.state.request_id)),
            status_code=error.status_code,
        )

    @app.exception_handler(DomainError)
    async def domain_error(_request: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(error.payload(str(_request.state.request_id)), status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _error: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            DomainError(422, "invalid_input").payload(str(_request.state.request_id)),
            status_code=422,
        )

    @app.exception_handler(sqlite3.OperationalError)
    async def storage_error(_request: Request, _error: sqlite3.OperationalError) -> JSONResponse:
        return JSONResponse(
            DomainError(503, "storage_busy").payload(str(_request.state.request_id)),
            status_code=503,
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "execution_profile": settings.profile}

    app.include_router(router(repo))
    app.include_router(questions.router(answers, PublicationGate(repo, lock)))
    app.include_router(documents.router(repo))
    app.include_router(admin.router(repo, jobs))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "X-CSRF-Token", "If-Match"],
    )
    app.add_middleware(Guard, settings=settings, repo=repo, publication_lock=lock)
    return app


def create_default_app() -> FastAPI:
    return create_app(Settings.from_env())
