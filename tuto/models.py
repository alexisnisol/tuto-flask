#import yaml, os.path

#Books = yaml.safe_load(
#    open(os.path.join(
#        os.path.dirname(__file__),
#        "static/data.yml")))

from .app import db, login_manager
from flask_login import UserMixin

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return "Author (%d) %s" % (self.id, self.name)

class Favorite(db.Model):
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.username'), primary_key=True)
    books = db.relationship('Book', back_populates='favorites')
    users = db.relationship('User', back_populates='favorites')

genresDeLivres = db.Table(
    'genresDeLivres',
    db.Model.metadata,
    db.Column('genre', db.String(50), db.ForeignKey('genres.name')),
    db.Column('book', db.Integer, db.ForeignKey('book.id'))
)

class Genres(db.Model):
    name = db.Column(db.String(50), primary_key=True)
    books = db.relationship('Book', secondary=genresDeLivres, back_populates='genres')

    def __repr__(self):
        return self.name

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    url = db.Column(db.String(200))
    image = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', backref=db.backref('books', lazy='dynamic')) #dynamic => suppression en cascade etc.
    favorites = db.relationship('Favorite', back_populates='books')
    genres = db.relationship('Genres', secondary=genresDeLivres, back_populates='books')
    notes = db.relationship('Note', back_populates='book')

    def __repr__(self):
        return "<Book (%d) %s>" % (self.id, self.title)

class Note(db.Model):
    user_id = db.Column(db.String(50), db.ForeignKey('user.username'), primary_key=True)
    value = db.Column(db.Integer)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    book = db.relationship('Book', back_populates='notes')
    user = db.relationship('User', back_populates='notes')

def avg_note(book_id : int):
    """
    Return the average note of a book
    
    Parameters:
        book_id (int): the id of the book

    Returns:
        float: the average note of the book
    """
    notes = Note.query.filter_by(book_id=book_id).all()
    if len(notes) == 0:
        return None
    return sum([note.value for note in notes]) / len(notes)

def remove_book(id):
    b = Book.query.get(id)

    #remove all favorites for this book
    for fav in Favorite.query.filter_by(book_id=b.id).all():
        db.session.delete(fav)

    db.session.delete(b)
    db.session.commit()

def get_paginate(num_page):
    return Book.query.join(Author).order_by(Author.name).paginate(page=num_page, error_out=False, max_per_page=10)

def get_sample():
    return Book.query.all()

def get_author(id):
    return Author.query.get(id)

class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))
    favorites = db.relationship('Favorite', back_populates='users')
    notes = db.relationship('Note', back_populates='user')

    def get_id(self):
        return self.username
    
def add_user(username, password):
    u = User(username=username, password=password)
    db.session.add(u)
    db.session.commit()
    return u
    
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)