#!/usr/bin/env python3
"""
Export script to backup all data from local database
"""
import json
import os
from datetime import datetime
from app import app, db, Player, LedgerEntry, Payment, LedgerHistory

def export_data():
    with app.app_context():
        # Export Players
        players = Player.query.all()
        players_data = []
        for player in players:
            players_data.append({
                'name': player.name,
                'preferred_payment_method': player.preferred_payment_method,
                'payment_id': player.payment_id,
                'created_at': player.created_at.isoformat() if player.created_at else None
            })
        
        # Export Ledger Entries
        ledger_entries = LedgerEntry.query.all()
        ledger_data = []
        for entry in ledger_entries:
            # Get player name for reference
            player = Player.query.get(entry.player_id)
            ledger_data.append({
                'player_name': player.name if player else 'Unknown',
                'game_date': entry.game_date.isoformat(),
                'net_profit': entry.net_profit,
                'running_balance': entry.running_balance,
                'created_at': entry.created_at.isoformat() if entry.created_at else None
            })
        
        # Export Payments
        payments = Payment.query.all()
        payments_data = []
        for payment in payments:
            # Get player name for reference
            player = Player.query.get(payment.player_id)
            payments_data.append({
                'player_name': player.name if player else 'Unknown',
                'amount': payment.amount,
                'payment_date': payment.payment_date.isoformat(),
                'payment_method': payment.payment_method,
                'created_at': payment.created_at.isoformat() if payment.created_at else None
            })
        
        # Export Ledger History
        history = LedgerHistory.query.all()
        history_data = []
        for entry in history:
            history_data.append({
                'player_name': entry.player_name,
                'final_balance': entry.final_balance,
                'cleared_date': entry.cleared_date.isoformat(),
                'created_at': entry.created_at.isoformat() if entry.created_at else None
            })
        
        # Create export directory
        export_dir = 'database_export'
        os.makedirs(export_dir, exist_ok=True)
        
        # Save data to JSON files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(f'{export_dir}/players_{timestamp}.json', 'w') as f:
            json.dump(players_data, f, indent=2)
        
        with open(f'{export_dir}/ledger_entries_{timestamp}.json', 'w') as f:
            json.dump(ledger_data, f, indent=2)
        
        with open(f'{export_dir}/payments_{timestamp}.json', 'w') as f:
            json.dump(payments_data, f, indent=2)
        
        with open(f'{export_dir}/history_{timestamp}.json', 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # Create a summary file
        summary = {
            'export_date': datetime.now().isoformat(),
            'players_count': len(players_data),
            'ledger_entries_count': len(ledger_data),
            'payments_count': len(payments_data),
            'history_count': len(history_data),
            'files': [
                f'players_{timestamp}.json',
                f'ledger_entries_{timestamp}.json',
                f'payments_{timestamp}.json',
                f'history_{timestamp}.json'
            ]
        }
        
        with open(f'{export_dir}/export_summary_{timestamp}.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Data exported successfully to {export_dir}/")
        print(f"📊 Summary:")
        print(f"   - Players: {len(players_data)}")
        print(f"   - Ledger Entries: {len(ledger_data)}")
        print(f"   - Payments: {len(payments_data)}")
        print(f"   - History: {len(history_data)}")
        print(f"\n📁 Files created:")
        for file in summary['files']:
            print(f"   - {export_dir}/{file}")
        print(f"\n🚀 Next steps:")
        print(f"   1. Upload these files to Railway")
        print(f"   2. Use the import script on Railway to restore data")

if __name__ == '__main__':
    export_data()
