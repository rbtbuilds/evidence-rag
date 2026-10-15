import asyncio
import logging
import secrets
import time
from http.cookies import SimpleCookie
from uuid import uuid4

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

    def authorize(self, headers: Headers, path: str, method: str) -> None:
        if not path.startswith("/api/") or method == "OPTIONS":
            return
        parsed = SimpleCookie()
        parsed.load(headers.get("cookie", ""))
        morsel = parsed.get("evidence_session")
        token = morsel.value if morsel else ""
        current = self.repo.resolve_scope(token)
        if path.startswith("/api/admin/") and current.role != "maintainer":
            raise DomainError(403, "forbidden")
        if method in {"POST", "PUT", "PATCH", "DELETE"} and not secrets.compare_digest(
            headers.get("x-csrf-token", ""), self.repo.csrf(token)
        ):
            raise DomainError(403, "csrf_invalid")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        path, method = scope["path"], scope["method"]
        request_id = str(uuid4())
        start = time.perf_counter()
        started = False
        logged = False
        status = 500
        scope.setdefault("state", {})["request_id"] = request_id

        async def safe_send(message: Message) -> None:
            nonlocal started, logged, status
            if message["type"] == "http.response.start":
                started = True
                status = message["status"]
                message["headers"] = [
                    pair
                    for pair in message.get("headers", [])
                    if pair[0].lower() not in {b"cache-control", b"x-request-id"}
                ] + [
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-request-id", request_id.encode()),
                ]
            await send(message)
            if (
                message["type"] == "http.response.body"
                and not message.get("more_body", False)
                and not logged
            ):
                logged = True
                template = getattr(scope.get("route"), "path", "/unmatched")
                logging.getLogger("uvicorn.error").info(
                    "http_request route=%s status=%d request_id=%s duration_ms=%.2f",
                    template,
                    status,
                    request_id,
                    (time.perf_counter() - start) * 1000,
                )

        try:
            if headers.get("host") != "127.0.0.1:8115":
                raise DomainError(400, "invalid_host")
            mutable = method in {"POST", "PUT", "PATCH", "DELETE"}
            if (mutable or method == "OPTIONS") and headers.get("origin") != self.settings.origin:
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
                async with self.lock:
                    peer = str((scope.get("client") or ("unknown", 0))[0])
                    now = time.monotonic()
                    values = [v for v in self.attempts.get(peer, []) if now - v < 60]
                    if len(values) >= 5:
                        raise DomainError(429, "rate_limited")
                    self.attempts[peer] = values

                    async def login_send(message: Message) -> None:
                        if message["type"] == "http.response.start" and message["status"] in {
                            401,
                            422,
                        }:
                            self.attempts[peer].append(time.monotonic())
                        await safe_send(message)

                    await self.app(scope, bounded_receive, login_send)
            elif path == "/api/questions" and method == "POST":
                self.authorize(headers, path, method)
                await self.app(scope, bounded_receive, safe_send)
            else:
                async with self.lock:
                    self.authorize(headers, path, method)
                    await self.app(scope, bounded_receive, safe_send)
        except DomainError as error:
            await JSONResponse(error.payload(request_id), status_code=error.status)(
                scope, receive, safe_send
            )
        except Exception:  # noqa: BLE001 - never serialize untrusted input in an error.
            if started:
                raise RuntimeError("Response publication interrupted") from None
            error = DomainError(500, "internal_error")
            await JSONResponse(error.payload(request_id), status_code=500)(
                scope, receive, safe_send
            )
