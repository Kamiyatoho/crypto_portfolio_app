from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Importer l'usine à application
from app import create_app
# Importer le blueprint Binance (au cas où create_app ne l'enregistre pas automatiquement)
from app.routes.binance_routes import bp as binance_bp

# Créer l'application
app = create_app()

# Enregistrer le blueprint Binance sous le préfixe /api/binance
app.register_blueprint(binance_bp, url_prefix="/api/binance")

if __name__ == "__main__":
    # Mode debug si FLASK_DEBUG est défini à true dans l'environnement
    debug = os.getenv("FLASK_DEBUG", "true").lower() in ("1", "true", "yes")
    # Port configurable via la variable d'environnement PORT
    port = int(os.getenv("PORT", 5000))
    # Lancer le serveur sur toutes les interfaces
    app.run(host="0.0.0.0", port=port, debug=debug)