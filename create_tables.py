# create_tables.py

from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env

from app import app
from models import db

with app.app_context():
    db.create_all()
    print("Tables created successfully.")
