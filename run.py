from app import create_app, db
from app.models import Admin

app = create_app()

with app.app_context():

    if not Admin.query.filter_by(username="admin").first():

        admin = Admin(username="admin")

        admin.set_password("123456")

        db.session.add(admin)
        db.session.commit()

        print("Администратор создан.")

    else:

        print("Администратор уже существует.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)