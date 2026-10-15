from uuid import uuid4


class DomainError(Exception):
    def __init__(self, status: int, code: str, message: str | None = None) -> None:
        self.status = status
        self.code = code
        self.message = message or code.replace("_", " ").capitalize()
        super().__init__(self.message)

    def payload(self, request_id: str | None = None) -> dict[str, dict[str, str]]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "request_id": request_id or str(uuid4()),
            }
        }
