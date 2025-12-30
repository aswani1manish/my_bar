# Deployment Checklist for Neighborhood Sips

Use this checklist to ensure a smooth deployment to the cloud.

## Pre-Deployment Preparation

### MongoDB Atlas Setup
- [ ] Create MongoDB Atlas account
- [ ] Create a new cluster (M0 Free Tier)
- [ ] Create database user with username and password
- [ ] Configure Network Access (allow 0.0.0.0/0 or specific IPs)
- [ ] Get connection string
- [ ] Create `neighborhood_sips` database
- [ ] Test connection from local machine

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
- [ ] Add MongoDB Atlas connection string to `.env`
- [ ] Set `DATABASE_NAME=neighborhood_sips`
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

### Initial Data
- [ ] Run `python3 load_sample_ingredients.py` (optional)
- [ ] Verify data loaded successfully

### Backend Testing
- [ ] Test health endpoint: `https://yourusername.pythonanywhere.com/api/health`
- [ ] Test ingredients endpoint: `https://yourusername.pythonanywhere.com/api/ingredients`
- [ ] Check error logs if issues occur
- [ ] Verify MongoDB connection works

## Frontend Deployment

### Configuration
- [ ] Run configuration script locally:
  ```bash
  ./configure_frontend.sh https://yourusername.pythonanywhere.com/api
  ```
- [ ] Verify `frontend/js/config.js` has correct API URL

### Deployment Option A: Serve from Backend
- [ ] Copy frontend to backend: `cp -r frontend backend/static`
- [ ] Update `app.py` to serve frontend routes
- [ ] Update `static/js/config.js` to use relative API URL (`/api`)
- [ ] Reload web app

### Deployment Option B: Separate Hosting
- [ ] Upload frontend to separate static hosting service
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
- [ ] Check MongoDB Atlas metrics
- [ ] Verify database connections close properly

### Security
- [ ] Verify `.env` file not exposed
- [ ] Confirm `FLASK_DEBUG=False`
- [ ] Check CORS settings are restrictive (not `*`)
- [ ] Verify HTTPS is working
- [ ] Test that only allowed origins can access API
- [ ] Review MongoDB Atlas Network Access rules

### Documentation
- [ ] Update README with deployment URL
- [ ] Document any custom configuration
- [ ] Note any issues encountered and solutions

## Troubleshooting Reference

If you encounter issues, check:

1. **Error Logs**: PythonAnywhere Web tab → Error log
2. **Server Log**: PythonAnywhere Web tab → Server log
3. **Browser Console**: F12 → Console tab
4. **MongoDB Connection**: Test from PythonAnywhere console
5. **CORS Issues**: Check `ALLOWED_ORIGINS` in `.env`
6. **Static Files**: Verify paths match your username

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
- [ ] MongoDB Atlas shows connections

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
