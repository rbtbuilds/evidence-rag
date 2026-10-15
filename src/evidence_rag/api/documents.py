from uuid import UUID

from fastapi import APIRouter, Request

from evidence_rag.api.session import COOKIE
from evidence_rag.contracts import CitationView, DocumentSummary, DocumentView
from evidence_rag.db.repository import Repository


def router(repo: Repository) -> APIRouter:
    routes = APIRouter()

    @routes.get("/api/documents", response_model=list[DocumentSummary])
    def documents(request: Request) -> list[DocumentSummary]:
        return repo.documents(repo.resolve_scope(request.cookies.get(COOKIE, "")))

    @routes.get("/api/documents/{document_id}", response_model=DocumentView)
    def document(document_id: UUID, request: Request) -> DocumentView:
        return repo.document(repo.resolve_scope(request.cookies.get(COOKIE, "")), str(document_id))

    @routes.get("/api/citations/{chunk_id}", response_model=CitationView)
    def citation(chunk_id: str, request: Request) -> CitationView:
        return repo.citation(repo.resolve_scope(request.cookies.get(COOKIE, "")), chunk_id)

    return routes
