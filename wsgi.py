import os
from app import app, db
import json
from datetime import datetime
from sqlalchemy import text

# Initialize database tables
with app.app_context():
    db.create_all()

# For Gunicorn
application = app
