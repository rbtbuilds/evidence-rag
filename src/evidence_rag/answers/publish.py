import asyncio

from fastapi.responses import JSONResponse
from starlette.types import Receive, Scope, Send

from evidence_rag.answers.cache import Cache
from evidence_rag.answers.service import PendingAnswer
from evidence_rag.db.repository import Repository
from evidence_rag.errors import DomainError


class PublicationGate:
    def __init__(self, repo: Repository, lock: asyncio.Lock) -> None:
        self.repo, self.lock = repo, lock

    async def send_checked(self, session_id: str, pending: PendingAnswer, send: Send) -> None:
        async with self.lock:
            try:
                current = self.repo.resolve_scope(session_id)
                if current != pending.scope:
                    raise DomainError(409, "corpus_changed")
                self.repo.check_citations(current, [c.chunk_id for c in pending.answer.citations])
                Cache(self.repo).put(current, pending.key, pending.answer)
                response = JSONResponse(pending.answer.model_dump())
            except DomainError as error:
                response = JSONResponse(error.payload(), status_code=error.status)
            await response({"type": "http"}, _unused_receive, send)


async def _unused_receive() -> dict[str, object]:
    return {"type": "http.disconnect"}


class CheckedResponse(JSONResponse):
    def __init__(self, gate: PublicationGate, token: str, pending: PendingAnswer) -> None:
        super().__init__({})
        self.gate, self.token, self.pending = gate, token, pending

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.gate.send_checked(self.token, self.pending, send)
