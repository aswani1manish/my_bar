# Quick Reference: Cloud Deployment

This is a condensed version of the deployment guide. For full details, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Overview

- **Frontend**: PythonAnywhere (static files or served via Flask)
- **Backend**: PythonAnywhere (Flask app)
- **Database**: MySQL (PythonAnywhere MySQL or external service)

## 1. MySQL Database Setup (5 minutes)

### Option A: PythonAnywhere MySQL (Easiest)

1. Log in to PythonAnywhere → **Databases** tab
2. Set MySQL password (if not already set)
3. Note your connection details:
   - Host: `yourusername.mysql.pythonanywhere-services.com`
   - Username: `yourusername`
   - Database: `yourusername$neighborhood_sips`
4. The database will be created automatically when you run `python init_db.py` during backend setup

### Option B: External MySQL Service

1. Create MySQL database on your preferred service (AWS RDS, DigitalOcean, etc.)
2. Note connection details (host, port, username, password, database name)
3. Configure firewall to allow PythonAnywhere connections

## 2. PythonAnywhere Backend (10 minutes)

### Upload Code
```bash
# On PythonAnywhere Bash console
git clone https://github.com/aswani1manish/my_bar.git
cd my_bar/backend
```

### Setup Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 my_bar_env
pip install -r requirements.txt
```

### Configure
```bash
# Create .env file
nano .env
```

Add (for PythonAnywhere MySQL):
```bash
MYSQL_HOST=yourusername.mysql.pythonanywhere-services.com
MYSQL_PORT=3306
MYSQL_USER=yourusername
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=yourusername$neighborhood_sips
FLASK_ENV=production
FLASK_DEBUG=False
ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com
```

Or for external MySQL:
```bash
MYSQL_HOST=your-mysql-host.com
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=neighborhood_sips
FLASK_ENV=production
FLASK_DEBUG=False
ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com
```

### Web App Configuration

1. Web tab → Add new web app → Manual → Python 3.10
2. WSGI file → Replace with:
```python
import sys
import os

path = '/home/yourusername/my_bar/backend'
if path not in sys.path:
    sys.path.insert(0, path)

from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

from app import app as application
```
3. Virtualenv: `/home/yourusername/.virtualenvs/my_bar_env`
4. Static files:
   - URL: `/api/uploads/`
   - Directory: `/home/yourusername/my_bar/backend/uploads`
5. Click **Reload**

### Initialize Database
```bash
cd ~/my_bar/backend
workon my_bar_env
python init_db.py
```

You should see:
```
✓ Database 'yourusername$neighborhood_sips' initialized successfully
✓ Tables created: ingredients, recipes, collections
```

Reload web app again after initialization.

### Load Data (Optional)
```bash
cd ~/my_bar/backend
workon my_bar_env
python3 load_sample_ingredients.py
```

## 3. Frontend Deployment

### Option A: Serve from Backend (Easiest)

```bash
# On PythonAnywhere
cd ~/my_bar/backend
cp -r ../frontend ./static
```

Edit `app.py`, add before `if __name__ == '__main__':`:
```python
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('static', path)
    except:
        return send_from_directory('static', 'index.html')
```

Update `static/js/config.js`:
```javascript
var APP_CONFIG = {
    apiUrl: '/api'  // Relative URL
};
```

Reload web app.

### Option B: Separate Hosting

1. Configure API URL locally:
```bash
./configure_frontend.sh https://yourusername.pythonanywhere.com/api
```

2. Upload `frontend/` directory to hosting service (GitHub Pages, Netlify, etc.)

## 4. Test Deployment

- Health check: `https://yourusername.pythonanywhere.com/api/health`
- Frontend: `https://yourusername.pythonanywhere.com/`
- Test CRUD operations on ingredients, recipes, collections

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 500 Error | Check error log in Web tab; verify `.env` MySQL credentials |
| MySQL connection error | Check hostname, username, password in `.env`; run `python init_db.py` |
| Table doesn't exist | Run `python init_db.py` in virtual environment |
| CORS error | Update `ALLOWED_ORIGINS` in `.env` |
| Images not loading | Check static files mapping |

## URLs

Replace `yourusername` with your PythonAnywhere username:

- Frontend: `https://yourusername.pythonanywhere.com/`
- API: `https://yourusername.pythonanywhere.com/api/`
- Health: `https://yourusername.pythonanywhere.com/api/health`

## Support

- Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- PythonAnywhere help: https://help.pythonanywhere.com/
- PythonAnywhere MySQL: https://help.pythonanywhere.com/pages/MySQLdb/
- MySQL docs: https://dev.mysql.com/doc/
