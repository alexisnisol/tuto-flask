from .app import app, db, mkpath
from flask import render_template, url_for, redirect, request
from .models import get_author, get_sample, Book, Author, User
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, PasswordField, SelectField, DecimalField
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from wtforms.validators import DataRequired
from hashlib import sha256
from flask_login import login_user, current_user, logout_user, login_required

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])

class BookForm(FlaskForm):

    id = HiddenField('id')
    title = StringField('Titre', validators=[DataRequired()])
    price = DecimalField('Prix', validators=[DataRequired()])
    author = SelectField('Auteur', choices=[], validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])

    def set_choices(self, authors):
        self.author.choices = [(a.id, a.name) for a in authors]

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

@app.route("/add/book")
@login_required
def add_book():
    f = BookForm()
    f.set_choices(Author.query.all())
    return render_template("books/add_book.html", form=f)

@app.route("/save/book", methods=["POST"])
@login_required
def save_book():
    b = None
    f = BookForm()
    f.set_choices(Author.query.all())
    if f.validate_on_submit():
        #if f.id.data:
        #    id = int(f.id.data)
        #    a = get_author(id)
        #    a.name = f.name.data
        #    db.session.commit()
        #    return redirect(url_for("edit_author", id=id))
        #else:
        a = Author.query.get(f.author.data)
        b = Book(
            price=f.price.data,
            url=f.url.data,
            image=f.image.data.filename,
            title=f.title.data,
            author_id= a.id)
    
        #add image to static folder
        try:

            db.session.add(b)
            db.session.commit()

            image_data = f.image.data

            # Save the received frame as an image
            with open(mkpath(f'static/images/{image_data.filename}'), 'wb') as file:
                file.write(image_data.read())
            return books()
        except Exception as e:
            return f"Erreur: {e}"
    
        
    
    return render_template("books/add_book.html", form=f)
    
@app.route("/detail/<id>")
@login_required
def detail(id):
    #books = get_sample()
    #book = books[int(id)]
    book = Book.query.get(int(id))
    return render_template("books/detail.html", book=book)

@app.route("/edit/book/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):
    b = Book.query.get(id)
    f = BookForm()
    f.set_choices(Author.query.all())
    
    if f.validate_on_submit():
        b.title = f.title.data
        b.price = f.price.data
        b.author_id = f.author.data
        b.url = f.url.data
        db.session.commit()
        return redirect(url_for("books"))
    
    f = BookForm(
        id=b.id,
        title=b.title,
        price=b.price,
        author=b.author_id,
        url=b.url)
    
    return render_template("books/edit_book.html", book=b, form=f)

@app.route("/delete/book/<int:id>")
@login_required
def delete_book(id):
    b = Book.query.get(id)
    db.session.delete(b)
    db.session.commit()
    return redirect(url_for("books"))

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

def delete_author():
    a = None
    f = AuthorForm()
    if f.validate_on_submit():
        a = get_author(int(f.id.data))

        for b in a.books:
            db.session.delete(b)

        db.session.delete(a)
        db.session.commit()
        return redirect(url_for("authors"))
    return redirect(url_for("add_author"))

@app.route("/save/author", methods=["POST"])
@login_required
def save_author():
    a = None
    f = AuthorForm()
    if f.validate_on_submit():
        if request.form.get("action") == "Supprimer":
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


#request.args.get('query')