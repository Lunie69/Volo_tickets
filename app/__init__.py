from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager

db = SQLAlchemy()
# login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    # login_manager.init_app(app)

    from .routes import routes

    app.register_blueprint(routes)
    from .admin import admin

    app.register_blueprint(admin)

    with app.app_context():
        from . import models
        db.create_all()

    return app