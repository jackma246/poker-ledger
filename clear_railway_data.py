#!/usr/bin/env python3
"""
Clear all data from Railway database
Run this to remove any fake/wrong data
"""

import os
from app import app, db, Player, LedgerEntry, Payment

def clear_all_data():
    """Clear all data from the database"""
    with app.app_context():
        print("Clearing all data from Railway database...")
        
        # Delete all payments
        Payment.query.delete()
        print("Deleted all payments")
        
        # Delete all ledger entries
        LedgerEntry.query.delete()
        print("Deleted all ledger entries")
        
        # Delete all players
        Player.query.delete()
        print("Deleted all players")
        
        # Commit the changes
        db.session.commit()
        
        print("All data cleared successfully!")
        print("Now redeploy to import your real data from the JSON files")

if __name__ == "__main__":
    clear_all_data()
