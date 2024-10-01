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