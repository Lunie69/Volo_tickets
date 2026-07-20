from datetime import datetime
from . import db


class Volunteer(db.Model):
    __tablename__ = "volunteers"

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(255), nullable=False)
    iin = db.Column(db.String(12), unique=True, nullable=False)

    ticket_file = db.Column(db.String(255), nullable=False)

    downloads = db.Column(db.Integer, default=0)


class DownloadLog(db.Model):
    __tablename__ = "download_logs"

    id = db.Column(db.Integer, primary_key=True)

    volunteer_id = db.Column(
        db.Integer,
        db.ForeignKey("volunteers.id"),
        nullable=False
    )

    ip_address = db.Column(db.String(100))

    downloaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )