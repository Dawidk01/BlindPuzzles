# routes/history_route.py
from flask import render_template

from utils.db_helpers import get_user_attempts


USER_ID = 1


def history():
    """Wyświetla tabelę z historią prób użytkownika."""
    attempts = get_user_attempts()
    return render_template("history.html", attempts=attempts)
