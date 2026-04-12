
import logging

from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette_prometheus import PrometheusMiddleware

from app.core.config import settings
from app.core.metrics import set_app_info

logger = logging.getLogger(__name__)

def setup_metrics(app: FastAPI):
    """
    Configura o middleware e os endpoints para métricas Prometheus.
    """
    # Middleware de métricas Prometheus (deve vir antes do CORS)
    app.add_middleware(PrometheusMiddleware)

    @app.get("/metrics")
    def metrics():
        """Endpoint para Prometheus coletar métricas."""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    set_app_info(version="1.0.0", environment=settings.app_env)
    logger.info("Métricas Prometheus habilitadas em /metrics")
