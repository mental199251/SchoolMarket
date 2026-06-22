from flask import g
from pymongo.errors import PyMongoError

from app.utils.response import error_response


def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_not_found(_error):
        return error_response(
            error_code="NOT_FOUND",
            message="请求的资源不存在",
            status_code=404,
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return error_response(
            error_code="METHOD_NOT_ALLOWED",
            message="请求方法不支持",
            status_code=405,
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(
            "Unhandled error, request_id=%s: %s",
            getattr(g, "request_id", "unknown"),
            error,
            exc_info=True,
        )
        return error_response(
            error_code="INTERNAL_ERROR",
            message="服务暂时不可用",
            status_code=500,
        )

    @app.errorhandler(PyMongoError)
    def handle_database_error(error):
        app.logger.warning(
            "Database operation failed, request_id=%s: %s",
            getattr(g, "request_id", "unknown"),
            error,
        )
        return error_response(
            error_code="DATABASE_UNAVAILABLE",
            message="数据库暂不可用",
            status_code=503,
        )
