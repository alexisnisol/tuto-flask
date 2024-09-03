from .app import app
from flask import render_template

@app.route("/")
def home():
    return render_template(
        "home.html",
        title="Hello World!",
        names=["Pierre", "Paul", "Corinne"])
