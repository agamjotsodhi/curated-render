"""SQLAlchemy models for Curated."""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import json

bcrypt = Bcrypt()
db = SQLAlchemy()

##########################################################################################################################################

class User(db.Model):
    """User in the application"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(130), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=True)
    image_url = db.Column(db.Text, default="static/images/default-img.jpg")

    favorites = db.relationship('Favorite', backref='user', cascade="all, delete-orphan")
    search_histories = db.relationship('SearchHistory', backref='searched_user', cascade="all, delete-orphan")

    @classmethod        
    def signup(cls, username, email, password, image_url, first_name):
        """Hashes user inputted password and adds to the database"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
            first_name=first_name,
            image_url=image_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):      
        """Check to see that login credentials exist/are correct"""
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return False


class Artwork(db.Model):
    """All data per each artwork """

    __tablename__ = 'artworks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    alt_titles = db.Column(db.String, nullable=True)
    artist_display = db.Column(db.String, nullable=True)
    date_start = db.Column(db.Integer, nullable=True)
    date_end = db.Column(db.Integer, nullable=True)
    date_display = db.Column(db.String, nullable=True)
    place_of_origin = db.Column(db.String, nullable=True)
    classification_titles = db.Column(db.String, nullable=True)
    edition = db.Column(db.String, nullable=True)
    color = db.Column(db.String, nullable=True)
    dimensions = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    image_id = db.Column(db.String, nullable=True)
    artwork_type_title = db.Column(db.String, nullable=True)
    api_link = db.Column(db.String, nullable=True)
    medium_display = db.Column(db.String, nullable=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=True)

    @classmethod
    def add_new_artwork(cls, data):
        """Adds a new artwork entry to records."""
        type_instance = Type.get_or_create(data.get('artwork_type_title'))  # Get or create the type
        
        # Convert color to JSON string if it's a dictionary
        color = json.dumps(data.get('color')) if isinstance(data.get('color'), dict) else data.get('color')
        
        # Handle possible missing fields with defaults
        artwork = cls(
            id=data['id'],
            title=data.get('title', 'Untitled'),
            alt_titles=data.get('alt_titles', None),
            artist_display=data.get('artist_display', 'Unknown Artist'),
            date_start=data.get('date_start', None),
            date_end=data.get('date_end', None),
            date_display=data.get('date_display', 'Unknown Date'),
            place_of_origin=data.get('place_of_origin', 'Unknown Place'),
            classification_titles=', '.join(data.get('classification_titles', [])),
            edition=data.get('edition', 'Unknown Edition'),
            color=color,
            dimensions=data.get('dimensions', 'Unknown Dimensions'),
            description=data.get('description', 'No Description Available'),
            image_id=data.get('image_id', None),
            artwork_type_title=data.get('artwork_type_title', 'Unknown Type'),
            api_link=data.get('api_link', None),
            medium_display=data.get('medium_display', 'Unknown Medium'),
            type=type_instance
        )
        db.session.merge(artwork)
        db.session.commit()
        
        return artwork


class Type(db.Model):
    """Artwork types in the application - to sort artworks by the same art type"""

    __tablename__ = 'types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    
    artworks = db.relationship('Artwork', backref='type', lazy=True)

    @classmethod
    def get_or_create(cls, name):
        """Get an existing type or create a new one if it does not exist."""
        type_instance = cls.query.filter_by(name=name).first()
        if not type_instance:
            type_instance = cls(name=name)
            db.session.add(type_instance)
            db.session.commit()
        return type_instance
    
    def get_artwork_ids(self):
        """Get all artwork IDs for this type."""
        return [artwork.id for artwork in self.artworks]

class Favorite(db.Model):
    """Mapping a favorited artwork to user's profile"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id', ondelete="cascade"), nullable=False)

    # Define the relationship to Artwork
    artwork = db.relationship('Artwork', backref='favorites')

class SearchHistory(db.Model):
    """Store all searches that user previously made"""

    __tablename__ = 'search_history'

    search_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)
    search_term = db.Column(db.String, nullable=False)
    
    @classmethod
    def save_history(cls, user_id, search_term):
        """Save a search term to the search history."""
        search_history = cls(user_id=user_id, search_term=search_term)
        db.session.add(search_history)
        db.session.commit()


def connect_db(app):
    """Connects this 'curated' database to the Flask app.py"""
    db.app = app
    db.init_app(app)
