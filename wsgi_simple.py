import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
from functools import wraps

# Create Flask app
app = Flask(__name__)

# Basic configuration without config module
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///poker_ledger.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Admin configuration
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required for this action.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Database Models
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    preferred_payment_method = db.Column(db.String(50), nullable=True)
    payment_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ledger_entries = db.relationship('LedgerEntry', backref='player', lazy=True)
    payments = db.relationship('Payment', backref='player', lazy=True)

class LedgerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    net_profit = db.Column(db.Float, default=0.0)
    running_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('player_id', 'game_date', name='_player_game_uc'),)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LedgerHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(100), nullable=False)
    final_balance = db.Column(db.Float, nullable=False)
    cleared_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Import routes from app.py
from app import *

# Initialize database tables
with app.app_context():
    db.create_all()

# For Gunicorn
application = app
