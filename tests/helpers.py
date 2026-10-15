from dataclasses import dataclass, field

from fastapi.testclient import TestClient

from evidence_rag.contracts import Role
from evidence_rag.db.repository import Repository

ORIGIN = "http://127.0.0.1:5115"


@dataclass
class DemoHarness:
    client: TestClient
    repo: Repository
    credentials: dict[Role, dict[str, str]] = field(repr=False)

    def reader(self) -> dict[str, str]:
        return self.credentials["reader"]

    def maintainer(self) -> dict[str, str]:
        return self.credentials["maintainer"]


RESTRICTED_MARKERS = ("MAINTAINER-CAL-7391", "REPLACED-MARKER")


def disclosed_markers(text: str, role: Role, lifecycle: str) -> list[str]:
    forbidden = (
        RESTRICTED_MARKERS
        if role == "reader" or lifecycle == "deleted"
        else (RESTRICTED_MARKERS[0],)
        if lifecycle == "replaced"
        else ()
    )
    return [marker for marker in forbidden if marker in text]
