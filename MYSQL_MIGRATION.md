# MongoDB to MySQL Migration Guide

## Overview
This guide helps you migrate your existing Neighborhood Sips data from MongoDB to MySQL.

## Prerequisites
- Python 3.8+
- MySQL 8.0+
- Both MongoDB and MySQL running (temporarily during migration)
- Access to your existing MongoDB database

## Step 1: Install New Dependencies

```bash
cd backend
source venv/bin/activate  # If using virtual environment
pip install -r requirements.txt
```

## Step 2: Setup MySQL Database

### Create Database and User
```bash
mysql -u root -p

CREATE DATABASE neighborhood_sips;
CREATE USER 'neighborhood_sips'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON neighborhood_sips.* TO 'neighborhood_sips'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Initialize Database Schema
```bash
python init_db.py
```

This creates the following tables:
- `ingredients` - Stores ingredient data
- `recipes` - Stores recipe data
- `collections` - Stores collection data

## Step 3: Configure Environment

Update your `.env` file with MySQL credentials:

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=neighborhood_sips
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=neighborhood_sips

# Keep MongoDB URI temporarily for migration
MONGO_URI=mongodb://localhost:27017/
```

## Step 4: Migrate Data (Optional)

If you have existing MongoDB data to migrate, create a migration script:

```python
#!/usr/bin/env python3
"""
Migrate data from MongoDB to MySQL
"""
import json
from datetime import datetime
from pymongo import MongoClient
import mysql.connector
from config import Config

# MongoDB connection (old)
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['neighborhood_sips']

# MySQL connection (new)
config = Config()
mysql_conn = mysql.connector.connect(
    host=config.MYSQL_HOST,
    port=config.MYSQL_PORT,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    database=config.MYSQL_DATABASE
)
mysql_cursor = mysql_conn.cursor()

# Migrate ingredients
print("Migrating ingredients...")
ingredients = list(mongo_db['ingredients'].find())
for ing in ingredients:
    query = """
        INSERT INTO ingredients (name, description, category, tags, images, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        ing.get('name'),
        ing.get('description', ''),
        ing.get('category', ''),
        json.dumps(ing.get('tags', [])),
        json.dumps(ing.get('images', [])),
        ing.get('created_at', datetime.utcnow()),
        ing.get('updated_at', datetime.utcnow())
    )
    mysql_cursor.execute(query, params)
print(f"✓ Migrated {len(ingredients)} ingredients")

# Migrate recipes
print("Migrating recipes...")
recipes = list(mongo_db['recipes'].find())
for recipe in recipes:
    query = """
        INSERT INTO recipes (name, description, ingredients, instructions, tags, images, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        recipe.get('name'),
        recipe.get('description', ''),
        json.dumps(recipe.get('ingredients', [])),
        recipe.get('instructions', ''),
        json.dumps(recipe.get('tags', [])),
        json.dumps(recipe.get('images', [])),
        recipe.get('created_at', datetime.utcnow()),
        recipe.get('updated_at', datetime.utcnow())
    )
    mysql_cursor.execute(query, params)
print(f"✓ Migrated {len(recipes)} recipes")

# Migrate collections
print("Migrating collections...")
collections = list(mongo_db['collections'].find())
for coll in collections:
    query = """
        INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        coll.get('name'),
        coll.get('description', ''),
        json.dumps(coll.get('recipe_ids', [])),
        json.dumps(coll.get('tags', [])),
        json.dumps(coll.get('images', [])),
        coll.get('created_at', datetime.utcnow()),
        coll.get('updated_at', datetime.utcnow())
    )
    mysql_cursor.execute(query, params)
print(f"✓ Migrated {len(collections)} collections")

mysql_conn.commit()
mysql_cursor.close()
mysql_conn.close()

print("\n✓ Migration completed successfully!")
```

Save this as `migrate_mongo_to_mysql.py` and run:
```bash
python migrate_mongo_to_mysql.py
```

## Step 5: Start Fresh (Alternative)

If you don't have data to migrate, simply load sample ingredients:

```bash
python load_sample_ingredients.py
```

This loads 34 common cocktail ingredients.

## Step 6: Verify Migration

Test the API to ensure everything works:

```bash
# Start the server
python app.py

# In another terminal, test endpoints
curl http://localhost:5000/api/health
curl http://localhost:5000/api/ingredients
curl http://localhost:5000/api/recipes
curl http://localhost:5000/api/collections
```

## Step 7: Update Frontend Configuration

If you're running the frontend separately, ensure it points to the correct backend URL. No changes are needed to the frontend code itself as the API endpoints remain the same.

## Key Changes

### Database Structure
- **MongoDB ObjectId** → **MySQL AUTO_INCREMENT INT**
  - IDs are now integers instead of strings
  - Frontend doesn't need changes as it works with both

### JSON Fields
MySQL stores arrays and objects as JSON columns:
- `tags` - JSON array
- `images` - JSON array  
- `ingredients` (in recipes) - JSON array
- `recipe_ids` (in collections) - JSON array

### Query Performance
- Indexed columns: `name`, `category`
- Full-text search uses SQL `LIKE` operator
- Tag filtering uses `JSON_CONTAINS` function

## Troubleshooting

### Connection Error
If you get "Access denied for user 'root'@'localhost'":
- Check MySQL credentials in `.env`
- Ensure MySQL user has proper permissions

### Table Not Found
If you get "Table doesn't exist" error:
- Run `python init_db.py` to create tables

### JSON Field Issues
If tags/images don't display properly:
- Ensure they're stored as JSON strings in the database
- Check that JSON fields are properly parsed in API responses

## Rollback

If you need to rollback to MongoDB:
1. Keep the MongoDB backup
2. Restore old version from git: `git checkout <previous-commit>`
3. Reinstall dependencies: `pip install -r requirements.txt`

## Support

For issues or questions, please open an issue on GitHub.
