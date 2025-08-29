import os
from app import app, db, Player, LedgerEntry, Payment, GameHistory
from datetime import datetime

def run_migration_if_needed():
    """Run migration if we're on Railway with PostgreSQL and no data exists"""
    try:
        # Only run if we're on Railway and have PostgreSQL
        if os.getenv('RAILWAY_ENVIRONMENT') == 'production' and os.getenv('DATABASE_URL'):
            player_count = Player.query.count()
            if player_count == 0:
                print("Railway PostgreSQL detected - running initial migration...")
                
                # Create players
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
                
                # Create ledger entries
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
                
                # Create payments
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
                
                print("Migration completed successfully!")
                
    except Exception as e:
        print(f"Error during migration: {e}")

# Initialize database tables
with app.app_context():
    db.create_all()
    run_migration_if_needed()

# For Gunicorn
application = app
