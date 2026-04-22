import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "sqlite:///database.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
