"""Module contenant les formulaires de l'application"""
from hashlib import sha256
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, HiddenField, PasswordField, SelectField, DecimalField, SelectMultipleField, URLField
)
from wtforms.validators import DataRequired, Optional
from tuto.models import Author, Genres, User, add_user

class AuthorForm(FlaskForm):
    """Formulaire pour la gestion des auteurs
    """
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])

class BookForm(FlaskForm):
    """Formulaire pour la gestion des livres

    Attributes:
        id (HiddenField): Identifiant du livre
        title (StringField): Titre du livre
        price (DecimalField): Prix du livre
        author (SelectField): Auteur du livre (liste déroulante des auteurs de la base de données)
        url (StringField): URL du livre (lien vers la page amazon, fnac, ...)
        image (FileField): Image de couverture du livre
    """
    id = HiddenField('id')
    title = StringField('Titre', validators=[DataRequired()])
    genres = SelectMultipleField('Genre', validators=[Optional()])
    price = DecimalField('Prix', validators=[DataRequired()])
    author = SelectField('Auteur', choices=[], validators=[DataRequired()])
    url = URLField('URL', validators=[DataRequired()])
    image = FileField('image', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.set_genres(Genres.query.all())
        self.set_choices(Author.query.all())

    def set_genres(self, genres):
        """Définit les genres disponibles dans le formulaire

        Args:
            genres (list): Liste des genres disponibles
        """
        self.genres.choices = [("", "Aucun")] + [(g.name, g.name) for g in genres]

    def set_choices(self, authors):
        """Définit les auteurs disponibles dans le formulaire

        Args:
            authors (list): Liste des auteurs disponibles
        """
        self.author.choices = [(a.id, a.name) for a in authors]

class AdvancedSearchForm(FlaskForm):
    """Formulaire de recherche avancée
    """
    title = StringField('Titre',
                        render_kw={"placeholder": "(optionnel) Entrez le titre du livre"},
                        validators=[Optional()])

    author = SelectField('Auteur',
                         choices=[],
                         default=None,
                         validators=[Optional()])

    price_min = DecimalField('Prix Min',
                             render_kw={"placeholder": "(optionnel) Prix minimum"},
                             validators=[Optional()])

    price_max = DecimalField('Prix Max',
                             render_kw={"placeholder": "(optionnel) Prix maximum"},
                             validators=[Optional()])

    genre = SelectField('Genre',
                        choices=[],
                        default=None,
                        validators=[Optional()])

    def set_choices(self):
        """Définit les auteurs disponibles dans le formulaire

        Args:
            authors (list): Liste des auteurs disponibles
        """
        self.author.choices = [("", "Aucun")] + [(a.id, a.name) for a in Author.query.all()]
        self.genre.choices = [("", "Aucun")] + [(g.name, g.name) for g in Genres.query.all()]

class LoginForm(FlaskForm):
    """Formulaire de connexion
    
    Attributes:
        username (StringField): Nom d'utilisateur
        password (PasswordField): Mot de passe
        next (HiddenField): Page de redirection après connexion
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    next = HiddenField('next')

    def get_authenticated_user(self):
        """Vérifie si l'utilisateur existe et si le mot de passe est correct

        Returns:
            User: Utilisateur connecté si les informations sont correctes, None sinon
        """
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None
    
    def create_user(self):
        """Crée un utilisateur dans la base de données à partir des informations du formulaire,
        si l'utilisateur n'existe pas déjà

        Returns:
            Boolean: True si l'utilisateur a été créé, False sinon
        """
        user = User.query.get(self.username.data)
        if user is None:
            m = sha256()
            m.update(self.password.data.encode())
            return add_user(self.username.data, m.hexdigest())
        return None
class GenreForm(FlaskForm):
    """Formulaire pour la gestion des genres
    """
    name = StringField('Nom', validators=[DataRequired()])
