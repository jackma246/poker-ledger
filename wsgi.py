import os
from app import app, db
import json
from datetime import datetime
from sqlalchemy import text

def import_initial_data():
    """Import initial data if database is empty"""
    try:
        with app.app_context():
            # Check if database is empty
            result = db.session.execute(text("SELECT COUNT(*) FROM player"))
            player_count = result.fetchone()[0]
            
            if player_count == 0:
                print("🔄 Database is empty, importing initial data...")
                
                # Import players
                with open('database_export/players_20250828_184612.json', 'r') as f:
                    players_data = json.load(f)
                
                player_map = {}
                for player_data in players_data:
                    result = db.session.execute(text("""
                        INSERT INTO player (name, preferred_payment_method, payment_id)
                        VALUES (:name, :preferred_payment_method, :payment_id)
                        RETURNING id
                    """), {
                        'name': player_data['name'],
                        'preferred_payment_method': player_data['preferred_payment_method'],
                        'payment_id': player_data['payment_id']
                    })
                    player_id = result.fetchone()[0]
                    player_map[player_data['name']] = player_id
                    print(f"  ✅ Created player: {player_data['name']}")
                
                # Import ledger entries
                with open('database_export/ledger_entries_20250828_184612.json', 'r') as f:
                    ledger_data = json.load(f)
                
                for entry_data in ledger_data:
                    player_name = entry_data['player_name']
                    if player_name in player_map:
                        db.session.execute(text("""
                            INSERT INTO ledger_entry (player_id, game_date, net_profit, running_balance)
                            VALUES (:player_id, :game_date, :net_profit, :running_balance)
                        """), {
                            'player_id': player_map[player_name],
                            'game_date': entry_data['game_date'],
                            'net_profit': entry_data['net_profit'],
                            'running_balance': entry_data['running_balance']
                        })
                
                # Import payments
                with open('database_export/payments_20250828_184612.json', 'r') as f:
                    payments_data = json.load(f)
                
                for payment_data in payments_data:
                    player_name = payment_data['player_name']
                    if player_name in player_map:
                        db.session.execute(text("""
                            INSERT INTO payment (player_id, amount, payment_date, payment_method)
                            VALUES (:player_id, :amount, :payment_date, :payment_method)
                        """), {
                            'player_id': player_map[player_name],
                            'amount': payment_data['amount'],
                            'payment_date': payment_data['payment_date'],
                            'payment_method': payment_data['payment_method']
                        })
                
                db.session.commit()
                print(f"✅ Initial data imported: {len(players_data)} players, {len(ledger_data)} ledger entries, {len(payments_data)} payments")
            else:
                print(f"✅ Database already has {player_count} players, skipping import")
                
    except Exception as e:
        print(f"⚠️  Error during data import: {e}")

# Initialize database
with app.app_context():
    db.create_all()
    # Import data if running on Railway (production)
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        import_initial_data()

# Set application for Gunicorn
application = app
