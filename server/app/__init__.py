import os

from flask import Flask

from app.config.settings import CONFIGS
from app.extensions import init_extensions
from app.middleware.request_context import register_request_context
from app.routes.health import health_bp
from app.utils.errors import register_error_handlers


def create_app(config_name=None, config_overrides=None):
    app = Flask(__name__)

    selected_config = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(CONFIGS.get(selected_config, CONFIGS["development"]))

    if config_overrides:
        app.config.update(config_overrides)

    app.json.ensure_ascii = False
    app.json.sort_keys = False

    init_extensions(app)
    register_request_context(app)
    register_error_handlers(app)
    app.register_blueprint(health_bp)

    return app
