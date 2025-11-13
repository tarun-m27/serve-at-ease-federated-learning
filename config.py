import os
from datetime import timedelta

class Config:
    """Application configuration for local (MySQL) and production (PostgreSQL)"""

    # Secret key for session management
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

    # Database configuration - supports both PostgreSQL (Render) and MySQL (local)
    # Render provides DATABASE_URL environment variable for PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Production: Use PostgreSQL from Render
        # Render uses 'postgres://' but SQLAlchemy needs 'postgresql://'
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local development: Use MySQL with XAMPP
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
        MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'serve_at_ease')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )

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
