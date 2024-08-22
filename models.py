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

    id = db.Column(db.Integer, primary_key=True)  # Primary key of the user
    username = db.Column(db.String(50), unique=True, nullable=False)  # Username of the user
    password = db.Column(db.String(130), nullable=False)  # Hashed password of the user
    email = db.Column(db.String(75), nullable=False, unique=True)  # Email of the user
    first_name = db.Column(db.String, nullable=True)  # First name of the user
    image_url = db.Column(db.Text, default="static/images/default-img.jpg")  # URL of the user's profile image

    # Relationships to the User:
    favorites = db.relationship('Favorite', backref='user', cascade="all, delete-orphan")
    search_histories = db.relationship('SearchHistory', backref='searched_user', cascade="all, delete-orphan")

    # User class methods:
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

    id = db.Column(db.Integer, primary_key=True)  # Primary key - artwork id
    title = db.Column(db.String, nullable=False)  # Artwork title
    alt_titles = db.Column(db.String, nullable=True)  # Alternative titles
    artist_display = db.Column(db.String, nullable=True)  # Artist display name of artwork
    date_start = db.Column(db.Integer, nullable=True)  # Artwork start date
    date_end = db.Column(db.Integer, nullable=True)  # Artword end date
    date_display = db.Column(db.String, nullable=True)  # Display date of the artwork
    place_of_origin = db.Column(db.String, nullable=True)  # Place of origin of the artwork
    classification_titles = db.Column(db.String, nullable=True)  # Classification titles of the artwork
    edition = db.Column(db.String, nullable=True)  # Artwork edition
    color = db.Column(db.String, nullable=True)  # HSL color codes used in artwork
    dimensions = db.Column(db.String, nullable=True)  # Size and dimensions of work
    description = db.Column(db.String, nullable=True)  # Description of the artwork
    image_id = db.Column(db.String, nullable=True)  # Image ID of the artwork
    artwork_type_title = db.Column(db.String, nullable=True)  # Artwork type - category of work
    api_link = db.Column(db.String, nullable=True)  # API link for the artwork
    medium_display = db.Column(db.String, nullable=True)  # Medium display of the artwork
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=True)  # Foreign key to the type

    @classmethod
    def add_new_artwork(cls, data):
        """Adds a new artwork entry to records."""
        type_instance = Type.get_or_create(data.get('artwork_type_title'))  # Get or create the type
        
        # Convert color (HSL color codes) to JSON string if it's a dictionary
        color = json.dumps(data.get('color')) if isinstance(data.get('color'), dict) else data.get('color')
        
        # Create the artwork entry
        artwork = cls(
            id=data['id'],
            title=data['title'],
            alt_titles=data.get('alt_titles'),
            artist_display=data.get('artist_display'),
            date_start=data.get('date_start'),
            date_end=data.get('date_end'),
            date_display=data.get('date_display'),
            place_of_origin=data.get('place_of_origin'),
            classification_titles=', '.join(data.get('classification_titles', [])),
            edition=data.get('edition'),
            color=color,
            dimensions=data.get('dimensions'),
            description=data.get('description'),
            image_id=data.get('image_id'),
            artwork_type_title=data.get('artwork_type_title'),
            api_link=data.get('api_link'),
            medium_display=data.get('medium_display'),
            type=type_instance  # Associate with the type
        )
        db.session.merge(artwork)
        db.session.commit()
        
        return artwork


class Type(db.Model):
    """Artwork types in the application - to sort artworks by the same art type"""

    __tablename__ = 'types'

    id = db.Column(db.Integer, primary_key=True)  # Primary key of the type
    name = db.Column(db.String, nullable=False, unique=True)  # Name of the type
    
    artworks = db.relationship('Artwork', backref='type', lazy=True)  # Relationship to artworks of this type

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

    id = db.Column(db.Integer, primary_key=True)  # Primary key of the favorite
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)  # Foreign key to the user
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id', ondelete="cascade"), nullable=False)  # Foreign key to the artwork
    artwork = db.relationship('Artwork', backref='favorites', lazy=True)



class SearchHistory(db.Model):
    """Store all searches that user previously made"""

    __tablename__ = 'search_history'

    search_id = db.Column(db.Integer, primary_key=True)  # Primary key of the search history
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)  # Foreign key to the user
    search_term = db.Column(db.String, nullable=False)  # The search term used by the user
    
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
