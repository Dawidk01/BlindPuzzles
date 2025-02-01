# routes/home_route.py

from flask import render_template

def home():
    """Strona główna"""
    return render_template("home.html")
