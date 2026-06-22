import os

from flask import Flask

from app.config.settings import CONFIGS
from app.extensions import init_extensions
from app.middleware.request_context import register_request_context
from app.routes.admin import admin_bp
from app.routes.announcements import announcements_bp
from app.routes.auth import auth_bp
from app.routes.categories import categories_bp
from app.routes.health import health_bp
from app.routes.messages import messages_bp
from app.routes.products import products_bp
from app.routes.trades import trades_bp
from app.routes.uploads import uploads_bp
from app.routes.users import users_bp
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
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(announcements_bp, url_prefix="/api/v1/announcements")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(categories_bp, url_prefix="/api/v1/categories")
    app.register_blueprint(messages_bp, url_prefix="/api/v1/messages")
    app.register_blueprint(products_bp, url_prefix="/api/v1/products")
    app.register_blueprint(trades_bp, url_prefix="/api/v1/trades")
    app.register_blueprint(uploads_bp)
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")

    return app
