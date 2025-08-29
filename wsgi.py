import os
from app import app, db, Player, LedgerEntry, Payment
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
                    {"name": "Jacob"},
                    {"name": "Alex"},
                    {"name": "Sam"},
                    {"name": "Jordan"},
                    {"name": "Casey"},
                    {"name": "Taylor"},
                    {"name": "Morgan"},
                    {"name": "Riley"}
                ]
                
                for player_data in players_data:
                    player = Player(**player_data)
                    db.session.add(player)
                
                db.session.commit()
                print(f"Added {len(players_data)} players")
                
                # Create ledger entries (using correct field names)
                ledger_data = [
                    {"player_id": 1, "game_date": datetime(2024, 1, 15).date(), "net_profit": 30.0, "running_balance": 30.0},
                    {"player_id": 2, "game_date": datetime(2024, 1, 15).date(), "net_profit": 45.0, "running_balance": 45.0},
                    {"player_id": 3, "game_date": datetime(2024, 1, 15).date(), "net_profit": -15.0, "running_balance": -15.0},
                    {"player_id": 4, "game_date": datetime(2024, 1, 15).date(), "net_profit": 30.0, "running_balance": 30.0},
                    {"player_id": 5, "game_date": datetime(2024, 1, 15).date(), "net_profit": -10.0, "running_balance": -10.0},
                    {"player_id": 6, "game_date": datetime(2024, 1, 15).date(), "net_profit": 25.0, "running_balance": 25.0},
                    {"player_id": 7, "game_date": datetime(2024, 1, 15).date(), "net_profit": -25.0, "running_balance": -25.0},
                    {"player_id": 8, "game_date": datetime(2024, 1, 15).date(), "net_profit": 20.0, "running_balance": 20.0}
                ]
                
                for entry_data in ledger_data:
                    entry = LedgerEntry(**entry_data)
                    db.session.add(entry)
                
                db.session.commit()
                print(f"Added {len(ledger_data)} ledger entries")
                
                # Create payments (using correct field names)
                payments_data = [
                    {"player_id": 1, "amount": 30.0, "payment_date": datetime(2024, 1, 16).date(), "payment_method": "Venmo"},
                    {"player_id": 3, "amount": 15.0, "payment_date": datetime(2024, 1, 16).date(), "payment_method": "Cash"},
                    {"player_id": 5, "amount": 10.0, "payment_date": datetime(2024, 1, 17).date(), "payment_method": "Venmo"},
                    {"player_id": 7, "amount": 25.0, "payment_date": datetime(2024, 1, 17).date(), "payment_method": "Cash"}
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
