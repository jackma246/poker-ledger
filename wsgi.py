import os
import json
from datetime import datetime
from app import app, db, Player, LedgerEntry, Payment

def import_actual_data():
    """Import actual user data from exported JSON files"""
    try:
        # Only run if we're on Railway and have PostgreSQL
        if os.getenv('RAILWAY_ENVIRONMENT') == 'production' and os.getenv('DATABASE_URL'):
            print("Railway PostgreSQL detected - importing actual user data...")
            
            # Check if data already exists
            player_count = Player.query.count()
            if player_count == 0:
                print("Database is empty - importing data...")
                
                # Import players
                if os.path.exists('exported_players.json'):
                    with open('exported_players.json', 'r') as f:
                        players_data = json.load(f)
                    
                    for player_data in players_data:
                        # Convert datetime string back to datetime object
                        if player_data.get('created_at'):
                            player_data['created_at'] = datetime.fromisoformat(player_data['created_at'])
                        
                        player = Player(**player_data)
                        db.session.add(player)
                    
                    db.session.commit()
                    print(f"Imported {len(players_data)} players")
                
                # Import ledger entries
                if os.path.exists('exported_ledger.json'):
                    with open('exported_ledger.json', 'r') as f:
                        ledger_data = json.load(f)
                    
                    for entry_data in ledger_data:
                        # Convert date strings back to date objects
                        if entry_data.get('game_date'):
                            entry_data['game_date'] = datetime.fromisoformat(entry_data['game_date']).date()
                        if entry_data.get('created_at'):
                            entry_data['created_at'] = datetime.fromisoformat(entry_data['created_at'])
                        
                        entry = LedgerEntry(**entry_data)
                        db.session.add(entry)
                    
                    db.session.commit()
                    print(f"Imported {len(ledger_data)} ledger entries")
                
                # Import payments
                if os.path.exists('exported_payments.json'):
                    with open('exported_payments.json', 'r') as f:
                        payments_data = json.load(f)
                    
                    for payment_data in payments_data:
                        # Convert date strings back to date objects
                        if payment_data.get('payment_date'):
                            payment_data['payment_date'] = datetime.fromisoformat(payment_data['payment_date']).date()
                        if payment_data.get('created_at'):
                            payment_data['created_at'] = datetime.fromisoformat(payment_data['created_at'])
                        
                        payment = Payment(**payment_data)
                        db.session.add(payment)
                    
                    db.session.commit()
                    print(f"Imported {len(payments_data)} payments")
                
                print("Actual user data import completed successfully!")
            else:
                print(f"Database already has {player_count} players - skipping import")
            
    except Exception as e:
        print(f"Error during data import: {e}")

# Initialize database tables
with app.app_context():
    db.create_all()
    import_actual_data()

# For Gunicorn
application = app
