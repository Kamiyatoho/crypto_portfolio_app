import os
from flask import Flask
from app.services.db import init_db
from app.routes.dashboard_routes import bp as dashboard_bp

def create_app():
    # 1. Initialize local database/tables
    init_db()

    # 2. Create Flask application
    app = Flask(__name__)

    # 3. Load configuration (e.g. DATABASE_URL, BINANCE_API_KEY/SECRET, etc.)
    #    You can define defaults in config.py and override via env-vars.
    app.config.from_object("config")

    # 4. Register your dashboard blueprint
    app.register_blueprint(dashboard_bp)

    return app

app = create_app()

if __name__ == "__main__":
    # Debug on by default; bind to localhost:5000 (or override via PORT env-var)
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host=host, port=port)