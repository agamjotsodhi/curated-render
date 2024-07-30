"""SQLAlchemy models for Curated."""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

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
    # search_histories = db.relationship('SearchHistory', backref='searched_user', cascade="all, delete-orphan")


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
    __tablename__ = 'artworks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    artist_display = db.Column(db.String, nullable=True)
    date_display = db.Column(db.String, nullable=True)
    classification_titles = db.Column(db.String, nullable=True)
    description= db.Column(db.Text, nullable=True)
    image_id = db.Column(db.String, nullable=True)
    api_link = db.Column(db.String, nullable=True)


class Theme(db.Model):
    __tablename__ = 'themes'
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String, unique=True, nullable=False)


class Favorite(db.Model):
    """Mapping a favorited artwork to user's profile"""

    __tablename__ = 'favorites'


    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id', ondelete="cascade"), nullable=False)
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)



class SearchHistory(db.Model):
    """Store all searches that user previously made"""
    
    __tablename__ = 'search_history'
    
    search_id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)
    search_term = db.Column(db.String, nullable=False)
    # timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # searched_user = db.relationship('User', backref='search_histories', lazy=True)

    @classmethod
    def save_history(cls, user_id, search_term):
        search_history = cls(user_id=user_id, search_term=search_term)
        db.session.add(search_history)
        db.session.commit()
    

def connect_db(app):
    """Connects this 'curated' database to the Flask app.py"""
    db.app = app
    db.init_app(app)
