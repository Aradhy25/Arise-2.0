"""DeepGuard AI — FastAPI application entrypoint."""

from contextlib import asynccontextmanager

import app.ml.compat  # noqa: F401 — must run before torchvision imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, detect, history
from app.core.config import get_settings
from app.db import session as db_session
from app.db.models import Base
from app.ml.inference import get_engine
from app.schemas import HealthOut


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_settings()
    Base.metadata.create_all(bind=db_session.engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Deepfake detection API with dedicated Real/Fake inference and forensic reports.",
        lifespan=lifespan,
    )

    allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(auth.router, prefix="/api")
    app.include_router(detect.router, prefix="/api")
    app.include_router(history.router, prefix="/api")

    heatmaps = settings.upload_dir / "heatmaps"
    heatmaps.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/files/heatmaps", StaticFiles(directory=str(heatmaps)), name="heatmaps")
    app.mount("/files/reports", StaticFiles(directory=str(settings.reports_dir)), name="reports")

    @app.get("/api/health", response_model=HealthOut)
    @app.get("/healthz", response_model=HealthOut, include_in_schema=False)
    def health() -> HealthOut:
        try:
            eng = get_engine()
            model = eng.model_name
            device = str(eng.device)
            detector_loaded = eng.hf_detector is not None or eng.has_finetuned_weights
            if eng.hf_detector is not None:
                inference_mode = "huggingface-vit"
            elif eng.has_finetuned_weights:
                inference_mode = "pytorch"
            else:
                inference_mode = "forensic-heuristic"
            status = "ok" if detector_loaded else "degraded"
        except Exception:
            model = settings.default_model
            device = settings.device
            detector_loaded = False
            inference_mode = "unavailable"
            status = "degraded"
        return HealthOut(
            status=status,
            app=settings.app_name,
            version=settings.app_version,
            model=model,
            device=device,
            weights_loaded=detector_loaded,
            inference_mode=inference_mode,
        )

    @app.get("/")
    def root() -> dict:
        return {"app": settings.app_name, "docs": "/docs", "health": "/api/health", "frontend": "Streamlit on port 8501"}

    return app


app = create_app()
