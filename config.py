import os
from datetime import timedelta

class Config:
    """App configuration supporting three modes:
    - PostgreSQL when DATABASE_URL is set (production)
    - MySQL only when explicitly requested via USE_MYSQL=1 (local/XAMPP)
    - SQLite fallback by default (no external DB required)
    """

    # Secret key for session management
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    USE_MYSQL = os.environ.get('USE_MYSQL', '0') == '1'

    if DATABASE_URL:
        # Production: Use PostgreSQL-style URL
        # Some providers use 'postgres://' but SQLAlchemy expects 'postgresql://'
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif USE_MYSQL:
        # Explicit MySQL (requires PyMySQL installed)
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
        MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'serve_at_ease')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )
    else:
        # Default: SQLite file (no external DB). Path lives in the repo directory.
        base_dir = os.path.abspath(os.path.dirname(__file__))
        sqlite_path = os.path.join(base_dir, 'serve_at_ease.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path}"

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # File upload configuration
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
