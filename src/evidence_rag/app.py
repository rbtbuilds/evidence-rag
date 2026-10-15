from fastapi import FastAPI

from evidence_rag.config import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Evidence RAG", version="0.1.0")
    app.state.settings = settings

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "execution_profile": settings.profile}

    return app


def create_default_app() -> FastAPI:
    return create_app(Settings.from_env())
