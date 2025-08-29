import os
from app import app, db

# Initialize database tables
with app.app_context():
    db.create_all()

# For Gunicorn
application = app