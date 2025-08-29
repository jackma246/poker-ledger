#!/usr/bin/env python3
"""
Import script to restore data from JSON files to Railway database
"""
import json
import os
from datetime import datetime
from app import app, db, Player, LedgerEntry, Payment, LedgerHistory

def import_data(export_dir='database_export'):
    with app.app_context():
        # Find the most recent export files
        files = os.listdir(export_dir)
        
        # Find JSON files with timestamps
        player_files = [f for f in files if f.startswith('players_') and f.endswith('.json')]
        ledger_files = [f for f in files if f.startswith('ledger_entries_') and f.endswith('.json')]
        payment_files = [f for f in files if f.startswith('payments_') and f.endswith('.json')]
        history_files = [f for f in files if f.startswith('history_') and f.endswith('.json')]
        
        if not player_files:
            print("❌ No player export files found!")
            return
        
        # Use the most recent files
        latest_player_file = sorted(player_files)[-1]
        latest_ledger_file = sorted(ledger_files)[-1] if ledger_files else None
        latest_payment_file = sorted(payment_files)[-1] if payment_files else None
        latest_history_file = sorted(history_files)[-1] if history_files else None
        
        print(f"📁 Using export files:")
        print(f"   - Players: {latest_player_file}")
        if latest_ledger_file:
            print(f"   - Ledger: {latest_ledger_file}")
        if latest_payment_file:
            print(f"   - Payments: {latest_payment_file}")
        if latest_history_file:
            print(f"   - History: {latest_history_file}")
        
        # Import Players
        print(f"\n🔄 Importing players...")
        with open(f'{export_dir}/{latest_player_file}', 'r') as f:
            players_data = json.load(f)
        
        player_map = {}  # Map player names to IDs
        for player_data in players_data:
            # Check if player already exists
            existing_player = Player.query.filter_by(name=player_data['name']).first()
            if existing_player:
                print(f"   ⚠️  Player '{player_data['name']}' already exists, skipping")
                player_map[player_data['name']] = existing_player.id
                continue
            
            # Create new player
            player = Player(
                name=player_data['name'],
                preferred_payment_method=player_data['preferred_payment_method'],
                payment_id=player_data['payment_id']
            )
            db.session.add(player)
            db.session.flush()  # Get the ID
            player_map[player_data['name']] = player.id
            print(f"   ✅ Created player: {player_data['name']}")
        
        # Import Ledger Entries
        if latest_ledger_file:
            print(f"\n🔄 Importing ledger entries...")
            with open(f'{export_dir}/{latest_ledger_file}', 'r') as f:
                ledger_data = json.load(f)
            
            for entry_data in ledger_data:
                player_name = entry_data['player_name']
                if player_name not in player_map:
                    print(f"   ⚠️  Player '{player_name}' not found, skipping ledger entry")
                    continue
                
                # Check if entry already exists
                existing_entry = LedgerEntry.query.filter_by(
                    player_id=player_map[player_name],
                    game_date=datetime.fromisoformat(entry_data['game_date']).date()
                ).first()
                
                if existing_entry:
                    print(f"   ⚠️  Ledger entry for {player_name} on {entry_data['game_date']} already exists, skipping")
                    continue
                
                # Create new entry
                entry = LedgerEntry(
                    player_id=player_map[player_name],
                    game_date=datetime.fromisoformat(entry_data['game_date']).date(),
                    net_profit=entry_data['net_profit'],
                    running_balance=entry_data['running_balance']
                )
                db.session.add(entry)
                print(f"   ✅ Added ledger entry: {player_name} on {entry_data['game_date']}")
        
        # Import Payments
        if latest_payment_file:
            print(f"\n🔄 Importing payments...")
            with open(f'{export_dir}/{latest_payment_file}', 'r') as f:
                payments_data = json.load(f)
            
            for payment_data in payments_data:
                player_name = payment_data['player_name']
                if player_name not in player_map:
                    print(f"   ⚠️  Player '{player_name}' not found, skipping payment")
                    continue
                
                # Create new payment
                payment = Payment(
                    player_id=player_map[player_name],
                    amount=payment_data['amount'],
                    payment_date=datetime.fromisoformat(payment_data['payment_date']).date(),
                    payment_method=payment_data['payment_method']
                )
                db.session.add(payment)
                print(f"   ✅ Added payment: {player_name} - ${payment_data['amount']}")
        
        # Import History
        if latest_history_file:
            print(f"\n🔄 Importing history...")
            with open(f'{export_dir}/{latest_history_file}', 'r') as f:
                history_data = json.load(f)
            
            for history_entry in history_data:
                # Check if history entry already exists
                existing_history = LedgerHistory.query.filter_by(
                    player_name=history_entry['player_name'],
                    cleared_date=datetime.fromisoformat(history_entry['cleared_date']).date()
                ).first()
                
                if existing_history:
                    print(f"   ⚠️  History entry for {history_entry['player_name']} already exists, skipping")
                    continue
                
                # Create new history entry
                history = LedgerHistory(
                    player_name=history_entry['player_name'],
                    final_balance=history_entry['final_balance'],
                    cleared_date=datetime.fromisoformat(history_entry['cleared_date']).date()
                )
                db.session.add(history)
                print(f"   ✅ Added history entry: {history_entry['player_name']}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Data import completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Players imported: {len(players_data)}")
        if latest_ledger_file:
            print(f"   - Ledger entries imported: {len(ledger_data)}")
        if latest_payment_file:
            print(f"   - Payments imported: {len(payments_data)}")
        if latest_history_file:
            print(f"   - History entries imported: {len(history_data)}")

if __name__ == '__main__':
    import_data()
