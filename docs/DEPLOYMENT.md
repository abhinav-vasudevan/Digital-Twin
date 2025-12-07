# PythonAnywhere Deployment Guide

## Step 1: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/registration/register/beginner/
2. Create a free account
3. Verify your email

## Step 2: Set Up Your App

### Open a Bash Console
1. From PythonAnywhere dashboard, click "Consoles" → "Bash"
2. Clone your repository:
```bash
git clone https://github.com/abhinav-vasudevan/Digital-Twin.git
cd Digital-Twin
```

### Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 digitaltwin
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create Data Directory
```bash
mkdir -p service/data
cd service/data
echo '{}' > users.json
echo '{}' > profile.json
echo '{}' > meal_plans.json
echo '{}' > daily_logs.json
cd ../..
```

## Step 3: Configure Web App

### Create Web App
1. Go to "Web" tab in PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select "Python 3.10"

### Configure WSGI File
1. Click on "WSGI configuration file" link
2. Delete all content and replace with:

```python
import sys
from pathlib import Path

# Update this with your username
project_home = '/home/YOUR_USERNAME/Digital-Twin'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the FastAPI app
from service.api import app
application = app
```

### Set Virtual Environment
1. In the "Web" tab, find "Virtualenv" section
2. Enter: `/home/YOUR_USERNAME/.virtualenvs/digitaltwin`
3. Click the checkmark

### Set Working Directory
1. In "Code" section, set "Working directory" to:
   `/home/YOUR_USERNAME/Digital-Twin`

### Configure Static Files (Optional for better performance)
1. In "Static files" section, add:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/Digital-Twin/service/static/`

## Step 4: Launch

1. Click the green "Reload" button at the top
2. Your app will be live at: `YOUR_USERNAME.pythonanywhere.com`

## Updating Your App

When you make changes:

```bash
cd ~/Digital-Twin
git pull
# If requirements changed:
pip install -r requirements.txt
# Reload web app from Web tab
```

## Troubleshooting

### Check Error Logs
- Go to "Web" tab → "Error log" link

### Check Server Log
- Go to "Web" tab → "Server log" link

### Common Issues

**Import Error:**
- Make sure working directory is set correctly
- Check WSGI file has correct username

**Static Files Not Loading:**
- Add static files mapping in Web tab

**Database/JSON Files Not Found:**
- Make sure `service/data/` directory exists with JSON files

## Important Notes

- Free tier has 512 MB disk space
- Your app is always online (no sleeping)
- Data persists in JSON files
- Custom domains available on paid plans

## Your App URLs

- Main site: https://YOUR_USERNAME.pythonanywhere.com
- Login: https://YOUR_USERNAME.pythonanywhere.com/login
- Dashboard: https://YOUR_USERNAME.pythonanywhere.com/dashboard
