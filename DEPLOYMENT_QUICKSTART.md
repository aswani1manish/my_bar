# Quick Reference: Cloud Deployment

This is a condensed version of the deployment guide. For full details, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Overview

- **Frontend**: PythonAnywhere (static files or served via Flask)
- **Backend**: PythonAnywhere (Flask app)
- **Database**: MongoDB Atlas (cloud MongoDB)

## 1. MongoDB Atlas Setup (5 minutes)

1. Sign up at https://www.mongodb.com/cloud/atlas/register
2. Create free M0 cluster
3. Create database user (save username/password)
4. Network Access → Add IP → Allow from Anywhere (0.0.0.0/0)
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/...`

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

Add:
```bash
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=neighborhood_sips
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
| 500 Error | Check error log in Web tab |
| MongoDB timeout | Verify connection string and Network Access |
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
- MongoDB Atlas docs: https://docs.atlas.mongodb.com/
