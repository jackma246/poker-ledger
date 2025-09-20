from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os
from werkzeug.utils import secure_filename
from functools import wraps
from config import config

# Get configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[config_name])

# Admin configuration
ADMIN_PASSWORD = app.config['ADMIN_PASSWORD']

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required for this action.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Database Models
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    preferred_payment_method = db.Column(db.String(50), nullable=True)  # Cash, Venmo, Zelle, etc.
    payment_id = db.Column(db.String(100), nullable=True)  # Venmo ID, phone number, email, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ledger_entries = db.relationship('LedgerEntry', backref='player', lazy=True)
    payments = db.relationship('Payment', backref='player', lazy=True)

class LedgerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    net_profit = db.Column(db.Float, default=0.0)
    running_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('player_id', 'game_date', name='_player_game_uc'),)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)  # Track how payment was made
    transfer_to_player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)  # For transfers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transfer_to_player = db.relationship('Player', foreign_keys=[transfer_to_player_id], backref='transfers_received')

class LedgerHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(100), nullable=False)
    final_balance = db.Column(db.Float, nullable=False)
    cleared_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
@admin_required
def upload_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            try:
                # Read CSV file
                df = pd.read_csv(file)
                required_columns = ['player_nickname', 'net']
                
                if not all(col in df.columns for col in required_columns):
                    flash('CSV must contain player_nickname and net columns', 'error')
                    return redirect(request.url)
                
                # Get game date from form
                game_date_str = request.form.get('game_date')
                if not game_date_str:
                    flash('Game date is required', 'error')
                    return redirect(request.url)
                
                game_date = datetime.strptime(game_date_str, '%Y-%m-%d').date()
                
                # Check if this game date already has entries
                existing_entries = LedgerEntry.query.filter_by(game_date=game_date).first()
                if existing_entries:
                    flash(f'Game data for {game_date_str} already exists. Please use a different date or clear existing entries.', 'error')
                    return redirect(request.url)
                
                # Consolidate duplicate players in the CSV
                consolidated_data = {}
                for _, row in df.iterrows():
                    player_name = row['player_nickname'].strip()
                    net_profit_cents = float(row['net'])
                    net_profit_dollars = net_profit_cents / 100.0
                    
                    # Convert to lowercase for case-insensitive comparison
                    player_key = player_name.lower()
                    
                    if player_key in consolidated_data:
                        # Add to existing player's net profit
                        consolidated_data[player_key]['net'] += net_profit_dollars
                        consolidated_data[player_key]['original_names'].add(player_name)
                    else:
                        # Create new player entry
                        consolidated_data[player_key] = {
                            'name': player_name,  # Use first occurrence as display name
                            'net': net_profit_dollars,
                            'original_names': {player_name}
                        }
                
                # Process consolidated data
                new_players = []
                existing_players = []
                
                for player_key, data in consolidated_data.items():
                    player_name = data['name']
                    net_profit_dollars = data['net']
                    
                    # Check if player exists (case insensitive)
                    existing_player = Player.query.filter(
                        db.func.lower(Player.name) == db.func.lower(player_name)
                    ).first()
                    
                    if existing_player:
                        existing_players.append({
                            'name': player_name,
                            'net': net_profit_dollars,
                            'player_id': existing_player.id,
                            'matched_name': existing_player.name
                        })
                    else:
                        new_players.append({
                            'name': player_name,
                            'net': net_profit_dollars
                        })
                
                # Show consolidation info if there were duplicates
                consolidation_info = []
                for player_key, data in consolidated_data.items():
                    if len(data['original_names']) > 1:
                        consolidation_info.append({
                            'final_name': data['name'],
                            'original_names': list(data['original_names']),
                            'total_net': data['net']
                        })
                
                # Get all existing players for dropdown
                all_existing_players = Player.query.order_by(Player.name).all()
                
                return render_template('confirm_upload.html', 
                                     new_players=new_players, 
                                     existing_players=existing_players,
                                     game_date=game_date_str,
                                     consolidation_info=consolidation_info,
                                     all_existing_players=all_existing_players)
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/confirm_upload', methods=['POST'])
@admin_required
def confirm_upload():
    game_date = datetime.strptime(request.form.get('game_date'), '%Y-%m-%d').date()
    
    try:
        # Double-check that no entries exist for this game date
        existing_entries = LedgerEntry.query.filter_by(game_date=game_date).first()
        if existing_entries:
            flash(f'Game data for {game_date.strftime("%Y-%m-%d")} already exists. Please use a different date.', 'error')
            return redirect(url_for('upload_csv'))
        
        print("=== DEBUG: Processing upload ===")
        print(f"Game date: {game_date}")
        
        # Process new players with their actions
        new_players_data = request.form.getlist('new_players')
        print(f"New players data: {new_players_data}")
        
        processed_players = set()  # Track processed players to avoid duplicates
        
        for i, player_data in enumerate(new_players_data):
            if player_data:
                name, net = player_data.split('|')
                name = name.strip()
                
                # Check if we've already processed this player
                if name in processed_players:
                    print(f"WARNING: Duplicate player '{name}' found in new_players_data")
                    continue
                
                processed_players.add(name)
                print(f"Processing new player: {name} with net: {net}")
                
                # Get the action chosen for this player
                action = request.form.get(f'action_{i}')
                print(f"Action for {name}: {action}")
                
                if action == 'match':
                    # Match to existing player
                    match_player_id = request.form.get(f'match_player_{i}')
                    if match_player_id:
                        existing_player = Player.query.get(int(match_player_id))
                        if existing_player:
                            print(f"Matching '{name}' to existing player '{existing_player.name}' (ID: {existing_player.id})")
                            
                            # Add ledger entry to existing player
                            last_entry = LedgerEntry.query.filter_by(player_id=existing_player.id).order_by(LedgerEntry.game_date.desc()).first()
                            current_balance = last_entry.running_balance if last_entry else 0.0
                            
                            entry = LedgerEntry(
                                player_id=existing_player.id,
                                game_date=game_date,
                                net_profit=float(net),
                                running_balance=current_balance + float(net)
                            )
                            db.session.add(entry)
                        else:
                            print(f"ERROR: Could not find existing player with ID {match_player_id}")
                            flash(f'Error: Could not find existing player for {name}', 'error')
                            return redirect(url_for('upload_csv'))
                    else:
                        print(f"ERROR: No match player selected for {name}")
                        flash(f'Error: Please select an existing player to match {name} to', 'error')
                        return redirect(url_for('upload_csv'))
                        
                elif action == 'create':
                    # Create new player with custom name
                    create_name = request.form.get(f'create_name_{i}', name).strip()
                    if create_name:
                        print(f"Creating new player '{create_name}' (from CSV name '{name}')")
                        
                        # Check if the new name already exists
                        existing_player = Player.query.filter(
                            db.func.lower(Player.name) == db.func.lower(create_name)
                        ).first()
                        
                        if existing_player:
                            print(f"ERROR: Player '{create_name}' already exists")
                            flash(f'Error: Player "{create_name}" already exists. Please choose a different name or match to existing player.', 'error')
                            return redirect(url_for('upload_csv'))
                        
                        # Create new player
                        player = Player(name=create_name)
                        db.session.add(player)
                        db.session.flush()  # Get the ID
                        print(f"Created player '{create_name}' with ID {player.id}")
                        
                        # Add ledger entry
                        entry = LedgerEntry(
                            player_id=player.id,
                            game_date=game_date,
                            net_profit=float(net),
                            running_balance=float(net)
                        )
                        db.session.add(entry)
                    else:
                        print(f"ERROR: No name provided for new player from {name}")
                        flash(f'Error: Please provide a name for the new player from {name}', 'error')
                        return redirect(url_for('upload_csv'))
                else:
                    print(f"ERROR: Invalid action '{action}' for {name}")
                    flash(f'Error: Invalid action for {name}', 'error')
                    return redirect(url_for('upload_csv'))
        
        # Process existing players
        existing_players_data = request.form.getlist('existing_players')
        print(f"Existing players data: {existing_players_data}")
        
        for i, player_data in enumerate(existing_players_data):
            if player_data:
                name, net, original_player_id = player_data.split('|')
                name = name.strip()
                
                if name in processed_players:
                    print(f"WARNING: Player '{name}' already processed, skipping")
                    continue
                
                processed_players.add(name)
                print(f"Processing existing player: {name} (Original ID: {original_player_id}) with net: {net}")
                
                # Check if user wants to fix the match
                existing_action = request.form.get(f'existing_action_{i}')
                print(f"Existing action for {name}: {existing_action}")
                
                if existing_action == 'fix':
                    # User wants to fix the match
                    fix_player_id = request.form.get(f'fix_match_player_{i}')
                    if fix_player_id and fix_player_id != original_player_id:
                        target_player_id = int(fix_player_id)
                        print(f"Fixing match for '{name}' from player ID {original_player_id} to {target_player_id}")
                    else:
                        target_player_id = int(original_player_id)
                        print(f"Keeping original match for '{name}' (player ID: {original_player_id})")
                else:
                    # Keep the original match
                    target_player_id = int(original_player_id)
                    print(f"Keeping original match for '{name}' (player ID: {original_player_id})")
                
                # Get current running balance for the target player
                last_entry = LedgerEntry.query.filter_by(player_id=target_player_id).order_by(LedgerEntry.game_date.desc()).first()
                current_balance = last_entry.running_balance if last_entry else 0.0
                
                # Add ledger entry to the target player
                entry = LedgerEntry(
                    player_id=target_player_id,
                    game_date=game_date,
                    net_profit=float(net),
                    running_balance=current_balance + float(net)
                )
                db.session.add(entry)
        
        print("=== DEBUG: About to commit ===")
        db.session.commit()
        print("=== DEBUG: Commit successful ===")
        flash('CSV data uploaded successfully!', 'success')
        return redirect(url_for('ledger'))
        
    except Exception as e:
        print(f"=== DEBUG: Error occurred: {str(e)} ===")
        db.session.rollback()
        flash(f'Error uploading data: {str(e)}', 'error')
        return redirect(url_for('upload_csv'))

@app.route('/ledger')
def ledger():
    # Get all players with their current ledger status
    players = Player.query.all()
    ledger_data = []
    
    for player in players:
        # Get latest ledger entry
        latest_entry = LedgerEntry.query.filter_by(player_id=player.id).order_by(LedgerEntry.game_date.desc()).first()
        
        # Calculate total payments
        total_payments = db.session.query(db.func.sum(Payment.amount)).filter_by(player_id=player.id).scalar() or 0.0
        
        # Calculate remaining payment
        current_balance = latest_entry.running_balance if latest_entry else 0.0
        # If current_balance is negative (player owes money), payments reduce the debt
        # If current_balance is positive (player is owed money), payments reduce what they're owed
        remaining_payment = current_balance + total_payments
        
        # Fix negative zero issue by treating very small numbers as zero
        if abs(remaining_payment) < 0.01:
            remaining_payment = 0.0
        
        ledger_data.append({
            'player': player,
            'current_balance': current_balance,
            'total_payments': total_payments,
            'remaining_payment': remaining_payment,
            'latest_game': latest_entry.game_date if latest_entry else None
        })
    
    return render_template('ledger.html', ledger_data=ledger_data)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    
    # Get all ledger entries
    ledger_entries = LedgerEntry.query.filter_by(player_id=player_id).order_by(LedgerEntry.game_date.desc()).all()
    
    # Get all payments with recipient information
    payments = Payment.query.filter_by(player_id=player_id).order_by(Payment.payment_date.desc()).all()
    
    # Calculate total net profit from games only
    total_net_profit = sum(entry.net_profit for entry in ledger_entries)
    
    return render_template('player_detail.html', player=player, ledger_entries=ledger_entries, payments=payments, total_net_profit=total_net_profit)

@app.route('/edit_player', methods=['POST'])
@admin_required
def edit_player():
    player_id = request.form.get('player_id')
    preferred_payment_method = request.form.get('preferred_payment_method')
    payment_id = request.form.get('payment_id')
    
    player = Player.query.get_or_404(int(player_id))
    player.preferred_payment_method = preferred_payment_method if preferred_payment_method else None
    player.payment_id = payment_id if payment_id else None
    
    db.session.commit()
    flash('Player information updated successfully!', 'success')
    return redirect(url_for('player_detail', player_id=player_id))

@app.route('/add_payment', methods=['POST'])
@admin_required
def add_payment():
    player_id = request.form.get('player_id')
    transfer_to_player_id = request.form.get('transfer_to_player_id')
    amount = float(request.form.get('amount'))
    payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
    payment_method = request.form.get('payment_method')
    
    # Create payment record for the payer
    payment = Payment(
        player_id=int(player_id),
        amount=amount,
        payment_date=payment_date,
        payment_method=payment_method,
        transfer_to_player_id=int(transfer_to_player_id) if transfer_to_player_id else None
    )
    db.session.add(payment)
    
    # If this is a transfer to another player, create a corresponding negative payment record for the recipient
    if transfer_to_player_id:
        recipient_payment = Payment(
            player_id=int(transfer_to_player_id),
            amount=-amount,  # Negative amount for the recipient
            payment_date=payment_date,
            payment_method=payment_method,
            transfer_to_player_id=int(player_id)  # Reference back to the original payer
        )
        db.session.add(recipient_payment)
    
    db.session.commit()
    
    if transfer_to_player_id:
        payer = Player.query.get(int(player_id))
        recipient = Player.query.get(int(transfer_to_player_id))
        flash(f'Payment transfer of ${amount:.2f} from {payer.name} to {recipient.name} recorded successfully!', 'success')
    else:
        flash('Payment added successfully!', 'success')
    
    return redirect(url_for('player_detail', player_id=player_id))

@app.route('/edit_ledger_entry', methods=['POST'])
@admin_required
def edit_ledger_entry():
    entry_id = request.form.get('entry_id')
    net_profit = float(request.form.get('net_profit'))
    
    entry = LedgerEntry.query.get_or_404(int(entry_id))
    old_net = entry.net_profit
    entry.net_profit = net_profit
    
    # Recalculate running balance for this entry and all subsequent entries
    player_entries = LedgerEntry.query.filter_by(player_id=entry.player_id).order_by(LedgerEntry.game_date).all()
    
    running_balance = 0.0
    for e in player_entries:
        if e.id == entry.id:
            running_balance += net_profit
        else:
            running_balance += e.net_profit
        e.running_balance = running_balance
    
    db.session.commit()
    flash('Ledger entry updated successfully!', 'success')
    return redirect(url_for('player_detail', player_id=entry.player_id))

@app.route('/clear_ledger', methods=['POST'])
@admin_required
def clear_ledger():
    player_id = request.form.get('player_id')
    player = Player.query.get_or_404(int(player_id))
    
    # Get current balance
    latest_entry = LedgerEntry.query.filter_by(player_id=player.id).order_by(LedgerEntry.game_date.desc()).first()
    final_balance = latest_entry.running_balance if latest_entry else 0.0
    
    # Add to history
    history_entry = LedgerHistory(
        player_name=player.name,
        final_balance=final_balance,
        cleared_date=datetime.utcnow().date()
    )
    db.session.add(history_entry)
    
    # Delete all ledger entries and payments for this player
    LedgerEntry.query.filter_by(player_id=player.id).delete()
    Payment.query.filter_by(player_id=player.id).delete()
    
    # Delete the player
    db.session.delete(player)
    db.session.commit()
    
    flash(f'Ledger cleared for {player.name}!', 'success')
    return redirect(url_for('ledger'))

@app.route('/history')
def history():
    history_entries = LedgerHistory.query.order_by(LedgerHistory.cleared_date.desc()).all()
    return render_template('history.html', history_entries=history_entries)

@app.route('/export')
def export_data():
    # Export current ledger data
    players = Player.query.all()
    export_data = []
    
    for player in players:
        latest_entry = LedgerEntry.query.filter_by(player_id=player.id).order_by(LedgerEntry.game_date.desc()).first()
        total_payments = db.session.query(db.func.sum(Payment.amount)).filter_by(player_id=player.id).scalar() or 0.0
        
        current_balance = latest_entry.running_balance if latest_entry else 0.0
        remaining_payment = current_balance - total_payments
        
        export_data.append({
            'Player Name': player.name,
            'Preferred Payment Method': player.preferred_payment_method or 'Not set',
            'Payment ID': player.payment_id or 'Not set',
            'Current Balance': current_balance,
            'Total Payments': total_payments,
            'Remaining Payment': remaining_payment,
            'Last Game': latest_entry.game_date.strftime('%Y-%m-%d') if latest_entry else 'N/A'
        })
    
    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(export_data)
    export_path = os.path.join(app.config['UPLOAD_FOLDER'], f'ledger_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    df.to_csv(export_path, index=False)
    
    return jsonify({'success': True, 'file': export_path})

@app.route('/debug_player/<int:player_id>')
def debug_player(player_id):
    player = Player.query.get_or_404(player_id)
    
    # Get all ledger entries
    ledger_entries = LedgerEntry.query.filter_by(player_id=player_id).order_by(LedgerEntry.game_date.desc()).all()
    
    # Get all payments
    payments = Payment.query.filter_by(player_id=player_id).order_by(Payment.payment_date.desc()).all()
    
    # Calculate values
    current_balance = ledger_entries[0].running_balance if ledger_entries else 0.0
    total_payments = sum(p.amount for p in payments)
    remaining_payment = current_balance + total_payments
    
    debug_info = {
        'player_name': player.name,
        'current_balance': current_balance,
        'total_payments': total_payments,
        'remaining_payment': remaining_payment,
        'calculation': f"{current_balance} + {total_payments} = {remaining_payment}",
        'ledger_entries': [
            {
                'game_date': str(entry.game_date),
                'net_profit': entry.net_profit,
                'running_balance': entry.running_balance
            } for entry in ledger_entries
        ],
        'payments': [
            {
                'payment_date': str(payment.payment_date),
                'amount': payment.amount,
                'payment_method': payment.payment_method
            } for payment in payments
        ]
    }
    
    return jsonify(debug_info)

@app.route('/debug')
def debug():
    players = Player.query.all()
    player_info = []
    for player in players:
        entries = LedgerEntry.query.filter_by(player_id=player.id).all()
        player_info.append({
            'id': player.id,
            'name': player.name,
            'entries': [{'game_date': str(e.game_date), 'net_profit': e.net_profit} for e in entries]
        })
    return jsonify(player_info)

@app.route('/api/players')
def api_players():
    players = Player.query.all()
    return jsonify([{'id': p.id, 'name': p.name} for p in players])

@app.route('/calendar')
def calendar():
    # Get all unique game dates
    game_dates = db.session.query(LedgerEntry.game_date).distinct().order_by(LedgerEntry.game_date.desc()).all()
    game_dates = [date[0] for date in game_dates]
    
    # Group dates by year and month for easier display
    calendar_data = {}
    for date in game_dates:
        year = date.year
        month = date.month
        if year not in calendar_data:
            calendar_data[year] = {}
        if month not in calendar_data[year]:
            calendar_data[year][month] = []
        calendar_data[year][month].append(date)
    
    return render_template('calendar.html', calendar_data=calendar_data)

@app.route('/game/<date>')
def game_detail(date):
    try:
        game_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('calendar'))
    
    # Get all players who played on this date
    entries = LedgerEntry.query.filter_by(game_date=game_date).all()
    
    if not entries:
        flash(f'No game data found for {date}', 'error')
        return redirect(url_for('calendar'))
    
    # Get player details for each entry
    game_data = []
    for entry in entries:
        player = Player.query.get(entry.player_id)
        game_data.append({
            'player': player,
            'net_profit': entry.net_profit,
            'entry_id': entry.id
        })
    
    # Sort by net profit (highest to lowest)
    game_data.sort(key=lambda x: x['net_profit'], reverse=True)
    
    return render_template('game_detail.html', game_date=game_date, game_data=game_data)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Admin access granted!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid admin password.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Admin access revoked.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 