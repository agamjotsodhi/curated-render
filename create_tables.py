# create_tables.py
from app import app
from models import db

with app.app_context():
    db.create_all()
    print("Tables created successfully.")

# Run command in Terminal: 
#   python create_tables.py

