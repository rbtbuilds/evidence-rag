from uuid import UUID

from fastapi import APIRouter, Header
from fastapi.responses import Response

from evidence_rag.contracts import ImportInput, JobAccepted, JobView, RebuildInput, ReplaceInput
from evidence_rag.db.repository import Repository
from evidence_rag.documents.jobs import JobService
from evidence_rag.errors import DomainError


def router(repo: Repository, jobs: JobService) -> APIRouter:
    routes = APIRouter(prefix="/api/admin")

    @routes.post("/documents", status_code=202, response_model=JobAccepted)
    async def create(body: ImportInput) -> dict[str, str]:
        return {"job_id": jobs.enqueue("import", body)}

    @routes.post("/documents/{document_id}/versions", status_code=202, response_model=JobAccepted)
    async def replace(document_id: UUID, body: ReplaceInput) -> dict[str, str]:
        return {"job_id": jobs.enqueue("replace", body, str(document_id))}

    @routes.post("/rebuild", status_code=202, response_model=JobAccepted)
    async def rebuild(body: RebuildInput) -> dict[str, str]:
        return {"job_id": jobs.enqueue("rebuild", body)}

    @routes.get("/jobs/{job_id}", response_model=JobView)
    def job(job_id: UUID) -> JobView:
        return jobs.view(str(job_id))

    @routes.post("/jobs/{job_id}/cancel", response_model=JobView)
    def cancel(job_id: UUID, body: RebuildInput) -> JobView:
        return jobs.cancel(str(job_id))

    @routes.delete("/documents/{document_id}", status_code=204)
    def delete(document_id: UUID, if_match: str = Header()) -> Response:
        if not if_match.isdecimal():
            raise DomainError(422, "invalid_input")
        repo.delete(str(document_id), int(if_match))
        jobs.cancel_document(str(document_id))
        return Response(status_code=204)

    @routes.get("/documents/{document_id}/versions/{version_id}")
    def history(document_id: UUID, version_id: UUID) -> dict[str, str]:
        with repo.connection() as db:
            row = db.execute(
                "SELECT v.label,v.status,v.effective_date,v.text FROM versions v JOIN documents d ON v.document_id=d.id WHERE d.id=? AND v.id=? AND d.deleted_at IS NULL AND v.status IN ('active','superseded') AND v.text IS NOT NULL",
                (str(document_id), str(version_id)),
            ).fetchone()
        if row is None:
            raise DomainError(404, "not_found")
        return {key: str(row[key]) for key in ("label", "status", "effective_date", "text")}

    return routes
