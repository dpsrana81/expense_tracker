import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


def _env(name, default=None):
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value


class Config:
    SECRET_KEY = _env("SECRET_KEY", "change-this-to-a-random-secret-key-at-least-32-chars")
    JWT_SECRET_KEY = _env("JWT_SECRET_KEY", "change-this-to-a-random-jwt-secret-key-at-least-32-chars")

    # Database: defaults to local SQLite for easy setup, override with
    # DATABASE_URL for MySQL / AWS RDS, e.g.
    # mysql+pymysql://user:password@host:3306/expense_tracker
    SQLALCHEMY_DATABASE_URI = _env(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, '..', 'instance', 'expense_tracker.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT stored in httpOnly cookies so the browser based dashboard can use it
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_COOKIE_SECURE = _env("JWT_COOKIE_SECURE", "False") == "True"
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # File uploads (receipts) - stored locally by default,
    # set USE_S3=True with AWS credentials for production
    UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

    USE_S3 = _env("USE_S3", "False") == "True"
    AWS_S3_BUCKET = _env("AWS_S3_BUCKET", "")
    AWS_REGION = _env("AWS_REGION", "us-east-1")

    CORS_ORIGINS = _env("CORS_ORIGINS", "*")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
