import asyncio
import secrets
import time

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from evidence_rag.config import Settings
from evidence_rag.db.repository import Repository
from evidence_rag.errors import DomainError


class Guard:
    def __init__(
        self, app: ASGIApp, settings: Settings, repo: Repository, publication_lock: asyncio.Lock
    ) -> None:
        self.app, self.settings, self.repo, self.lock = app, settings, repo, publication_lock
        self.attempts: dict[str, list[float]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        path, method = scope["path"], scope["method"]

        async def safe_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(
                    [(b"cache-control", b"no-store"), (b"x-content-type-options", b"nosniff")]
                )
            await send(message)

        try:
            if headers.get("host") != "127.0.0.1:8115":
                raise DomainError(400, "invalid_host")
            mutable = method in {"POST", "PUT", "PATCH", "DELETE"}
            if mutable and headers.get("origin") != self.settings.origin:
                raise DomainError(
                    403, "forbidden", "Request origin is not the local web application."
                )
            body = bytearray()
            if mutable:
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    body.extend(message.get("body", b""))
                    if len(body) > 269 * 1024:
                        raise DomainError(413, "limit_exceeded")
                    if not message.get("more_body", False):
                        break
            delivered = False

            async def bounded_receive() -> Message:
                nonlocal delivered
                if not delivered and mutable:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            if path == "/api/session" and method == "POST":
                peer = str((scope.get("client") or ("unknown", 0))[0])
                now = time.monotonic()
                values = [v for v in self.attempts.get(peer, []) if now - v < 60]
                if len(values) >= 5:
                    raise DomainError(429, "rate_limited")
                self.attempts[peer] = values
                original_send = safe_send

                async def login_send(message: Message) -> None:
                    if message["type"] == "http.response.start" and message["status"] in {401, 422}:
                        self.attempts[peer].append(time.monotonic())
                    await original_send(message)

                async with self.lock:
                    await self.app(scope, bounded_receive, login_send)
                return
            elif path.startswith("/api/"):
                cookies = headers.get("cookie", "")
                from http.cookies import SimpleCookie

                parsed = SimpleCookie()
                parsed.load(cookies)
                morsel = parsed.get("evidence_session")
                token = morsel.value if morsel else ""
                current = self.repo.resolve_scope(token)
                if path.startswith("/api/admin/") and current.role != "maintainer":
                    raise DomainError(403, "forbidden")
                if mutable and not secrets.compare_digest(
                    headers.get("x-csrf-token", ""), self.repo.csrf(token)
                ):
                    raise DomainError(403, "csrf_invalid")
            if path == "/api/questions":
                await self.app(scope, bounded_receive, safe_send)
            else:
                async with self.lock:
                    await self.app(scope, bounded_receive, safe_send)
        except DomainError as error:
            await JSONResponse(error.payload(), status_code=error.status)(scope, receive, safe_send)
