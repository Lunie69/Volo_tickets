import os
import zipfile
import shutil
import os
import shutil
from flask import send_file
from openpyxl import Workbook
from io import BytesIO
from .ticket_manager import assign_tickets
from .zip_manager import extract_tickets
from .models import Volunteer, DownloadLog
from . import db
from .models import Volunteer

from werkzeug.utils import secure_filename

from config import Config

from .importer import import_excel
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    url_for
)

from .models import Admin

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        admin_user = Admin.query.filter_by(
            username=username
        ).first()

        if admin_user and admin_user.check_password(password):

            session["admin"] = True

            return redirect(url_for("admin.dashboard"))

        error = "Неверный логин или пароль."

    return render_template(
        "admin_login.html",
        error=error
    )


@admin.route("/")
def dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    total = Volunteer.query.count()

    downloaded = Volunteer.query.filter(
        Volunteer.downloads > 0
    ).count()

    not_downloaded = total - downloaded

    return render_template(
        "dashboard.html",
        total=total,
        downloaded=downloaded,
        not_downloaded=not_downloaded
    )

@admin.route("/upload", methods=["GET", "POST"])
def upload():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    if request.method == "POST":

        file = request.files["file"]

        if file.filename != "":

            filename = secure_filename(file.filename)

            path = os.path.join(
                Config.UPLOAD_FOLDER,
                filename
            )

            file.save(path)

            import_excel(path)

            return redirect(
                url_for("admin.dashboard")
            )

    return render_template("upload.html")

@admin.route("/new-event", methods=["GET", "POST"])
def new_event():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    message = None

    if request.method == "POST":

        excel = request.files["excel"]
        zip_file = request.files["zip"]

        if excel.filename == "" or zip_file.filename == "":
            message = "Выберите оба файла."
            return render_template(
                "new_event.html",
                message=message
            )

        # очищаем базу
        if request.form.get("clear"):

            DownloadLog.query.delete()
            Volunteer.query.delete()

            db.session.commit()

        # сохраняем excel
        excel_path = os.path.join(
            Config.UPLOAD_FOLDER,
            "volunteers.xlsx"
        )

        excel.save(excel_path)

        # сохраняем zip
        zip_path = os.path.join(
            Config.UPLOAD_FOLDER,
            "tickets.zip"
        )

        zip_file.save(zip_path)

        # импортируем людей
        import_excel(excel_path)

        # распаковываем pdf
        extract_tickets(
            zip_path,
            Config.TICKETS_FOLDER
        )

        # автоматически привязываем
        ok, text = assign_tickets(
            Config.TICKETS_FOLDER
        )

        message = text

    return render_template(
        "new_event.html",
        message=message
    )

@admin.route("/volunteers")
def volunteers():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    search = request.args.get("search", "").strip()

    page = request.args.get("page", 1, type=int)

    query = Volunteer.query

    if search:

        query = query.filter(
            (Volunteer.fullname.contains(search)) |
            (Volunteer.iin.contains(search))
        )

    pagination = query.order_by(
        Volunteer.fullname
    ).paginate(
        page=page,
        per_page=25,
        error_out=False
    )

    return render_template(
        "volunteers.html",
        volunteers=pagination.items,
        pagination=pagination,
        search=search
    )

@admin.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("admin.login")
    )

@admin.route("/logs")
def logs():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    logs = DownloadLog.query.order_by(
        DownloadLog.downloaded_at.desc()
    ).all()

    return render_template(
        "download_logs.html",
        logs=logs
    )

@admin.route("/volunteer/<int:volunteer_id>/edit", methods=["GET", "POST"])
def edit_volunteer(volunteer_id):

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    volunteer = Volunteer.query.get_or_404(volunteer_id)

    if request.method == "POST":

        volunteer.fullname = request.form["fullname"].strip()
        volunteer.iin = request.form["iin"].strip()
        volunteer.ticket_file = request.form["ticket"].strip()

        db.session.commit()

        return redirect(url_for("admin.volunteers"))

    return render_template(
        "edit_volunteer.html",
        volunteer=volunteer
    )


@admin.route("/volunteer/<int:volunteer_id>/delete")
def delete_volunteer(volunteer_id):

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    volunteer = Volunteer.query.get_or_404(volunteer_id)

    DownloadLog.query.filter_by(
        volunteer_id=volunteer.id
    ).delete()

    db.session.delete(volunteer)

    db.session.commit()

    return redirect(url_for("admin.volunteers"))

@admin.route("/volunteer/add", methods=["GET", "POST"])
def add_volunteer():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    if request.method == "POST":

        existing = Volunteer.query.filter_by(
            iin=request.form["iin"].strip()
        ).first()

        if existing:
            return "Волонтёр с таким ИИН уже существует."

        volunteer = Volunteer(
            fullname=request.form["fullname"].strip(),
            iin=request.form["iin"].strip(),
            ticket_file=request.form["ticket"].strip(),
        )

        db.session.add(volunteer)
        db.session.commit()

        return redirect(url_for("admin.volunteers"))

    return render_template(
        "add_volunteer.html"
    )

@admin.route("/export")
def export():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    wb = Workbook()
    ws = wb.active
    ws.title = "Волонтёры"

    ws.append([
        "ФИО",
        "ИИН",
        "Билет",
        "Скачиваний"
    ])

    volunteers = Volunteer.query.order_by(
        Volunteer.fullname
    ).all()

    for volunteer in volunteers:

        ws.append([
            volunteer.fullname,
            volunteer.iin,
            volunteer.ticket_file,
            volunteer.downloads
        ])

    output = BytesIO()

    wb.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="volunteers.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@admin.route("/tickets/upload", methods=["GET", "POST"])
def upload_tickets():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    if request.method == "POST":

        file = request.files.get("zipfile")

        if not file:
            return "Файл не выбран."

        temp_zip = os.path.join(
            Config.TEMP_FOLDER,
            "tickets.zip"
        )

        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
        os.makedirs(Config.TICKETS_FOLDER, exist_ok=True)

        file.save(temp_zip)

        # очищаем папку tickets
        shutil.rmtree(
            Config.TICKETS_FOLDER,
            ignore_errors=True
        )

        os.makedirs(Config.TICKETS_FOLDER)

        with zipfile.ZipFile(temp_zip) as zip_ref:
            zip_ref.extractall(Config.TICKETS_FOLDER)

        os.remove(temp_zip)

        return redirect(url_for("admin.ticket_status"))

    return render_template(
        "upload_tickets.html"
    )

@admin.route("/tickets/status")
def ticket_status():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    volunteers = Volunteer.query.count()

    pdfs = len([
        f for f in os.listdir(
            Config.TICKETS_FOLDER
        )
        if f.lower().endswith(".pdf")
    ])

    return render_template(
        "ticket_status.html",
        volunteers=volunteers,
        pdfs=pdfs
    )

@admin.route("/tickets/reset")
def reset_tickets():

    if not session.get("admin"):
        return redirect(url_for("admin.login"))

    volunteers = Volunteer.query.all()

    for volunteer in volunteers:
        volunteer.ticket_file = None
        volunteer.downloads = 0

    DownloadLog.query.delete()

    db.session.commit()

    return redirect(url_for("admin.dashboard"))