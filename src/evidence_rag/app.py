import asyncio
import sqlite3

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from evidence_rag.api.guard import Guard
from evidence_rag.api.session import router
from evidence_rag.config import Settings
from evidence_rag.db.repository import Repository
from evidence_rag.errors import DomainError


def create_app(settings: Settings) -> FastAPI:
    repo = Repository(settings.database)
    app = FastAPI(title="Evidence RAG", version="0.1.0")
    app.state.settings = settings
    app.state.repo = repo
    lock = asyncio.Lock()
    app.state.publication_lock = lock

    @app.exception_handler(DomainError)
    async def domain_error(_request: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(error.payload(), status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _error: RequestValidationError) -> JSONResponse:
        return JSONResponse(DomainError(422, "invalid_input").payload(), status_code=422)

    @app.exception_handler(sqlite3.OperationalError)
    async def storage_error(_request: Request, _error: sqlite3.OperationalError) -> JSONResponse:
        return JSONResponse(DomainError(503, "storage_busy").payload(), status_code=503)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "execution_profile": settings.profile}

    app.include_router(router(repo))
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
