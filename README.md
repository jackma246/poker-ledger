# Poker Ledger Management System

A local HTTP web application for managing poker game finances, tracking player buy-ins, cash-outs, and maintaining running balances with payment tracking.

## Features

- **Admin-Only Modifications**: Secure admin role for uploading CSV files and managing payments
- **Read-Only Access**: Regular users can view ledger data but cannot modify it
- **CSV Upload**: Import game results from CSV files with automatic player matching (Admin only)
- **Cents Conversion**: Automatically converts cents values to dollars (e.g., 5000 cents = $50.00)
- **Ledger Management**: Track running balances, payments, and remaining amounts
- **Player Management**: Automatic case-insensitive player matching with confirmation for new players
- **Payment Preferences**: Store preferred payment methods (Venmo, Zelle, PayPal, etc.) and payment IDs
- **Payment Tracking**: Record partial and full payments with dates and payment methods (Admin only)
- **Ledger History**: Store cleared ledgers in history for audit purposes
- **Data Export**: Export current ledger data as CSV files
- **Modern UI**: Clean, responsive interface built with Bootstrap
- **Online Deployment Ready**: Configured for easy deployment to cloud platforms

## CSV Format Requirements

The application expects CSV files with the following columns:

| Column | Required | Description |
|--------|----------|-------------|
| `player_nickname` | Yes | Player's name |
| `net` | Yes | Net profit/loss for the session **in cents** |
| `player_id` | No | Unique player identifier (not used) |
| `session_start_at` | No | Session start time (not used) |
| `session_end_at` | No | Session end time (not used) |
| `buy_in` | No | Buy-in amount (not used) |
| `buy_out` | No | Cash-out amount (not used) |
| `stack` | No | Final stack (not used) |

### Example CSV (values in cents):
```csv
player_nickname,player_id,session_start_at,session_end_at,buy_in,buy_out,stack,net
John,12345,2024-01-15 19:00:00,2024-01-15 23:00:00,10000,15000,15000,5000
Sarah,12346,2024-01-15 19:00:00,2024-01-15 23:00:00,10000,8000,8000,-2000
```

**Note**: The `net` column values are in cents and will be automatically converted to dollars (5000 = $50.00, -2000 = -$20.00).

## Payment Method Preferences

Players can set their preferred payment methods and payment IDs:

- **Venmo**: Store Venmo username/ID
- **Zelle**: Store phone number or email
- **PayPal**: Store PayPal email
- **Cash**: No additional ID needed
- **Check**: No additional ID needed
- **Other**: Custom payment method

## Installation

### Local Development

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your web browser and go to `http://localhost:5000`

### Online Deployment

For hosting the application online so everyone can access it, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:
- Railway (Recommended - Free)
- Heroku
- PythonAnywhere
- DigitalOcean
- And more...

## Usage

### Admin Access
1. **Login as Admin**: Click "Admin Login" in the navigation and enter the admin password
2. **Admin Mode**: You'll see an "Admin Mode" badge when logged in
3. **Admin Features**: Only admins can upload CSV files, edit payments, and modify data

### 1. Upload CSV File (Admin Only)
- Navigate to the "Upload CSV" page (only visible when logged in as admin)
- Select your CSV file with game results (values in cents)
- Choose the game date
- Review the confirmation page showing new vs existing players
- Confirm the upload

### 2. View Ledger
- The main ledger page shows all players with:
  - Current balance
  - Total payments made
  - Remaining payment amount
  - Preferred payment method and ID
  - Last game date
  - Quick action buttons

### 3. Manage Player Information
- Click on a player's name to view detailed history
- Use "Edit Info" button to set payment preferences
- Choose preferred payment method and enter payment ID

### 4. Manage Payments (Admin Only)
- Click the "+" button next to any player to add a payment (only visible when logged in as admin)
- Enter the payment amount, date, and payment method
- Payments are tracked separately from game results

### 5. Edit Ledger Entries (Admin Only)
- Click on a player's name to view detailed history
- Edit individual game results if needed (only visible when logged in as admin)
- View payment history for each player

### 6. Clear Ledger (Admin Only)
- When a player has paid their balance (remaining payment ≤ 0)
- Use the "Clear Ledger" button to move them to history (only visible when logged in as admin)
- This creates a new clean ledger for future games

### 7. View History
- Access cleared ledgers and historical data
- See final balances and clearance dates
- Track which players paid in full vs outstanding balances

### 8. Export Data
- Export current ledger data as CSV
- Files are saved in the `uploads` folder with timestamps
- Includes payment preferences and payment IDs

## Database Structure

The application uses SQLite with the following tables:

- **Player**: Player information including payment preferences
- **LedgerEntry**: Individual game results with running balances
- **Payment**: Payment records with dates and payment methods
- **LedgerHistory**: Cleared ledgers for audit purposes

## File Structure

```
pokernow/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── sample_data.csv       # Sample CSV with cents values
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── upload.html       # CSV upload form
│   ├── confirm_upload.html # Upload confirmation
│   ├── ledger.html       # Main ledger view
│   ├── player_detail.html # Individual player details
│   └── history.html      # Ledger history
└── uploads/              # Uploaded files and exports
```

## Player Matching Logic

- **Exact Match**: Case-insensitive matching of player names
- **New Players**: Automatically detected and shown for confirmation
- **Existing Players**: Matched to current ledger entries
- **Confirmation**: Users can review all matches before processing

## Payment Tracking

- **Partial Payments**: Track multiple payments per player
- **Payment Methods**: Record how each payment was made (Cash, Venmo, Zelle, etc.)
- **Payment Preferences**: Store preferred payment methods and IDs for each player
- **Running Balance**: Automatically calculated from game results
- **Remaining Amount**: Current balance minus total payments
- **Payment History**: Full audit trail of all payments

## Cents to Dollars Conversion

The system automatically handles cents to dollars conversion:
- CSV input: `net` column values in cents (e.g., 5000, -2000)
- Display: Converted to dollars (e.g., $50.00, -$20.00)
- Storage: Stored as decimal dollars in database
- Export: Exported as dollars

## Security Notes

- **Admin Authentication**: Admin access is protected by password
- **Read-Only Access**: Regular users can only view data, not modify it
- **Session Management**: Admin sessions expire after 24 hours
- **Environment Variables**: Sensitive data (passwords, secret keys) should be set via environment variables in production
- **Database Security**: Database file (`poker_ledger.db`) contains all sensitive data
- **Backups**: Keep regular backups of the database file

## Troubleshooting

### Common Issues:

1. **CSV Upload Fails**:
   - Ensure CSV has `player_nickname` and `net` columns
   - Check that `net` values are in cents (whole numbers)
   - Check file format (UTF-8 encoding recommended)
   - Verify date format is valid

2. **Database Errors**:
   - Delete `poker_ledger.db` to reset the database
   - Ensure write permissions in the application directory

3. **Port Already in Use**:
   - Change the port in `app.py` line: `app.run(debug=True, host='0.0.0.0', port=5000)`

## Future Enhancements

Potential improvements for future versions:
- User authentication and multiple user support
- Advanced reporting and analytics
- Email notifications for outstanding balances
- Mobile-responsive design improvements
- Backup and restore functionality
- Game statistics and player performance tracking
- Payment method validation and verification

## License

This project is for personal use. Feel free to modify and adapt for your needs. 