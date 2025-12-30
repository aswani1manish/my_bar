# Cloud Deployment Guide for Neighborhood Sips

This guide provides step-by-step instructions for deploying the Neighborhood Sips application to the cloud as a brand new installation:
- **Backend**: PythonAnywhere (Flask application)
- **Database**: MySQL (PythonAnywhere MySQL or external MySQL service)
- **Frontend**: PythonAnywhere (Static files)

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Part 1: MySQL Database Setup](#part-1-mysql-database-setup)
3. [Part 2: Backend Deployment on PythonAnywhere](#part-2-backend-deployment-on-pythonanywhere)
4. [Part 3: Frontend Deployment on PythonAnywhere](#part-3-frontend-deployment-on-pythonanywhere)
5. [Part 4: Testing the Deployment](#part-4-testing-the-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have:

1. **PythonAnywhere Account** (free tier available)
   - Sign up at: https://www.pythonanywhere.com/registration/register/beginner/
   - Free tier includes one MySQL database

2. **Git** installed on your local machine (optional, for cloning code)

3. **Your application code** ready to deploy

---

## Part 1: MySQL Database Setup

### Option A: Use PythonAnywhere MySQL (Recommended for Beginners)

PythonAnywhere provides a MySQL database with your free account.

#### Step 1.1: Initialize MySQL Database on PythonAnywhere

1. Log in to [PythonAnywhere](https://www.pythonanywhere.com/)

2. Go to the **"Databases"** tab

3. You'll see your MySQL hostname (e.g., `yourusername.mysql.pythonanywhere-services.com`)

4. Set a MySQL password if you haven't already

5. Note down these credentials:
   ```
   Host: yourusername.mysql.pythonanywhere-services.com
   Username: yourusername
   Password: [your MySQL password]
   Database: yourusername$neighborhood_sips
   ```
   
   **Note:** The database `yourusername$neighborhood_sips` will be created automatically when you run the `init_db.py` script during backend setup (Step 2.8). Manual creation is not required.

### Option B: Use External MySQL Service

If you prefer to use an external MySQL service (e.g., AWS RDS, DigitalOcean, Azure):

#### Step 1.1: Create MySQL Database

1. Sign up for your preferred MySQL hosting service

2. Create a new MySQL database instance

3. Create a database named `neighborhood_sips`

4. Create a database user with full privileges on the database

5. Configure firewall/security groups to allow connections from PythonAnywhere

6. Note down the connection credentials:
   ```
   Host: your-mysql-host.com
   Port: 3306
   Username: your_username
   Password: your_password
   Database: neighborhood_sips
   ```

---

## Part 2: Backend Deployment on PythonAnywhere

### Step 2.1: Upload Your Code to PythonAnywhere

1. Log in to [PythonAnywhere](https://www.pythonanywhere.com/)

2. Go to the **"Files"** tab

3. Create a directory for your project:
   ```
   mkdir my_bar
   cd my_bar
   ```

4. **Option A: Upload files manually**
   - Use the "Upload a file" button
   - Upload all files from the `backend` directory

5. **Option B: Clone from GitHub** (recommended)
   - Go to the **"Consoles"** tab
   - Start a new **Bash console**
   - Run:
     ```bash
     cd ~
     git clone https://github.com/aswani1manish/my_bar.git
     cd my_bar/backend
     ```

### Step 2.2: Set Up Python Virtual Environment

In the PythonAnywhere Bash console:

```bash
cd ~/my_bar/backend

# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 my_bar_env

# Install dependencies
pip install -r requirements.txt
```

### Step 2.3: Configure Environment Variables

1. Create a `.env` file in the backend directory:
   ```bash
   cd ~/my_bar/backend
   nano .env
   ```

2. Add the following configuration (update with your values):

   **For PythonAnywhere MySQL:**
   ```bash
   # MySQL Configuration
   MYSQL_HOST=yourusername.mysql.pythonanywhere-services.com
   MYSQL_PORT=3306
   MYSQL_USER=yourusername
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=yourusername$neighborhood_sips
   
   # Flask Configuration
   FLASK_ENV=production
   FLASK_DEBUG=False
   
   # CORS Configuration (update with your PythonAnywhere domain)
   ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com
   
   # Upload Configuration
   MAX_CONTENT_LENGTH=16777216
   UPLOAD_FOLDER=uploads
   ```

   **For External MySQL Service:**
   ```bash
   # MySQL Configuration
   MYSQL_HOST=your-mysql-host.com
   MYSQL_PORT=3306
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=neighborhood_sips
   
   # Flask Configuration
   FLASK_ENV=production
   FLASK_DEBUG=False
   
   # CORS Configuration (update with your PythonAnywhere domain)
   ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com
   
   # Upload Configuration
   MAX_CONTENT_LENGTH=16777216
   UPLOAD_FOLDER=uploads
   ```

3. **Important:** Replace all placeholders:
   - `yourusername` with your PythonAnywhere username
   - `your_mysql_password` with your MySQL password
   - For external MySQL, update host, username, and password accordingly

4. Save and exit (Ctrl+X, then Y, then Enter)

### Step 2.4: Create Web App on PythonAnywhere

1. Go to the **"Web"** tab

2. Click **"Add a new web app"**

3. Choose **"Manual configuration"**

4. Select **Python 3.10**

5. Click **"Next"**

### Step 2.5: Configure WSGI File

1. In the **"Web"** tab, scroll to the **"Code"** section

2. Click on the **WSGI configuration file** link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)

3. **Replace all content** with:
   ```python
   import sys
   import os
   
   # Add your project directory to sys.path
   path = '/home/yourusername/my_bar/backend'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   # Set up environment variables
   from dotenv import load_dotenv
   env_path = os.path.join(path, '.env')
   load_dotenv(env_path)
   
   # Import Flask application
   from app import app as application
   ```

4. **Replace `yourusername`** with your actual PythonAnywhere username

5. Click **"Save"**

### Step 2.6: Configure Virtual Environment

1. In the **"Web"** tab, scroll to **"Virtualenv"**

2. Enter the path to your virtual environment:
   ```
   /home/yourusername/.virtualenvs/my_bar_env
   ```

3. **Replace `yourusername`** with your PythonAnywhere username

### Step 2.7: Set Static Files Mapping (for uploads)

1. In the **"Web"** tab, scroll to **"Static files"**

2. Add a new mapping:
   - **URL**: `/api/uploads/`
   - **Directory**: `/home/yourusername/my_bar/backend/uploads`

3. **Replace `yourusername`** with your PythonAnywhere username

### Step 2.8: Initialize Database Schema

Before reloading the web app, we need to initialize the database tables.

In a PythonAnywhere Bash console:

```bash
cd ~/my_bar/backend
workon my_bar_env
python init_db.py
```

This will create the necessary tables:
- `ingredients` - Stores ingredient data
- `recipes` - Stores recipe data  
- `collections` - Stores collection data

You should see output like:
```
✓ Database 'yourusername$neighborhood_sips' initialized successfully
✓ Tables created: ingredients, recipes, collections
```

### Step 2.9: Reload Web App

1. Scroll to the top of the **"Web"** tab

2. Click the big green **"Reload"** button

3. Your backend API should now be live at: `https://yourusername.pythonanywhere.com/api/`

### Step 2.10: Load Sample Data (Optional)

In a PythonAnywhere Bash console:

```bash
cd ~/my_bar/backend
workon my_bar_env
python3 load_sample_ingredients.py
```

---

## Part 3: Frontend Deployment on PythonAnywhere

### Option A: Separate Static Site (Recommended)

#### Step 3.1: Configure Frontend API URL

On your local machine, run:

```bash
cd my_bar
./configure_frontend.sh https://yourusername.pythonanywhere.com/api
```

Replace `yourusername` with your PythonAnywhere username.

#### Step 3.2: Upload Frontend Files

1. Go to the **"Files"** tab on PythonAnywhere

2. Create a new directory for the frontend:
   ```
   mkdir /home/yourusername/my_bar_frontend
   ```

3. Upload all files from the `frontend` directory to this location

#### Step 3.3: Create Static Web App

1. PythonAnywhere free tier only allows one web app, which is already used by the backend

2. **Alternative Options:**
   
   **Option 1: Serve frontend through the same Flask app**
   - Add routes in `app.py` to serve frontend files
   - See Option B below

   **Option 2: Use a different hosting service for frontend**
   - GitHub Pages (free)
   - Netlify (free)
   - Vercel (free)

### Option B: Serve Frontend from Backend (Single Web App)

#### Step 3.1: Upload Frontend to Backend Directory

In PythonAnywhere Bash console:

```bash
cd ~/my_bar/backend
cp -r ../frontend ./static
```

#### Step 3.2: Update app.py to Serve Frontend

Add this at the end of `app.py` (before `if __name__ == '__main__':`):

```python
# Serve frontend static files
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

#### Step 3.3: Update Frontend Configuration

Edit `static/js/config.js`:

```javascript
var APP_CONFIG = {
    apiUrl: '/api'  // Use relative URL since frontend and backend are on same domain
};
```

#### Step 3.4: Reload Web App

Click the **"Reload"** button on the **"Web"** tab.

Your frontend should now be accessible at: `https://yourusername.pythonanywhere.com/`

---

## Part 4: Testing the Deployment

### Step 4.1: Test Backend API

1. Open your browser and go to:
   ```
   https://yourusername.pythonanywhere.com/api/health
   ```

2. You should see:
   ```json
   {
     "status": "healthy",
     "app": "Neighborhood Sips"
   }
   ```

3. Test ingredients endpoint:
   ```
   https://yourusername.pythonanywhere.com/api/ingredients
   ```

### Step 4.2: Test Frontend

1. Open your browser and go to:
   ```
   https://yourusername.pythonanywhere.com/
   ```

2. You should see the Neighborhood Sips homepage

3. Navigate to **Ingredients**, **Recipes**, and **Collections**

4. Try creating a new ingredient to verify full functionality

### Step 4.3: Check Logs (if issues occur)

1. Go to the **"Web"** tab on PythonAnywhere

2. Check the **"Error log"** and **"Server log"** links

3. Fix any issues and reload the web app

---

## Troubleshooting

### Issue: "Internal Server Error" (500)

**Solution:**
1. Check the error log on PythonAnywhere (Web tab → Error log link)
2. Verify your `.env` file has the correct MySQL connection details
3. Ensure virtual environment is activated and all dependencies are installed
4. Check WSGI file path matches your username
5. Verify database tables exist by running `python init_db.py`

### Issue: "MySQL connection refused" or "Can't connect to MySQL server"

**Solution:**
1. For PythonAnywhere MySQL:
   - Verify MySQL hostname is correct (should be `yourusername.mysql.pythonanywhere-services.com`)
   - Check MySQL password is set in Databases tab
   - Ensure database name format is `yourusername$database_name`
   
2. For external MySQL:
   - Verify the host, port, username, and password in `.env`
   - Check that the MySQL server allows connections from PythonAnywhere IPs
   - Test connection from PythonAnywhere console:
     ```python
     # Simple connection test (for troubleshooting)
     import mysql.connector
     from mysql.connector import Error
     from config import Config
     
     try:
         config = Config()
         conn = mysql.connector.connect(
             host=config.MYSQL_HOST,
             port=config.MYSQL_PORT,
             user=config.MYSQL_USER,
             password=config.MYSQL_PASSWORD,
             database=config.MYSQL_DATABASE
         )
         print("✓ Connected successfully!")
         conn.close()
     except Error as err:
         print(f"✗ Connection failed: {err}")
     ```

### Issue: "Table doesn't exist"

**Solution:**
1. Run the database initialization script:
   ```bash
   cd ~/my_bar/backend
   workon my_bar_env
   python init_db.py
   ```
2. Check the output to ensure tables were created successfully
3. Reload the web app

### Issue: "CORS error" in browser console

**Solution:**
1. Update `ALLOWED_ORIGINS` in `.env` file
2. Include your PythonAnywhere domain (with https://)
3. Reload the web app

### Issue: Images not loading

**Solution:**
1. Check Static Files mapping in PythonAnywhere Web tab
2. Verify uploads directory exists and has proper permissions
3. Ensure URL path matches: `/api/uploads/`

### Issue: Frontend can't connect to backend

**Solution:**
1. Verify `frontend/js/config.js` has the correct API URL
2. Check browser console for exact error
3. Test backend API directly in browser
4. Ensure CORS is configured correctly

---

## Environment Variables Reference

### Backend (.env file)

```bash
# Required - MySQL Configuration
MYSQL_HOST=yourusername.mysql.pythonanywhere-services.com  # or external host
MYSQL_PORT=3306
MYSQL_USER=yourusername  # or external username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=yourusername$neighborhood_sips  # or 'neighborhood_sips' for external

# Required - Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Required - CORS Configuration
ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com

# Optional (with defaults)
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

### Frontend (config.js)

```javascript
var APP_CONFIG = {
    apiUrl: 'https://yourusername.pythonanywhere.com/api'
};
```

---

## Security Checklist

Before going to production:

- [ ] Use a strong MySQL password (not the default)
- [ ] For external MySQL, restrict access to specific IPs if possible
- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Use specific ALLOWED_ORIGINS (not `*`)
- [ ] Enable HTTPS (PythonAnywhere provides this by default)
- [ ] Keep `.env` file secure (never commit to Git)
- [ ] Regularly update dependencies for security patches
- [ ] Set up database backups (PythonAnywhere has daily backups for paid plans)
- [ ] Monitor application logs for errors
- [ ] Use environment-specific secrets and keys

---

## Useful Commands

### PythonAnywhere Console Commands

```bash
# Activate virtual environment
workon my_bar_env

# Update code from Git
cd ~/my_bar
git pull origin main

# Restart web app (from console)
touch /var/www/yourusername_pythonanywhere_com_wsgi.py

# View logs
tail -f ~/my_bar/backend/logs/app.log

# Check Python packages
pip list

# Load sample data
cd ~/my_bar/backend
python3 load_sample_ingredients.py
```

---

## Support and Resources

- **PythonAnywhere Help**: https://help.pythonanywhere.com/
- **PythonAnywhere MySQL Guide**: https://help.pythonanywhere.com/pages/MySQLdb/
- **Flask Deployment Guide**: https://flask.palletsprojects.com/en/latest/deploying/
- **MySQL Documentation**: https://dev.mysql.com/doc/
- **GitHub Repository**: https://github.com/aswani1manish/my_bar

---

## Quick Reference URLs

After deployment, your application will be accessible at:

- **Frontend**: `https://yourusername.pythonanywhere.com/`
- **Backend API**: `https://yourusername.pythonanywhere.com/api/`
- **Health Check**: `https://yourusername.pythonanywhere.com/api/health`
- **Ingredients**: `https://yourusername.pythonanywhere.com/api/ingredients`
- **Recipes**: `https://yourusername.pythonanywhere.com/api/recipes`
- **Collections**: `https://yourusername.pythonanywhere.com/api/collections`
- **Image Uploads**: `https://yourusername.pythonanywhere.com/api/uploads/<filename>`

---

**Congratulations!** Your Neighborhood Sips application is now deployed to the cloud! 🎉
