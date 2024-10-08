from .app import app, db
from flask import render_template, url_for, redirect, request
from .models import get_author, get_sample, Book, Author, User
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, PasswordField
from wtforms.validators import DataRequired
from hashlib import sha256
from flask_login import login_user, current_user, logout_user

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')

    def get_authenticated_user(self):
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None
    
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
    #books = get_sample()
    #book = books[int(id)]
    book = Book.query.get(int(id))
    return render_template("detail.html", book=book)

@app.route("/edit/author/<int:id>")
def edit_author(id):
    a = get_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template("edit_author.html", author=a, form=f)

@app.route("/save/author", methods=["POST"])
def save_author():
    a = None
    f = AuthorForm()

    if f.validate_on_submit():
        id = int(f.id.data)
        a = get_author(id)
        a.name = f.name.data
        db.session.commit()
        return redirect(url_for("edit_author", id=id))
    a = get_author(int(f.id.data))
    return render_template("edit_author.html", author=a, form=f)

@app.route("/login/", methods=("GET", "POST", ))
def login():
    f = LoginForm()
    if f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            return redirect(url_for("show_names"))
    return render_template("login.html", form=f) #appelé avec gate (donc on rentre l'url /login/) => affiche le formulaire de login,
                                                #si on soumet le formulaire (post), on vérifie les données, si elles sont correctes, 
                                                # on redirige vers la page d'accueil (car le validate_on_submit() est vrai)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))