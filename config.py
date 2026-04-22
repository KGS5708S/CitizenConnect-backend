import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    @staticmethod
    def get_database_uri():
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            return db_url.replace("postgres://", "postgresql://", 1)
        return "sqlite:///database.db"
    SQLALCHEMY_DATABASE_URI = get_database_uri()
