from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from sqlalchemy import text

from app.core.config import Settings, get_settings
from app.core.errors import install_error_handlers
from app.db.base import Base
from app.db.session import create_database_engine, create_session_factory
from app.modules.analysis.router import router as analysis_router
from app.modules.devices.router import router as devices_router
from app.modules.imports.router import router as imports_router
from app.modules.knowledge.router import router as knowledge_router
from app.modules.maintenance.router import router as maintenance_router
from app.modules.reports.router import router as reports_router
from app.services.llm.providers import build_provider


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        resolved.data_dir.mkdir(parents=True, exist_ok=True)
        engine = create_database_engine(resolved.database_url)
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
        app.state.llm_provider = build_provider(resolved)
        Base.metadata.create_all(engine)
        yield
        engine.dispose()

    app = FastAPI(
        title="AI Hospital Operations Platform",
        version="0.1.0",
        description="Demo-first hospital equipment operations, RAG, analysis, and reporting API",
        lifespan=lifespan,
    )
    app.state.settings = resolved
    install_error_handlers(app)

    api = APIRouter(prefix="/api/v1")

    @api.get("/health", tags=["health"])
    def health(request: Request) -> dict[str, object]:
        with request.app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        demo = request.app.state.settings.app_env == "demo"
        return {
            "service": request.app.state.settings.app_name,
            "status": "healthy",
            "mode": request.app.state.settings.app_env,
            "dependencies": {
                "database": "ready",
                "cache": "disabled" if demo else "unavailable",
                "vector_store": "local" if demo else "unavailable",
                "llm": "ready" if demo else "unavailable",
                "model_service": "disabled" if demo else "unavailable",
            },
        }

    api.include_router(devices_router)
    api.include_router(maintenance_router)
    api.include_router(imports_router)
    api.include_router(knowledge_router)
    api.include_router(analysis_router)
    api.include_router(reports_router)
    app.include_router(api)
    return app


app = create_app()
