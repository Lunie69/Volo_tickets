from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Volunteer(db.Model):
    __tablename__ = "volunteers"

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    iin = db.Column(
        db.String(12),
        unique=True,
        nullable=False,
        index=True
    )

    ticket_file = db.Column(
        db.String(255),
        unique=True,
        nullable=True
    )

    downloads = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    def __repr__(self):
        return f"<Volunteer {self.fullname}>"


class DownloadLog(db.Model):
    __tablename__ = "download_logs"

    id = db.Column(db.Integer, primary_key=True)

    volunteer_id = db.Column(
        db.Integer,
        db.ForeignKey("volunteers.id"),
        nullable=False
    )

    ip_address = db.Column(
        db.String(100),
        nullable=False
    )

    downloaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    volunteer = db.relationship(
        "Volunteer",
        backref="download_logs"
    )


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )