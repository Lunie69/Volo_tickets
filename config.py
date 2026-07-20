import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    TICKETS_FOLDER = os.path.join(BASE_DIR, "tickets")

    TEMP_FOLDER = os.path.join(BASE_DIR, "temp")