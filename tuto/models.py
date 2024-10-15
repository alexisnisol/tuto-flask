#import yaml, os.path

#Books = yaml.safe_load(
#    open(os.path.join(
#        os.path.dirname(__file__),
#        "static/data.yml")))

#i = 0
#for book in Books:
    #book['id'] = i
    #i += 1

#def get_books():
 #   return Books


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


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    url = db.Column(db.String(200))
    image = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', backref=db.backref('books', lazy='dynamic')) #dynamic => suppression en cascade etc.
    favorites = db.relationship('Favorite', back_populates='books')

    def __repr__(self):
        return "<Book (%d) %s>" % (self.id, self.title)

def get_sample():
    return Book.query.all()

def get_author(id):
    return Author.query.get(id)

class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))
    favorites = db.relationship('Favorite', back_populates='users')

    def get_id(self):
        return self.username
    
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)