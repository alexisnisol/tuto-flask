import click
from .app import app, db

@app.cli.command()#ajoute une commande
@click.argument('filename')#ajoute un argument
def loaddb(filename):
    '''Creates the tables and populates them with data.'''

    # création de toutes les tables
    db.create_all()

    # chargement de notre jeu de données
    import yaml
    books = yaml.safe_load(open(filename))

    # import des modèles
    from .models import Book, Author

    # première passe : création de tous les auteurs
    authors = {}
    for b in books:
        a = b["author"]
        if a not in authors:
            o = Author(name=a)
            db.session.add(o)
            authors[a] = o
    db.session.commit()

    # deuxième passe : création de tous les livres
    for b in books:
        a = authors[b["author"]]
        o = Book(
            price=b["price"],
            url=b["url"],
            image=b["img"],
            title=b["title"],
            author_id= a.id)
        db.session.add(o)
    db.session.commit()

@app.cli.command()
def syncdb():
    '''Creates all missing tables.'''
    db.create_all()

@app.cli.command()
@click.argument('username')
@click.argument('password')
def newuser(username, password):
    '''Adds a new user.'''
    from .models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = User(username=username, password=m.hexdigest())
    db.session.add(u)
    db.session.commit()

@app.cli.command()
@click.argument('username')
@click.argument('password')
def passwd(username, password):
    '''Changes the password of a user.'''
    from .models import User, load_user
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = load_user(username)
    u.password = m.hexdigest()
    db.session.commit()


@app.cli.command()
@click.argument('name')
def newgenre(name):
    '''Adds a new genre.'''
    from .models import Genres
    g = Genres(name=name)
    db.session.add(g)
    db.session.commit()


@app.cli.command()
@click.argument('id_book')
@click.argument('nom_genre')
def setgenre(id_book, nom_genre):
    '''Adds a genre to a book.'''
    from .models import Book, Genres
    g = Genres.query.get(nom_genre)
    b = Book.query.get(id_book)
    b.genres.append(g)
    db.session.commit()