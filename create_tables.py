"""   Create_tables.py
  
- Create PSQL Tables script
- To run application with database:
- Open Terminal
- Type in:  python create_tables.py """

from app import app
from models import db

with app.app_context():
    db.create_all()
    print("Tables created successfully.")



