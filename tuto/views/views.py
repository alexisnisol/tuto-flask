"""All functions that are called when a route is accessed are defined here."""
from flask import render_template, url_for, redirect, request
from flask_wtf.file import FileRequired
from flask_login import login_user, current_user, logout_user, login_required
from tuto.models import (
    get_author, Book, Author, Favorite, Genres, get_paginate, remove_book, Note, avg_note
)
from tuto.app import app, db, mkpath
from tuto.views.forms import BookForm, AuthorForm, LoginForm, AdvancedSearchForm, GenreForm

@app.route("/")
def home():
    """Route vers la page d'accueil.
    """
    return redirect(url_for("books"))

@app.route("/books")
def books():
    """Route vers la liste des livres.
    """

    num_page = request.args.get('page', 1, type=int)

    les_livres_favoris = []
    if current_user.is_authenticated:
        les_favoris = Favorite.query.filter_by(user_id=current_user.username).all()
        les_livres_favoris = [fav.books for fav in les_favoris]

    pagination = get_paginate(num_page)
    return render_template(
        "home.html",
        title="",
        books=pagination.items,
        pagination=pagination,
        favorites=les_livres_favoris
        )

@app.route("/add/book")
@login_required
def add_book():
    """Route vers l'ajout d'un nouveau livre.
    """
    f = BookForm()
    return render_template("books/add_book.html", form=f)

@app.route("/save/book", methods=["POST"])
@login_required
def save_book():
    """Route vers la sauvegarde d'un livre.
    Si le formulaire est valide, le livre est ajouté à la base de données.
    """
    b = None
    f = BookForm()
    f.image.validators.append(FileRequired())
    if f.validate_on_submit():
        a = Author.query.get(f.author.data)
        b = Book(
            price=f.price.data,
            url=f.url.data,
            image=f.image.data.filename,
            title=f.title.data,
            author_id= a.id)
        f.image.validators.pop()

        for genre in f.genres.data:
            g = Genres.query.filter_by(name=genre).first()
            b.genres.append(g)

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

@app.route("/favorite/<id>")
@login_required
def favorite_book(id):
    """Route vers l'ajout d'un livre en favori.
    """
    b = Book.query.get(int(id))

    #check if user has already favorited the book
    fav = Favorite.query.filter_by(book_id=b.id, user_id=current_user.username).first()
    if fav:
        db.session.delete(fav)
    else:
        fav = Favorite(
            book_id=b.id,
            user_id=current_user.username)
        db.session.add(fav)

    db.session.commit()
    return redirect(url_for("books"))

@app.route("/detail/<id>", methods=["GET", "POST"])
@login_required
def detail(id):
    """Route vers les détails d'un livre.
    """
    book = Book.query.get(int(id))

    #check if user has already favorited the book
    fav = Favorite.query.filter_by(book_id=book.id, user_id=current_user.username).first()

    note = avg_note(book.id)
    if request.method == "POST":
        note_donne = request.form.get("note")
        if note_donne:
            note_donne = int(note_donne)
            n = Note(
                user_id=current_user.username,
                value=note_donne,
                book_id=book.id
            )
            db.session.add(n)
            db.session.commit()

        suppr_note = request.form.get("suppr_note")
        if suppr_note:
            n = Note.query.filter_by(user_id=current_user.username, book_id=book.id).first()
            db.session.delete(n)
            db.session.commit()

        note = avg_note(book.id)

    note_donne = Note.query.filter_by(user_id=current_user.username, book_id=book.id).first()
    if note_donne:
        note_donne = note_donne.value
    return render_template(
        "books/detail.html",
        book=book,
        is_favorite=fav is not None,
        note=note,
        note_donne=note_donne
        )

@app.route("/edit/book/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):
    """Route vers l'édition d'un livre.
    Accessible en méthode GET et POST.
    En méthode GET, le formulaire est pré-rempli avec les informations du livre à modifier (id).
    En méthode POST, les informations du livre sont mises à jour dans la base de données.

    Args:
        id (int): Identifiant du livre à modifier
    """
    b = Book.query.get(id)
    f = BookForm()
    f.set_choices(Author.query.all())

    if f.validate_on_submit():
        b.title = f.title.data
        b.price = f.price.data
        b.author_id = f.author.data
        b.url = f.url.data
        b.genres.clear()
        for genre in f.genres.data:
            g = Genres.query.filter_by(name=genre).first()
            b.genres.append(g)

        # si il y une nouvelle image
        if f.image.data:
            b.image = f.image.data.filename

        db.session.commit()
        return redirect(url_for("books"))

    f = BookForm(
        id=b.id,
        title=b.title,
        genres=[g.name for g in b.genres],
        price=b.price,
        author=b.author_id,
        url=b.url
    )
    return render_template("books/edit_book.html", book=b, form=f)

@app.route("/delete/book/<int:id>")
@login_required
def delete_book(id):
    """Route vers la suppression d'un livre.

    Args:
        id (int): Identifiant du livre à supprimer
    """
    remove_book(id)
    return redirect(url_for("books"))

@app.route("/authors")
@login_required
def authors():
    """Route vers la liste des auteurs.
    """
    return render_template("authors/author.html", authors=Author.query.all())

@app.route("/add/author")
@login_required
def add_author():
    """Route vers l'ajout d'un auteur.
    """
    f = AuthorForm()
    return render_template("authors/add_author.html", form=f)

@app.route("/edit/author/<int:id>")
@login_required
def edit_author(id):
    """Route vers l'édition d'un auteur.

    Args:
        id (int): Identifiant de l'auteur à modifier
    """
    a = get_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    les_livres = Book.query.filter_by(author_id = a.id)
    return render_template("authors/edit_author.html", author=a, form=f, books = les_livres)

def delete_author():
    """
    Supprime un auteur de la base de données.
    Cette fonction est appelée lors de la soumission du formulaire de suppression d'un auteur.
    """
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
    """Route vers la sauvegarde d'un auteur.

    Accessible en méthode POST.
    
    Si le formulaire est valide,
        - si l'utilisateur a cliqué sur le bouton "Supprimer" : 
                l'auteur est supprimé de la base de données
        - sinon, l'utilisateur a cliqué sur le bouton "Enregistrer" :
            - si l'auteur existe déjà, il est mis à jour dans la base de données    
            - sinon, un nouvel auteur est ajouté à la base de données
    """
    a = None
    f = AuthorForm()
    if f.validate_on_submit():
        if request.form.get("action") == "Supprimer":
            return delete_author()

        if f.id.data: #Modification de l'auteur existant
            id = int(f.id.data)
            a = get_author(id)
            a.name = f.name.data
            db.session.commit()
            return redirect(url_for("edit_author", id=id))
        else: #Ajout d'un nouvel auteur
            a = Author()
            a.name = f.name.data
            db.session.add(a)
            db.session.commit()
            return redirect(url_for("authors"))

    a = get_author(int(f.id.data))
    return render_template("authors/edit_author.html", author=a, form=f)

@app.route("/login/", methods=["GET", "POST"])
def login():
    """Route vers la page d'autentification.
    Accessible en méthode GET et POST.
    En méthode GET, affiche le formulaire de connexion.
    En méthode POST, vérifie les informations de connexion
        et redirige vers la page d'accueil ou vers la redirection,
        si les informations sont correctes.
    """
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for('home')
            return redirect(next)
    #appelé avec get (donc on rentre l'url /login/) => affiche le formulaire de login,
    #si on soumet le formulaire (post), on vérifie les données, si elles sont correctes,
    # on redirige vers la page d'accueil (car le validate_on_submit() est vrai)
    return render_template("login.html", form=f)

@app.route("/logout/")
def logout():
    """Route vers la déconnexion.
    """
    logout_user()
    return redirect(url_for('home'))

@app.route("/search")
def search():
    """
    route vers la fonctionnalité de recherche
    d'un livre par nom
    """
    nom_livre = request.args.get("query")
    # les livres filtrés par nom
    # session.query(TableName).filter(TableName.colName.ilike(f'%{search_text}%')).all()
    # copilot : apply above line on avariable names les_livres
    les_livres = Book.query.filter(Book.title.ilike(f'%{nom_livre}%')).all()
    les_livres_favoris = []
    # récupération des livres favoris
    if current_user.is_authenticated:
        les_favoris = Favorite.query.filter_by(user_id=current_user.username).all()
        for fav in les_favoris:
            book = fav.books
            if nom_livre in book.title:
                les_livres_favoris.append(book)
    # la template
    return render_template(
        "books/searched_name.html",
        title = "Recherche par nom : \n" + nom_livre,
        books = les_livres,
        favorites = les_livres_favoris
        )

@app.route("/advanced_search", methods=["GET", "POST"])
def advanced_search():
    """
    route vers la fonctionnalité de recherche avancée
    """
    f = AdvancedSearchForm()
    f.set_choices(Author.query.all())
    if f.validate_on_submit():
        # récupération des données
        title = f.title.data
        author = f.author.data
        price_min = f.price_min.data
        price_max = f.price_max.data
        # les livres filtrés
        les_livres = Book.query
        if title:
            les_livres = les_livres.filter(Book.title.ilike(f'%{title}%'))
        if author != "":
            les_livres = les_livres.filter(Book.author_id == author)
        if price_min:
            les_livres = les_livres.filter(Book.price >= price_min)
        if price_max:
            les_livres = les_livres.filter(Book.price <= price_max)
        les_livres = les_livres.all()
        # les livres favoris
        les_livres_favoris = []
        if current_user.is_authenticated:
            les_favoris = Favorite.query.filter_by(user_id=current_user.username).all()
            for fav in les_favoris:
                book = fav.books
                if title in book.title:
                    les_livres_favoris.append(book)
        # la template
        return render_template(
            "books/advanced_search.html",
            title = "Recherche avancée",
            books = les_livres,
            favorites = les_livres_favoris,
            form = f
            )
    return render_template("books/advanced_search.html", form=f)


@app.route("/genres")
def genres():
    """
    route vers la liste des genres
    """
    return render_template("genres/genres.html", genres=Genres.query.all())

@app.route("/genre/add", methods=["GET", "POST"])
def add_genre():
    """
    route vers la fonctionnalité d'ajout d'un genre
    """
    f = GenreForm()
    # si le formulaire est valide, on ajoute le genre à la base de données
    if f.validate_on_submit():
        genre = Genres(name=f.name.data)
        db.session.add(genre)
        db.session.commit()
        return redirect(url_for("genres"))
    return render_template("genres/add_genre.html", form=f)
