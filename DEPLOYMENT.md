# Cloud Deployment Guide for Neighborhood Sips

This guide provides step-by-step instructions for deploying the Neighborhood Sips application to the cloud:
- **Backend**: PythonAnywhere (Flask application)
- **Database**: MongoDB Atlas (Cloud MongoDB)
- **Frontend**: PythonAnywhere (Static files)

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Part 1: MongoDB Atlas Setup](#part-1-mongodb-atlas-setup)
3. [Part 2: Backend Deployment on PythonAnywhere](#part-2-backend-deployment-on-pythonanywhere)
4. [Part 3: Frontend Deployment on PythonAnywhere](#part-3-frontend-deployment-on-pythonanywhere)
5. [Part 4: Testing the Deployment](#part-4-testing-the-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have:

1. **MongoDB Atlas Account** (free tier available)
   - Sign up at: https://www.mongodb.com/cloud/atlas/register

2. **PythonAnywhere Account** (free tier available)
   - Sign up at: https://www.pythonanywhere.com/registration/register/beginner/

3. **Git** installed on your local machine (to clone/push code)

4. **Your application code** ready to deploy

---

## Part 1: MongoDB Atlas Setup

### Step 1.1: Create a MongoDB Atlas Cluster

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)

2. Click **"Build a Database"** or **"Create"**

3. Choose **"Shared"** (Free tier - M0)

4. Select your cloud provider and region (choose the closest to your users)

5. Click **"Create Cluster"** (this may take a few minutes)

### Step 1.2: Configure Database Access

1. In the left sidebar, click **"Database Access"**

2. Click **"Add New Database User"**

3. Choose **"Password"** authentication

4. Set username and password (save these securely!)
   ```
   Example:
   Username: neighborhood_sips_user
   Password: YourSecurePassword123!
   ```

5. Set **"Built-in Role"** to **"Read and write to any database"**

6. Click **"Add User"**

### Step 1.3: Configure Network Access

1. In the left sidebar, click **"Network Access"**

2. Click **"Add IP Address"**

3. Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - Note: For production, restrict this to PythonAnywhere IP ranges

4. Click **"Confirm"**

### Step 1.4: Get Your Connection String

1. Go back to **"Database"** in the left sidebar

2. Click **"Connect"** on your cluster

3. Choose **"Connect your application"**

4. Copy the connection string (it looks like this):
   ```
   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

5. Replace `<password>` with your actual database user password

6. **Save this connection string** - you'll need it for the backend configuration

### Step 1.5: Create the Database

1. Click **"Browse Collections"** on your cluster

2. Click **"Add My Own Data"**

3. Database name: `neighborhood_sips`

4. Collection name: `ingredients` (we'll create others automatically)

5. Click **"Create"**

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
   ```bash
   # MongoDB Atlas Connection String
   MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   
   # Database name
   DATABASE_NAME=neighborhood_sips
   
   # Flask Configuration
   FLASK_ENV=production
   FLASK_DEBUG=False
   
   # CORS Configuration (update with your PythonAnywhere domain)
   ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com
   
   # Upload Configuration
   MAX_CONTENT_LENGTH=16777216
   UPLOAD_FOLDER=uploads
   ```

3. Save and exit (Ctrl+X, then Y, then Enter)

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

### Step 2.8: Reload Web App

1. Scroll to the top of the **"Web"** tab

2. Click the big green **"Reload"** button

3. Your backend API should now be live at: `https://yourusername.pythonanywhere.com/api/`

### Step 2.9: Load Sample Data (Optional)

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
1. Check the error log on PythonAnywhere
2. Verify your `.env` file has the correct MongoDB connection string
3. Ensure virtual environment is activated and all dependencies are installed
4. Check WSGI file path matches your username

### Issue: "MongoDB connection timeout"

**Solution:**
1. Verify MongoDB Atlas Network Access allows PythonAnywhere IPs
2. Check your connection string is correct (username, password, cluster URL)
3. Ensure database user has proper permissions
4. Test connection from PythonAnywhere console:
   ```python
   from pymongo import MongoClient
   client = MongoClient("your-connection-string")
   print(client.server_info())
   ```

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
# Required
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=neighborhood_sips

# Optional (with defaults)
FLASK_ENV=production
FLASK_DEBUG=False
ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com
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

- [ ] Change MongoDB password to a strong password
- [ ] Restrict MongoDB Atlas Network Access to specific IPs (PythonAnywhere ranges)
- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Use specific ALLOWED_ORIGINS (not `*`)
- [ ] Enable HTTPS (PythonAnywhere provides this by default)
- [ ] Keep `.env` file secure (never commit to Git)
- [ ] Regularly update dependencies for security patches
- [ ] Set up database backups in MongoDB Atlas
- [ ] Monitor application logs for errors

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
- **MongoDB Atlas Documentation**: https://docs.atlas.mongodb.com/
- **Flask Deployment Guide**: https://flask.palletsprojects.com/en/latest/deploying/
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
