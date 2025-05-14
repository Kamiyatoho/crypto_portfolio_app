import os
from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Binance API credentials
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

    # Flask secret key (for sessions, CSRF, etc.)
    SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(24)

    # Debug mode
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

    # Database (SQLite by default, stored in project root)
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'portfolio.db')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(basedir, DATABASE_NAME)}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False