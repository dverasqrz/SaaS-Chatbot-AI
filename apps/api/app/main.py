from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware


from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.chats import router as chats_router
from app.api.v1.workspaces import router as workspaces_router
from app.core.config import settings
from app.core.database_setup import setup_database
from app.models.workspace import Workspace  # noqa: F401


from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.workspace import Workspace  # noqa: F401

logger = logging.getLogger(__name__)

_DEFAULT_JWT_SECRET = "change-this-in-production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env == "production" and (
        settings.jwt_secret_key.get_secret_value() == _DEFAULT_JWT_SECRET
    ):
        logger.warning(
            "JWT_SECRET_KEY está com valor padrão. Defina um segredo forte em produção.",
        )
    setup_database()

    logger.info("Métricas Prometheus habilitadas em /metrics")
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="1.0.0",
    lifespan=lifespan,
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.cors_origins.split(",") if item.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}





from app.core.metrics_setup import setup_metrics

app.include_router(admin_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(workspaces_router, prefix="/api/v1")
app.include_router(chats_router, prefix="/api/v1")

setup_metrics(app)
