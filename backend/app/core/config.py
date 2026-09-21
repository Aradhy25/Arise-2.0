"""Application settings for DeepGuard AI."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DeepGuard AI"
    app_version: str = "1.1.0"
    debug: bool = False

    # Auth
    secret_key: str = "deepguard-dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Database — configure DATABASE_URL in backend/.env for MySQL.
    # SQLite remains the fallback for isolated tests/development only.
    database_url: str = "sqlite:///./deepguard.db"

    # Storage
    upload_dir: Path = Path(__file__).resolve().parents[2] / "uploads"
    weights_dir: Path = Path(__file__).resolve().parents[2] / "weights"
    reports_dir: Path = Path(__file__).resolve().parents[2] / "reports"
    max_upload_mb: int = 100

    # Inference
    default_model: str = "efficientnet"
    image_size: int = 224
    max_video_frames: int = 40
    fake_threshold: float = 0.5
    device: str = "cpu"

    # Dedicated deepfake detector. This avoids treating ImageNet classifier
    # heads as deepfake detectors. A local fine-tuned checkpoint can be used
    # explicitly after it has been trained and validated for this architecture.
    detector_backend: str = "huggingface"
    hf_model_id: str = "dima806/deepfake_vs_real_image_detection"
    use_local_checkpoint: bool = False
    document_model_id: str = "zodumair/document-forgery-detector"
    audio_model_id: str = "Vansh180/deepfake-audio-wav2vec2"
    max_document_pages: int = 8
    enable_audio_model: bool = True
    enable_document_model: bool = True
    video_audio_visual_weight: float = 0.70
    video_audio_weight: float = 0.30

    # CORS — comma-separated trusted origins. Configure HTTPS localhost for secure local UI.
    cors_origins: str = "https://localhost:8501,http://localhost:8501,http://localhost:5173,http://localhost:3000,http://127.0.0.1:8501,http://127.0.0.1:5173"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.weights_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    return settings
