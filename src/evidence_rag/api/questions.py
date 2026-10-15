import asyncio
from dataclasses import replace

from fastapi import APIRouter, Request

from evidence_rag.answers.publish import CheckedResponse, PublicationGate
from evidence_rag.answers.service import AnswerService
from evidence_rag.api.session import COOKIE
from evidence_rag.contracts import Answer, QuestionRequest


def router(service: AnswerService, gate: PublicationGate) -> APIRouter:
    routes = APIRouter()

    @routes.post("/api/questions", response_model=Answer)
    async def ask(body: QuestionRequest, request: Request) -> CheckedResponse:
        token = request.cookies.get(COOKIE, "")
        scope = service.repo.resolve_scope(token)
        pending = await asyncio.to_thread(service.answer, scope, body)
        pending = replace(
            pending,
            answer=pending.answer.model_copy(update={"request_id": str(request.state.request_id)}),
        )
        return CheckedResponse(gate, token, pending)

    return routes
