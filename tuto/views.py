from .app import app, db
from flask import render_template, url_for, redirect, request
from .models import get_author, get_sample, Book, Author, User
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, PasswordField
from wtforms.validators import DataRequired
from hashlib import sha256
from flask_login import login_user, current_user, logout_user, login_required

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    next = HiddenField('next')

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
    return render_template(
        "home.html",
        title="Page d'accueil",
        books=[])

@app.route("/books")
def books():
        return render_template("home.html", title="", books=get_sample())

@app.route("/detail/<id>")
@login_required
def detail(id):
    #books = get_sample()
    #book = books[int(id)]
    book = Book.query.get(int(id))
    return render_template("books/detail.html", book=book)

@app.route("/authors")
@login_required
def authors():
    return render_template("authors/author.html", authors=Author.query.all())

@app.route("/add/author")
@login_required
def add_author():
    f = AuthorForm()
    return render_template("authors/add_author.html", form=f)

@app.route("/edit/author/<int:id>")
@login_required
def edit_author(id):
    a = get_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template("authors/edit_author.html", author=a, form=f)

@app.route("/delete/author", methods=["POST"])
@login_required
def delete_author():
    a = None
    f = AuthorForm()
    print(f.id.data)
    if f.validate_on_submit():
        a = get_author(int(f.id.data))
        db.session.delete(a)
        db.session.commit()
        print("ok")
        return redirect(url_for("authors"))
    print("error")
    return redirect(url_for("add_author"))

@app.route("/save/author", methods=["POST"])
def save_author():

    a = None
    f = AuthorForm()

    print("a")
    if f.validate_on_submit():
        print(request.args)
        if request.form.get("submit") == "Supprimer":
            print("c")
            return delete_author()

        if f.id.data:
            id = int(f.id.data)
            a = get_author(id)
            a.name = f.name.data
            db.session.commit()
            return redirect(url_for("edit_author", id=id))
        else:
            a = Author()
            a.name = f.name.data
            db.session.add(a)
            db.session.commit()
            return redirect(url_for("authors"))
    
    a = get_author(int(f.id.data))
    return render_template("authors/edit_author.html", author=a, form=f)

@app.route("/login/", methods=("GET", "POST", ))
def login():
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for('home')
            return redirect(next)
    return render_template("login.html", form=f) #appelé avec get (donc on rentre l'url /login/) => affiche le formulaire de login,
                                                #si on soumet le formulaire (post), on vérifie les données, si elles sont correctes, 
                                                # on redirige vers la page d'accueil (car le validate_on_submit() est vrai)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))