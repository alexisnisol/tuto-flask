from .app import app
from flask import render_template
from .models import get_books


@app.route("/")
def home():
    return "<h1>Hello World!</h1>"

@app.route("/names")
def show_names():
    return render_template(
        "home.html",
        title="Hello World!",
        names=["Pierre", "Paul", "Corinne"])

@app.route("/livres")
def show_livres():
    return render_template(
        "livres.html",
        title="Livres d'Amazon !",
        books=get_books())