import os
from app import app, db
from sqlalchemy import text

def fix_sequences():
    """Fix PostgreSQL sequences to match current data"""
    try:
        # Fix player sequence
        result = db.session.execute(text("SELECT MAX(id) FROM player"))
        max_player_id = result.scalar()
        if max_player_id:
            db.session.execute(text(f"SELECT setval('player_id_seq', {max_player_id})"))
            print(f"Fixed player sequence to start from {max_player_id + 1}")
        
        # Fix ledger_entry sequence
        result = db.session.execute(text("SELECT MAX(id) FROM ledger_entry"))
        max_ledger_id = result.scalar()
        if max_ledger_id:
            db.session.execute(text(f"SELECT setval('ledger_entry_id_seq', {max_ledger_id})"))
            print(f"Fixed ledger_entry sequence to start from {max_ledger_id + 1}")
        
        # Fix payment sequence
        result = db.session.execute(text("SELECT MAX(id) FROM payment"))
        max_payment_id = result.scalar()
        if max_payment_id:
            db.session.execute(text(f"SELECT setval('payment_id_seq', {max_payment_id})"))
            print(f"Fixed payment sequence to start from {max_payment_id + 1}")
        
        db.session.commit()
        print("All sequences fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing sequences: {e}")
        db.session.rollback()

# Initialize database tables
with app.app_context():
    db.create_all()
    # Fix sequences to prevent duplicate key errors
    fix_sequences()

# For Gunicorn
application = app
