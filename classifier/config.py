import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://hvac_user:securepassword@localhost:5432/hvacdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
