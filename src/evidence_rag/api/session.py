from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from evidence_rag.auth.sessions import SessionService
from evidence_rag.contracts import LoginInput, SessionView
from evidence_rag.db.repository import Repository

COOKIE = "evidence_session"


def router(repo: Repository) -> APIRouter:
    routes = APIRouter()
    service = SessionService(repo)

    @routes.post("/api/session", response_model=SessionView)
    def login(body: LoginInput) -> JSONResponse:
        session = service.login(body.code)
        response = JSONResponse(
            SessionView(
                user_id=session.user_id, role=session.role, csrf_token=session.csrf_token
            ).model_dump()
        )
        response.set_cookie(
            COOKIE, session.session_id, httponly=True, samesite="strict", secure=False, max_age=3600
        )
        return response

    @routes.get("/api/session", response_model=SessionView)
    def current(request: Request) -> SessionView:
        token = request.cookies.get(COOKIE, "")
        scope = repo.resolve_scope(token)
        return SessionView(user_id=scope.user_id, role=scope.role, csrf_token=repo.csrf(token))

    @routes.delete("/api/session", status_code=204)
    def logout(request: Request) -> Response:
        service.logout(request.cookies.get(COOKIE, ""))
        response = Response(status_code=204)
        response.delete_cookie(COOKIE)
        return response

    return routes
