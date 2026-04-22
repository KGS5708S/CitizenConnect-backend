import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret")
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
