import os
from flask import Flask

from config import Config
from .services.db import init_db
from .routes.dashboard_routes import bp as dashboard_bp

def create_app():
    """
    Application factory for the crypto portfolio app.
    """
    # Initialize Flask app
    app = Flask(__name__, instance_relative_config=False)

    # Load configuration from Config class
    app.config.from_object(Config)

    # Initialize database (create tables if they don't exist)
    init_db()

    # Register blueprints
    app.register_blueprint(dashboard_bp, url_prefix="")

    return app