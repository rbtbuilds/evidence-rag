import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Profile = Literal["fixture", "local"]


@dataclass(frozen=True)
class Settings:
    root: Path
    profile: Profile = "fixture"
    origin: str = "http://127.0.0.1:5115"

    @property
    def database(self) -> Path:
        return self.root / "evidence.sqlite3"

    @classmethod
    def from_env(cls) -> "Settings":
        profile = os.getenv("EVIDENCE_PROFILE", "fixture")
        if profile not in ("fixture", "local"):
            raise ValueError("EVIDENCE_PROFILE must be fixture or local")
        return cls(Path(os.getenv("EVIDENCE_HOME", ".runtime")).resolve(), profile)
