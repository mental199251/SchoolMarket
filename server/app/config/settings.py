import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_origins(value):
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class BaseConfig:
    SERVICE_NAME = "school-market-api"
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = _as_int(os.getenv("FLASK_PORT"), 5001)
    DEBUG = False
    TESTING = False

    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://127.0.0.1:27017/?directConnection=true",
    )
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "school_market")
    MONGO_TIMEOUT_MS = _as_int(os.getenv("MONGO_TIMEOUT_MS"), 2000)

    CORS_ORIGINS = _as_origins(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-school-market-secret")
    JWT_EXPIRES_SECONDS = _as_int(os.getenv("JWT_EXPIRES_SECONDS"), 7 * 24 * 60 * 60)
    PASSWORD_MIN_LENGTH = _as_int(os.getenv("PASSWORD_MIN_LENGTH"), 8)
    UPLOAD_FOLDER = str((ROOT_DIR / os.getenv("UPLOAD_FOLDER", "server/uploads")).resolve())
    MAX_CONTENT_LENGTH = _as_int(os.getenv("MAX_CONTENT_LENGTH"), 10 * 1024 * 1024)
    UPLOAD_IMAGE_MAX_BYTES = _as_int(
        os.getenv("UPLOAD_IMAGE_MAX_BYTES"),
        5 * 1024 * 1024,
    )
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    OLLAMA_CONNECT_TIMEOUT_SECONDS = _as_int(
        os.getenv("OLLAMA_CONNECT_TIMEOUT_SECONDS"),
        3,
    )
    OLLAMA_RESPONSE_TIMEOUT_SECONDS = _as_int(
        os.getenv("OLLAMA_RESPONSE_TIMEOUT_SECONDS"),
        20,
    )


class DevelopmentConfig(BaseConfig):
    DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), True)


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    MONGO_TIMEOUT_MS = 50


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
