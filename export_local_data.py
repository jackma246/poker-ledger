#!/usr/bin/env python3
"""
Export all local data to JSON files for migration to Railway
"""

import json
import os
from datetime import datetime
from app import app, db, Player, LedgerEntry, Payment

def export_data():
    """Export all data to JSON files"""
    with app.app_context():
        print("Exporting local data...")
        
        # Export players
        players = Player.query.all()
        players_data = []
        for player in players:
            players_data.append({
                'id': player.id,
                'name': player.name,
                'preferred_payment_method': player.preferred_payment_method,
                'payment_id': player.payment_id,
                'created_at': player.created_at.isoformat() if player.created_at else None
            })
        
        with open('exported_players.json', 'w') as f:
            json.dump(players_data, f, indent=2)
        print(f"Exported {len(players_data)} players")
        
        # Export ledger entries
        ledger_entries = LedgerEntry.query.all()
        ledger_data = []
        for entry in ledger_entries:
            ledger_data.append({
                'id': entry.id,
                'player_id': entry.player_id,
                'game_date': entry.game_date.isoformat() if entry.game_date else None,
                'net_profit': entry.net_profit,
                'running_balance': entry.running_balance,
                'created_at': entry.created_at.isoformat() if entry.created_at else None
            })
        
        with open('exported_ledger.json', 'w') as f:
            json.dump(ledger_data, f, indent=2)
        print(f"Exported {len(ledger_data)} ledger entries")
        
        # Export payments
        payments = Payment.query.all()
        payments_data = []
        for payment in payments:
            payments_data.append({
                'id': payment.id,
                'player_id': payment.player_id,
                'amount': payment.amount,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'payment_method': payment.payment_method,
                'created_at': payment.created_at.isoformat() if payment.created_at else None
            })
        
        with open('exported_payments.json', 'w') as f:
            json.dump(payments_data, f, indent=2)
        print(f"Exported {len(payments_data)} payments")
        
        print("Data export completed!")

if __name__ == "__main__":
    export_data()
