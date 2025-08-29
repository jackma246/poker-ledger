#!/usr/bin/env python3
"""
Standalone script to import data directly into Railway production database
"""
import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration for Railway
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///poker_ledger.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"🔗 Connecting to database: {DATABASE_URL}")

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def import_data():
    print("🔄 Starting data import...")
    
    try:
        # Clear existing data
        print("🗑️  Clearing existing data...")
        session.execute(text("DELETE FROM payment"))
        session.execute(text("DELETE FROM ledger_entry"))
        session.execute(text("DELETE FROM player"))
        session.execute(text("DELETE FROM ledger_history"))
        session.commit()
        print("✅ Database cleared")
        
        # Import players
        print("📥 Importing players...")
        with open('database_export/players_20250828_184612.json', 'r') as f:
            players_data = json.load(f)
        
        player_map = {}
        for player_data in players_data:
            result = session.execute(text("""
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
        print("📥 Importing ledger entries...")
        with open('database_export/ledger_entries_20250828_184612.json', 'r') as f:
            ledger_data = json.load(f)
        
        for entry_data in ledger_data:
            player_name = entry_data['player_name']
            if player_name in player_map:
                session.execute(text("""
                    INSERT INTO ledger_entry (player_id, game_date, net_profit, running_balance)
                    VALUES (:player_id, :game_date, :net_profit, :running_balance)
                """), {
                    'player_id': player_map[player_name],
                    'game_date': entry_data['game_date'],
                    'net_profit': entry_data['net_profit'],
                    'running_balance': entry_data['running_balance']
                })
                print(f"  ✅ Added ledger entry: {player_name} on {entry_data['game_date']}")
        
        # Import payments
        print("📥 Importing payments...")
        with open('database_export/payments_20250828_184612.json', 'r') as f:
            payments_data = json.load(f)
        
        for payment_data in payments_data:
            player_name = payment_data['player_name']
            if player_name in player_map:
                session.execute(text("""
                    INSERT INTO payment (player_id, amount, payment_date, payment_method)
                    VALUES (:player_id, :amount, :payment_date, :payment_method)
                """), {
                    'player_id': player_map[player_name],
                    'amount': payment_data['amount'],
                    'payment_date': payment_data['payment_date'],
                    'payment_method': payment_data['payment_method']
                })
                print(f"  ✅ Added payment: {player_name} - ${payment_data['amount']}")
        
        # Commit all changes
        session.commit()
        
        print(f"\n✅ Data import completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Players imported: {len(players_data)}")
        print(f"   - Ledger entries imported: {len(ledger_data)}")
        print(f"   - Payments imported: {len(payments_data)}")
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    import_data()
