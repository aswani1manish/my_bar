# Deployment Checklist for Neighborhood Sips

Use this checklist to ensure a smooth deployment to the cloud.

## Pre-Deployment Preparation

### MySQL Database Setup
- [ ] Choose MySQL option: PythonAnywhere MySQL or External MySQL service
- [ ] For PythonAnywhere MySQL:
  - [ ] Set MySQL password in Databases tab
  - [ ] Note connection details (host, username, database format)
  - [ ] Create database: `yourusername$neighborhood_sips`
- [ ] For External MySQL:
  - [ ] Create MySQL database instance
  - [ ] Create database named `neighborhood_sips`
  - [ ] Create database user with privileges
  - [ ] Configure firewall for PythonAnywhere access
  - [ ] Note connection details (host, port, username, password)

### PythonAnywhere Setup
- [ ] Create PythonAnywhere account
- [ ] Note your PythonAnywhere username

## Backend Deployment

### Code Upload
- [ ] Upload backend code to PythonAnywhere or clone from Git
- [ ] Verify all files are present in `~/my_bar/backend/`

### Environment Setup
- [ ] Create virtual environment: `mkvirtualenv --python=/usr/bin/python3.10 my_bar_env`
- [ ] Activate environment: `workon my_bar_env`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify all packages installed correctly

### Configuration
- [ ] Create `.env` file in backend directory
- [ ] Add MySQL connection details to `.env`:
  - [ ] `MYSQL_HOST` (PythonAnywhere or external host)
  - [ ] `MYSQL_PORT` (usually 3306)
  - [ ] `MYSQL_USER` (your MySQL username)
  - [ ] `MYSQL_PASSWORD` (your MySQL password)
  - [ ] `MYSQL_DATABASE` (database name)
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Add PythonAnywhere domain to `ALLOWED_ORIGINS`
- [ ] Verify `.env` file is not committed to Git

### PythonAnywhere Web App
- [ ] Create new web app (Manual configuration, Python 3.10)
- [ ] Edit WSGI configuration file
- [ ] Update paths in WSGI file with your username
- [ ] Set virtualenv path: `/home/yourusername/.virtualenvs/my_bar_env`
- [ ] Add static files mapping for uploads:
  - URL: `/api/uploads/`
  - Directory: `/home/yourusername/my_bar/backend/uploads`
- [ ] Save all changes
- [ ] Click "Reload" button

### Database Initialization
- [ ] Run `python init_db.py` to create tables
- [ ] Verify tables created successfully:
  - [ ] ingredients
  - [ ] recipes
  - [ ] collections
- [ ] Reload web app after initialization

### Initial Data
- [ ] Run `python3 load_sample_ingredients.py` (optional)
- [ ] Verify data loaded successfully

### Backend Testing
- [ ] Test health endpoint: `https://yourusername.pythonanywhere.com/api/health`
- [ ] Test ingredients endpoint: `https://yourusername.pythonanywhere.com/api/ingredients`
- [ ] Check error logs if issues occur
- [ ] Verify MySQL connection works

## Frontend Deployment

### Configuration
- [ ] Run configuration script locally:
  ```bash
  ./configure_frontend.sh https://yourusername.pythonanywhere.com/api
  ```
- [ ] Verify `backend/static/js/config.js` has correct API URL

### Deployment Option A: Serve from Backend
- [ ] Frontend files are already in `backend/static`
- [ ] Update `app.py` to serve frontend routes (uncomment if needed)
- [ ] Update `static/js/config.js` to use relative API URL (`/api`)
- [ ] Reload web app

### Deployment Option B: Separate Hosting
- [ ] Upload `backend/static` directory to separate static hosting service
- [ ] Verify API URL is configured correctly
- [ ] Test CORS configuration

### Frontend Testing
- [ ] Access frontend URL in browser
- [ ] Verify homepage loads correctly
- [ ] Test navigation to all sections (Ingredients, Recipes, Collections)
- [ ] Test creating a new ingredient
- [ ] Test image upload functionality
- [ ] Test search and filter features
- [ ] Check browser console for any errors

## Post-Deployment

### Functionality Testing
- [ ] Create a new ingredient
- [ ] Upload image for ingredient
- [ ] Edit an ingredient
- [ ] Delete an ingredient
- [ ] Create a recipe with multiple ingredients
- [ ] Create a collection
- [ ] Test search functionality
- [ ] Test tag filtering
- [ ] Test on mobile device or responsive mode

### Performance & Monitoring
- [ ] Check page load times
- [ ] Verify images load correctly
- [ ] Monitor error logs
- [ ] Check MySQL database size and performance
- [ ] Verify database connections close properly

### Security
- [ ] Verify `.env` file not exposed
- [ ] Confirm `FLASK_DEBUG=False`
- [ ] Check CORS settings are restrictive (not `*`)
- [ ] Verify HTTPS is working
- [ ] Test that only allowed origins can access API
- [ ] Review MySQL access permissions
- [ ] Use strong MySQL password

### Documentation
- [ ] Update README with deployment URL
- [ ] Document any custom configuration
- [ ] Note any issues encountered and solutions

## Troubleshooting Reference

If you encounter issues, check:

1. **Error Logs**: PythonAnywhere Web tab → Error log
2. **Server Log**: PythonAnywhere Web tab → Server log
3. **Browser Console**: F12 → Console tab
4. **MySQL Connection**: Test from PythonAnywhere console with `python init_db.py`
5. **CORS Issues**: Check `ALLOWED_ORIGINS` in `.env`
6. **Static Files**: Verify paths match your username
7. **Database Tables**: Ensure `init_db.py` ran successfully

## Rollback Plan

If deployment fails:

- [ ] Keep local development environment working
- [ ] Document all changes made
- [ ] Have backup of database (if data was migrated)
- [ ] Know how to revert WSGI configuration
- [ ] Have previous working code version in Git

## Success Criteria

Deployment is successful when:

- [ ] Backend API responds at `/api/health`
- [ ] Frontend loads without errors
- [ ] Can create, read, update, delete ingredients
- [ ] Can create, read, update, delete recipes
- [ ] Can create, read, update, delete collections
- [ ] Images upload and display correctly
- [ ] Search and filter work properly
- [ ] Mobile responsive design works
- [ ] No errors in logs
- [ ] MySQL database connections working

---

**Deployment Date**: _______________

**Deployed By**: _______________

**URLs**:
- Frontend: _______________
- Backend API: _______________

**Notes**:
_______________________________________________
_______________________________________________
_______________________________________________
