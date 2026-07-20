from app import create_app, db
from app.models import Volunteer

app = create_app()

with app.app_context():

    volunteer = Volunteer(
        fullname="Иванов Иван Иванович",
        iin="123456789012",
        ticket_file="ticket001.pdf"
    )

    db.session.add(volunteer)
    db.session.commit()

    print("Готово")