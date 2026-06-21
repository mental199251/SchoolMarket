from uuid import uuid4

from flask import g, request


def register_request_context(app):
    @app.before_request
    def attach_request_id():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid4())

    @app.after_request
    def expose_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        return response

