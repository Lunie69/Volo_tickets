import os

from . import db
from .models import Volunteer


def assign_tickets(ticket_folder):
    """
    Автоматически привязывает PDF к волонтёрам.
    """

    volunteers = Volunteer.query.order_by(Volunteer.id).all()

    pdfs = [
        file for file in os.listdir(ticket_folder)
        if file.lower().endswith(".pdf")
    ]

    pdfs.sort()

    if len(volunteers) != len(pdfs):
        return False, (
            f"Количество волонтёров ({len(volunteers)}) "
            f"не совпадает с количеством PDF ({len(pdfs)})."
        )

    for volunteer, pdf in zip(volunteers, pdfs):
        volunteer.ticket_file = pdf

    db.session.commit()

    return True, "Все билеты успешно привязаны."