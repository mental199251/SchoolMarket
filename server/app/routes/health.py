from flask import Blueprint, current_app
from pymongo.errors import PyMongoError

from app.utils.response import error_response, success_response


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return success_response(
        data={
            "service": current_app.config["SERVICE_NAME"],
            "status": "healthy",
        },
        message="服务运行正常",
    )


@health_bp.get("/ready")
def ready():
    try:
        current_app.extensions["mongo"].ping()
    except (PyMongoError, TimeoutError, OSError) as exc:
        current_app.logger.warning("MongoDB readiness check failed: %s", exc)
        return error_response(
            error_code="DATABASE_UNAVAILABLE",
            message="数据库暂不可用",
            status_code=503,
        )

    return success_response(
        data={
            "service": current_app.config["SERVICE_NAME"],
            "status": "ready",
            "dependencies": {"mongodb": "ready"},
        },
        message="服务已就绪",
    )
