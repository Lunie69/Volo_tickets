import pandas as pd

from . import db
from .models import Volunteer


def import_excel(filepath):
    df = pd.read_excel(filepath)

    Volunteer.query.delete()

    for _, row in df.iterrows():
        volunteer = Volunteer(
            fullname=str(row["fullname"]).strip(),
            iin=str(row["iin"]).strip(),
        )

        db.session.add(volunteer)

    db.session.commit()