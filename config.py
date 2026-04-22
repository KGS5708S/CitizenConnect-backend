class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:Postgres%40123@localhost:5432/citizenconnect"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super-secret-key"

