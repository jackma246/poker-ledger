import os
from app import app, db, Player, LedgerEntry, Payment, GameHistory
import json
from datetime import datetime
from sqlalchemy import text

def import_initial_data():
    """Import initial data if database is empty"""
    try:
        # Check if we're on Railway and if player table is empty
        if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
            player_count = Player.query.count()
            if player_count == 0:
                print("Railway production environment detected - importing initial data...")
                
                # Import players
                players_data = [
                    {"name": "Jacob", "email": "jacob@example.com"},
                    {"name": "Alex", "email": "alex@example.com"},
                    {"name": "Sam", "email": "sam@example.com"},
                    {"name": "Jordan", "email": "jordan@example.com"},
                    {"name": "Casey", "email": "casey@example.com"},
                    {"name": "Taylor", "email": "taylor@example.com"},
                    {"name": "Morgan", "email": "morgan@example.com"},
                    {"name": "Riley", "email": "riley@example.com"}
                ]
                
                for player_data in players_data:
                    player = Player(**player_data)
                    db.session.add(player)
                
                db.session.commit()
                print(f"Added {len(players_data)} players")
                
                # Import ledger entries
                ledger_data = [
                    {"player_id": 1, "amount": 50.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 2, "amount": 75.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 3, "amount": 100.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 4, "amount": 25.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 5, "amount": 60.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 6, "amount": 40.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 7, "amount": 80.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 8, "amount": 30.0, "description": "Buy-in", "date": datetime(2024, 1, 15)},
                    {"player_id": 1, "amount": -20.0, "description": "Cash out", "date": datetime(2024, 1, 15)},
                    {"player_id": 2, "amount": 45.0, "description": "Winnings", "date": datetime(2024, 1, 15)},
                    {"player_id": 3, "amount": -15.0, "description": "Cash out", "date": datetime(2024, 1, 15)},
                    {"player_id": 4, "amount": 30.0, "description": "Winnings", "date": datetime(2024, 1, 15)},
                    {"player_id": 5, "amount": -10.0, "description": "Cash out", "date": datetime(2024, 1, 15)},
                    {"player_id": 6, "amount": 25.0, "description": "Winnings", "date": datetime(2024, 1, 15)},
                    {"player_id": 7, "amount": -25.0, "description": "Cash out", "date": datetime(2024, 1, 15)},
                    {"player_id": 8, "amount": 20.0, "description": "Winnings", "date": datetime(2024, 1, 15)}
                ]
                
                for entry_data in ledger_data:
                    entry = LedgerEntry(**entry_data)
                    db.session.add(entry)
                
                db.session.commit()
                print(f"Added {len(ledger_data)} ledger entries")
                
                # Import payments
                payments_data = [
                    {"player_id": 1, "amount": 30.0, "date": datetime(2024, 1, 16), "description": "Venmo payment"},
                    {"player_id": 3, "amount": 15.0, "date": datetime(2024, 1, 16), "description": "Cash payment"},
                    {"player_id": 5, "amount": 10.0, "date": datetime(2024, 1, 17), "description": "Venmo payment"},
                    {"player_id": 7, "amount": 25.0, "date": datetime(2024, 1, 17), "description": "Cash payment"}
                ]
                
                for payment_data in payments_data:
                    payment = Payment(**payment_data)
                    db.session.add(payment)
                
                db.session.commit()
                print(f"Added {len(payments_data)} payments")
                
                print("Initial data import completed successfully!")
                
    except Exception as e:
        print(f"Error during data import: {e}")

# Initialize database tables
with app.app_context():
    db.create_all()
    import_initial_data()

# For Gunicorn
application = app
