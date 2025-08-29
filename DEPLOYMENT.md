# Poker Ledger Deployment Guide

This guide will help you deploy the Poker Ledger application online so everyone can access it.

## Option 1: Deploy on Railway (Recommended - Free & Easy)

### 1. Prepare Your Application
1. Make sure your code is in a Git repository (GitHub, GitLab, etc.)
2. Ensure you have the following files:
   - `app.py`
   - `config.py`
   - `wsgi.py`
   - `requirements.txt`
   - All template files in the `templates/` folder

### 2. Deploy on Railway
1. Go to [Railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select your repository
4. Railway will automatically detect it's a Python app
5. Add environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-super-secret-key-here`
   - `ADMIN_PASSWORD=your-secure-admin-password`
6. Deploy!

### 3. Access Your Application
- Railway will provide you with a URL like `https://your-app-name.railway.app`
- Share this URL with your poker group
- Only you (the admin) can modify data using the admin password

## Option 2: Deploy on Heroku

### 1. Install Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### 2. Create Heroku App
```bash
heroku login
heroku create your-poker-ledger-app
```

### 3. Set Environment Variables
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set ADMIN_PASSWORD=your-secure-admin-password
```

### 4. Deploy
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## Option 3: Deploy on PythonAnywhere (Free Tier Available)

### 1. Sign Up
1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Create a free account

### 2. Upload Your Code
1. Go to the "Files" tab
2. Upload your application files
3. Or use Git to clone your repository

### 3. Set Up Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.9 poker-ledger
pip install -r requirements.txt
```

### 4. Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Flask" and Python 3.9
4. Set the source code directory to your app folder
5. Set the WSGI configuration file to point to your `wsgi.py`

### 5. Set Environment Variables
In the WSGI configuration file, add:
```python
import os
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-super-secret-key-here'
os.environ['ADMIN_PASSWORD'] = 'your-secure-admin-password'
```

## Option 4: Deploy on DigitalOcean App Platform

### 1. Create App
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect your Git repository

### 2. Configure App
- Build Command: `pip install -r requirements.txt`
- Run Command: `gunicorn wsgi:app`
- Environment Variables:
  - `FLASK_ENV=production`
  - `SECRET_KEY=your-super-secret-key-here`
  - `ADMIN_PASSWORD=your-secure-admin-password`

## Security Considerations

### 1. Change Default Passwords
- **IMPORTANT**: Change the default admin password (`admin123`) before deploying
- Use a strong, unique password
- Set it via environment variable `ADMIN_PASSWORD`

### 2. Secure Your Secret Key
- Generate a random secret key: `python -c "import secrets; print(secrets.token_hex(32))"`
- Set it via environment variable `SECRET_KEY`

### 3. HTTPS
- Most platforms (Railway, Heroku, etc.) provide HTTPS automatically
- For self-hosted solutions, ensure you have SSL certificates

## Admin Access

Once deployed:
1. Visit your application URL
2. Click "Admin Login" in the navigation
3. Enter your admin password
4. You'll see "Admin Mode" badge when logged in
5. Only you can upload CSV files, edit payments, etc.

## Regular User Access

Everyone else can:
- View the current ledger
- See player details
- Browse game history
- View the calendar
- Export data (read-only)

## Database Considerations

### SQLite (Default)
- Good for small to medium groups
- Data is stored in a file
- Backups: Download the `poker_ledger.db` file

### PostgreSQL (Recommended for Production)
- Better for larger groups
- More robust and scalable
- Set `DATABASE_URL` environment variable

## Backup Strategy

### Regular Backups
1. Export data regularly using the export feature
2. Download the database file if using SQLite
3. Set up automated backups if your platform supports it

### Data Recovery
- Keep multiple copies of your database
- Test your backup restoration process

## Monitoring

### Check Application Health
- Monitor your application's uptime
- Set up alerts for downtime
- Check logs for errors

### Usage Analytics
- Monitor how often the app is accessed
- Track which features are used most

## Troubleshooting

### Common Issues
1. **App won't start**: Check environment variables are set correctly
2. **Database errors**: Ensure database file has proper permissions
3. **Upload issues**: Check file size limits and upload folder permissions

### Getting Help
- Check the platform's documentation
- Look at application logs
- Test locally first before deploying

## Cost Considerations

### Free Options
- Railway: Free tier available
- Heroku: Free tier discontinued, paid plans start at $7/month
- PythonAnywhere: Free tier available
- Render: Free tier available

### Paid Options
- DigitalOcean: Starts at $5/month
- AWS: Pay-as-you-go
- Google Cloud: Pay-as-you-go

## Recommended Setup for Small Groups

1. **Railway** (Free tier)
2. **SQLite database** (sufficient for small groups)
3. **Strong admin password**
4. **Regular backups** (weekly exports)

This setup will cost $0 and provide a reliable, secure way for your poker group to track finances.
