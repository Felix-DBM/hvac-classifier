import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        # hier den kurzen Dialekt + client_encoding
        "postgresql://hvac_user:M31052003wd@localhost:5432/hvacdb?client_encoding=utf8"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
