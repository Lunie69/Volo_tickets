from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
    abort
)
from sqlalchemy import func
import os
from sqlalchemy import select
from .models import Volunteer, DownloadLog
from . import db
from config import Config

routes = Blueprint("routes", __name__)


@routes.route("/", methods=["GET", "POST"])
def index():

    volunteer = None
    error = None

    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()
        iin = request.form.get("iin", "").strip()

        if not fullname or not iin:
            error = "Заполните все поля."

        else:

            volunteer = Volunteer.query.filter(
                func.lower(func.trim(Volunteer.fullname)) == fullname.lower().strip(),
                Volunteer.iin == iin
            ).first()

            if not volunteer:
                error = "Пользователь не найден."

    return render_template(
        "index.html",
        volunteer=volunteer,
        error=error
    )


@routes.route("/download/<int:volunteer_id>")
def download(volunteer_id):
    volunteer = db.session.get(Volunteer, volunteer_id)

    if volunteer is None:
        abort(404)

    import os

    # Если билет еще не назначен — назначаем автоматически
    if volunteer.ticket_file is None:

        # Все PDF
        all_pdfs = sorted(
            f for f in os.listdir(Config.TICKETS_FOLDER)
            if f.lower().endswith(".pdf")
        )

        # Уже использованные PDF
        used = {
            v.ticket_file
            for v in Volunteer.query.with_entities(Volunteer.ticket_file).all()
            if v.ticket_file
        }

        # Ищем первый свободный
        free_ticket = None

        for pdf in all_pdfs:
            if pdf not in used:
                free_ticket = pdf
                break

        if free_ticket is None:
            abort(500, "Свободные билеты закончились.")

        volunteer.ticket_file = free_ticket
        db.session.commit()

    if not volunteer.ticket_file:

        # Повторно получаем запись с блокировкой
        volunteer = (
            db.session.execute(
                select(Volunteer)
                .where(Volunteer.id == volunteer.id)
                .with_for_update()
            )
            .scalar_one()
        )

        # Пока ждали блокировку, билет уже могли выдать
        if not volunteer.ticket_file:

            import os

            used = {
                v.ticket_file
                for v in Volunteer.query.all()
                if v.ticket_file
            }

            pdfs = sorted([
                f for f in os.listdir(Config.TICKETS_FOLDER)
                if f.lower().endswith(".pdf")
            ])

            free_pdf = None

            for pdf in pdfs:
                if pdf not in used:
                    free_pdf = pdf
                    break

            if free_pdf is None:
                abort(404)

            volunteer.ticket_file = free_pdf

        db.session.commit()

    volunteer.downloads += 1

    log = DownloadLog(
        volunteer_id=volunteer.id,
        ip_address=request.remote_addr
    )

    db.session.add(log)
    db.session.commit()

    return send_from_directory(
        Config.TICKETS_FOLDER,
        volunteer.ticket_file,
        as_attachment=True
    )