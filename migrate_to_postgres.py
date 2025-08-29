#!/usr/bin/env python3
"""
Script to migrate data from SQLite to PostgreSQL
Run this once after setting up PostgreSQL on Railway
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Player, LedgerEntry, Payment, GameHistory

def migrate_data():
    """Migrate sample data to PostgreSQL"""
    with app.app_context():
        # Check if data already exists
        if Player.query.count() > 0:
            print("Data already exists in database, skipping migration")
            return
        
        print("Starting data migration to PostgreSQL...")
        
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
        
        players = []
        for player_data in players_data:
            player = Player(**player_data)
            db.session.add(player)
            players.append(player)
        
        db.session.commit()
        print(f"Created {len(players)} players")
        
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
        print(f"Created {len(ledger_data)} ledger entries")
        
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
        print(f"Created {len(payments_data)} payments")
        
        print("Data migration completed successfully!")

if __name__ == "__main__":
    migrate_data()
