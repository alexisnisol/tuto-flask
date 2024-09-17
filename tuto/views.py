from .app import app
from flask import render_template
from .models import get_sample


@app.route("/")
def home():
    return "<h1>Hello World!</h1>"

@app.route("/names")
def show_names():
    return render_template(
        "home.html",
        title="Hello World!",
        books=get_sample())

@app.route("/detail/<id>")
def detail(id):
    books = get_sample()
    book = books[int(id)]
    return render_template("detail.html", book=book)
