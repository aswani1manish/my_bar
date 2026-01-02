from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.pooling import MySQLConnectionPool
import os
import base64
from datetime import datetime
import uuid
from PIL import Image, UnidentifiedImageError
from PIL.ImageOps import exif_transpose
import io
import json
import re
from config import Config

app = Flask(__name__)

# Load configuration from environment variables
config = Config()
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Configure CORS with allowed origins
if config.ALLOWED_ORIGINS == ['*']:
    CORS(app)
else:
    CORS(app, origins=config.ALLOWED_ORIGINS)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), config.UPLOAD_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL Configuration with connection pooling
try:
    db_pool = MySQLConnectionPool(
        pool_name="neighborhood_sips_pool",
        pool_size=5,
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        autocommit=False,
        consume_results=True
    )
    # Test connection
    conn = db_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchall()  # Consume results
    cursor.close()
    conn.close()
    print(f"✓ Connected to MySQL: {config.MYSQL_DATABASE}")
except MySQLError as e:
    print(f"✗ MySQL connection error: {e}")
    print(f"  Host: {config.MYSQL_HOST}:{config.MYSQL_PORT}")
    print(f"  Database: {config.MYSQL_DATABASE}")
    print(f"  NOTE: Application will start but database operations will fail.")
    print(f"  Please ensure MySQL is running and database is initialized (run init_db.py).")
    db_pool = None

# Helper function to get database connection
def get_db_connection():
    """Get a connection from the pool"""
    if db_pool is None:
        raise Exception("Database connection pool is not initialized")
    return db_pool.get_connection()

# Helper function to parse JSON field
def parse_json_field(value):
    """Parse JSON field from MySQL that could be str, bytes, bytearray, or already parsed"""
    if value is None:
        return None
    # If already a list or dict, return as-is
    if isinstance(value, (list, dict)):
        return value
    # If bytes or bytearray, decode to string first
    if isinstance(value, (bytes, bytearray)):
        value = value.decode('utf-8')
    # If string, parse as JSON
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return value
    # For any other type, return as-is
    return value

# Helper function to serialize document
def serialize_doc(doc):
    """Convert database row to dictionary with proper serialization"""
    if doc is None:
        return None
    # Convert to dict if it's a tuple/list (from cursor)
    if isinstance(doc, (tuple, list)):
        return doc
    # Handle datetime objects
    result = {}
    for key, value in doc.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, (bytes, bytearray)):
            result[key] = value.decode('utf-8')
        else:
            result[key] = value
    return result

# Helper function to sanitize filename
def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal and other security issues.
    Preserves original filename while ensuring safety.
    """
    if not filename:
        return None
    
    # Get the basename to prevent directory traversal
    filename = os.path.basename(filename)
    
    # Remove any remaining path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Replace any potentially problematic characters but keep alphanumeric, dots, dashes, underscores
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
    
    # Remove any leading/trailing whitespace or dots
    filename = filename.strip().strip('.')
    
    # If filename is empty after sanitization, return None
    if not filename:
        return None
    
    return filename

# Helper function to save base64 image
def save_base64_image(base64_string, prefix='img', original_filename=None):
    """
    Save base64 image to disk, preserving original filename if provided.
    Also preserves EXIF orientation metadata.
    
    Args:
        base64_string: Base64 encoded image data
        prefix: Prefix to use if no original filename (default: 'img')
        original_filename: Original filename to preserve (optional)
    
    Returns:
        Saved filename or None on error
    """
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        # Decode base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))

        # Preserve EXIF orientation by automatically rotating the image
        # This ensures images display with correct orientation
        image = exif_transpose(image)

        # Determine filename
        if original_filename:
            # Sanitize the original filename
            safe_filename = sanitize_filename(original_filename)
            if safe_filename:
                # Keep the original extension if present, otherwise use the image format
                name_part, ext_part = os.path.splitext(safe_filename)
                if not ext_part:
                    # No extension, add one based on image format
                    ext_part = f".{image.format.lower()}" if image.format else ".png"
                filename = f"{name_part}{ext_part}"
            else:
                # Fallback if sanitization fails
                filename = f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        else:
            # No original filename provided, use prefix with timestamp
            filename = f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"

        # Handle filename collisions by adding a counter
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter = 1
        name_part, ext_part = os.path.splitext(filename)
        while os.path.exists(filepath):
            filename = f"{name_part}_{counter}{ext_part}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1

        # Resize if too large (max 1024x1024)
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Determine format for saving - preserve original format when possible
        save_format = image.format if image.format in ['JPEG', 'PNG', 'GIF'] else 'PNG'
        
        # Save image with appropriate options
        if save_format == 'JPEG':
            image.save(filepath, save_format, optimize=True, quality=85)
        else:
            image.save(filepath, save_format, optimize=True)

        return filename
    except (IOError, ValueError, UnidentifiedImageError) as e:
        print(f"Error saving image: {e}")
        return None

# Serve uploaded images
@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============= INGREDIENTS ENDPOINTS =============

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    search = request.args.get('search', '')
    tags = request.args.get('tags', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM ingredients WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE %s OR description LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        # Check if any of the tags are in the JSON array
        tag_conditions = []
        for tag in tag_list:
            tag_conditions.append("JSON_CONTAINS(tags, %s)")
            params.append(json.dumps(tag))
        query += f" AND ({' OR '.join(tag_conditions)})"

    query += " ORDER BY name ASC"

    cursor.execute(query, params)
    ingredients = cursor.fetchall()

    # Parse JSON fields
    for ing in ingredients:
        ing['tags'] = parse_json_field(ing.get('tags'))
        ing['images'] = parse_json_field(ing.get('images'))

    cursor.close()
    conn.close()

    return jsonify(ingredients)

@app.route('/api/ingredients/<int:ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM ingredients WHERE id = %s", (ingredient_id,))
    ingredient = cursor.fetchone()

    cursor.close()
    conn.close()

    if ingredient:
        # Parse JSON fields
        ingredient['tags'] = parse_json_field(ingredient.get('tags'))
        ingredient['images'] = parse_json_field(ingredient.get('images'))
        return jsonify(serialize_doc(ingredient))
    return jsonify({'error': 'Ingredient not found'}), 404

# @app.route('/api/ingredients', methods=['POST'])
# def create_ingredient():
#     data = request.json

#     # Handle image uploads
#     images = []
#     if 'images' in data and data['images']:
#         for img_data in data['images']:
#             if img_data:
#                 filename = save_base64_image(img_data, 'ingredient')
#                 if filename:
#                     images.append(filename)

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     query = """
#         INSERT INTO ingredients (name, description, category, tags, images, created_at, updated_at)
#         VALUES (%s, %s, %s, %s, %s, %s, %s)
#     """
#     now = datetime.utcnow()
#     params = (
#         data.get('name'),
#         data.get('description', ''),
#         data.get('category', ''),
#         json.dumps(data.get('tags', [])),
#         json.dumps(images),
#         now,
#         now
#     )

#     cursor.execute(query, params)
#     conn.commit()
#     ingredient_id = cursor.lastrowid

#     cursor.close()
#     conn.close()

#     ingredient = {
#         'id': ingredient_id,
#         'name': data.get('name'),
#         'description': data.get('description', ''),
#         'category': data.get('category', ''),
#         'tags': data.get('tags', []),
#         'images': images,
#         'created_at': now.isoformat(),
#         'updated_at': now.isoformat()
#     }

#     return jsonify(ingredient), 201

# @app.route('/api/ingredients/<int:ingredient_id>', methods=['PUT'])
# def update_ingredient(ingredient_id):
#     data = request.json

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     # Get existing ingredient to preserve old images
#     cursor.execute("SELECT images FROM ingredients WHERE id = %s", (ingredient_id,))
#     existing = cursor.fetchone()

#     if not existing:
#         cursor.close()
#         conn.close()
#         return jsonify({'error': 'Ingredient not found'}), 404

#     images = json.loads(existing['images']) if isinstance(existing['images'], str) else (existing['images'] or [])

#     # Handle new image uploads
#     if 'images' in data and data['images']:
#         for img_data in data['images']:
#             if img_data and img_data.startswith('data:'):
#                 filename = save_base64_image(img_data, 'ingredient')
#                 if filename:
#                     images.append(filename)
#             elif img_data:  # Existing image filename
#                 if img_data not in images:
#                     images.append(img_data)

#     # Handle image removals
#     if 'removed_images' in data and data['removed_images']:
#         for img in data['removed_images']:
#             if img in images:
#                 images.remove(img)
#                 # Delete file from disk
#                 try:
#                     os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
#                 except:
#                     pass

#     query = """
#         UPDATE ingredients
#         SET name = %s, description = %s, category = %s, tags = %s, images = %s, updated_at = %s
#         WHERE id = %s
#     """
#     now = datetime.utcnow()
#     params = (
#         data.get('name'),
#         data.get('description', ''),
#         data.get('category', ''),
#         json.dumps(data.get('tags', [])),
#         json.dumps(images),
#         now,
#         ingredient_id
#     )

#     cursor.execute(query, params)
#     conn.commit()

#     # Fetch updated ingredient
#     cursor.execute("SELECT * FROM ingredients WHERE id = %s", (ingredient_id,))
#     ingredient = cursor.fetchone()

#     cursor.close()
#     conn.close()

#     if ingredient:
#         # Parse JSON fields
#         if ingredient.get('tags'):
#             ingredient['tags'] = json.loads(ingredient['tags']) if isinstance(ingredient['tags'], str) else ingredient['tags']
#         if ingredient.get('images'):
#             ingredient['images'] = json.loads(ingredient['images']) if isinstance(ingredient['images'], str) else ingredient['images']
#         return jsonify(serialize_doc(ingredient))
#     return jsonify({'error': 'Ingredient not found'}), 404

# @app.route('/api/ingredients/<int:ingredient_id>', methods=['DELETE'])
# def delete_ingredient(ingredient_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
#     deleted_count = cursor.rowcount
#     conn.commit()

#     cursor.close()
#     conn.close()

#     if deleted_count:
#         return jsonify({'message': 'Ingredient deleted successfully'})
#     return jsonify({'error': 'Ingredient not found'}), 404

@app.route('/api/ingredients/<int:ingredient_id>/bar-shelf', methods=['PATCH'])
def update_ingredient_bar_shelf(ingredient_id):
    """Update only the bar_shelf_availability field for an ingredient"""
    data = request.json
    bar_shelf_availability = data.get('bar_shelf_availability')
    
    # Validate input
    if bar_shelf_availability not in ['Y', 'N']:
        return jsonify({'error': 'bar_shelf_availability must be either "Y" or "N"'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Update bar_shelf_availability
    cursor.execute(
        "UPDATE ingredients SET bar_shelf_availability = %s WHERE id = %s",
        (bar_shelf_availability, ingredient_id)
    )
    
    # Check if any rows were affected
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Ingredient not found'}), 404
    
    conn.commit()
    
    # Fetch updated ingredient
    cursor.execute("SELECT * FROM ingredients WHERE id = %s", (ingredient_id,))
    ingredient = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    # Parse JSON fields
    ingredient['tags'] = parse_json_field(ingredient.get('tags'))
    ingredient['images'] = parse_json_field(ingredient.get('images'))
    return jsonify(serialize_doc(ingredient))

# ============= RECIPES ENDPOINTS =============

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    search = request.args.get('search', '')
    tags = request.args.get('tags', '')
    bar_shelf_mode = request.args.get('bar_shelf_mode', '').upper()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM recipes WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE %s OR description LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        tag_conditions = []
        for tag in tag_list:
            tag_conditions.append("JSON_CONTAINS(LOWER(tags), LOWER(%s))")
            params.append(json.dumps(tag))
        query += f" AND ({' AND '.join(tag_conditions)})"

    query += " ORDER BY name ASC"

    cursor.execute(query, params)
    recipes = cursor.fetchall()

    # Parse JSON fields
    for recipe in recipes:
        recipe['tags'] = parse_json_field(recipe.get('tags'))
        recipe['images'] = parse_json_field(recipe.get('images'))
        recipe['ingredients'] = parse_json_field(recipe.get('ingredients'))

    # Filter recipes based on bar shelf availability if bar_shelf_mode is 'Y'
    if bar_shelf_mode == 'Y':
        # Optimize by fetching all ingredient availabilities in one query
        # First, collect all unique ingredient names from all recipes
        all_ingredient_names = set()
        for recipe in recipes:
            ingredients = recipe.get('ingredients')
            if ingredients:
                for ingredient in ingredients:
                    ingredient_name = ingredient.get('name', '')
                    if ingredient_name:
                        all_ingredient_names.add(ingredient_name)
        
        # Fetch all ingredient availabilities in a single query
        ingredient_availability = {}
        if all_ingredient_names:
            # Create placeholders for IN clause
            placeholders = ', '.join(['%s'] * len(all_ingredient_names))
            query = f"SELECT name, bar_shelf_availability FROM ingredients WHERE name IN ({placeholders})"
            cursor.execute(query, tuple(all_ingredient_names))
            results = cursor.fetchall()
            for result in results:
                ingredient_availability[result['name']] = result.get('bar_shelf_availability', 'N')
        
        # Now filter recipes based on the fetched availability data
        filtered_recipes = []
        for recipe in recipes:
            ingredients = recipe.get('ingredients')
            # Only include recipes that have ingredients
            if ingredients:
                # Check if all ingredients are available on bar shelf
                all_available = True
                for ingredient in ingredients:
                    ingredient_name = ingredient.get('name', '')
                    if not ingredient_name:
                        # Exclude recipe if ingredient has no name (data integrity issue)
                        all_available = False
                        break
                    # Check availability from our pre-fetched data
                    if ingredient_availability.get(ingredient_name) != 'Y':
                        # Exclude recipe if ingredient not found or not available
                        all_available = False
                        break
                
                if all_available:
                    filtered_recipes.append(recipe)
        recipes = filtered_recipes

    cursor.close()
    conn.close()

    return jsonify(recipes)

@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
    recipe = cursor.fetchone()

    cursor.close()
    conn.close()

    if recipe:
        # Parse JSON fields
        recipe['tags'] = parse_json_field(recipe.get('tags'))
        recipe['images'] = parse_json_field(recipe.get('images'))
        recipe['ingredients'] = parse_json_field(recipe.get('ingredients'))
        return jsonify(serialize_doc(recipe))
    return jsonify({'error': 'Recipe not found'}), 404

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    data = request.json

    # Handle image uploads
    images = []
    if 'images' in data and data['images']:
        for img_data in data['images']:
            if img_data:
                # Check if image data includes filename (new format: {"data": "...", "filename": "..."})
                if isinstance(img_data, dict) and 'data' in img_data:
                    filename = save_base64_image(
                        img_data['data'], 
                        'recipe', 
                        img_data.get('filename')
                    )
                else:
                    # Legacy format: just base64 string
                    filename = save_base64_image(img_data, 'recipe')
                
                if filename:
                    images.append(filename)

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO recipes (name, description, ingredients, instructions, tags, images, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    now = datetime.utcnow()
    params = (
        data.get('name'),
        data.get('description', ''),
        json.dumps(data.get('ingredients', [])),
        data.get('instructions', ''),
        json.dumps(data.get('tags', [])),
        json.dumps(images),
        now,
        now
    )

    cursor.execute(query, params)
    conn.commit()
    recipe_id = cursor.lastrowid

    cursor.close()
    conn.close()

    recipe = {
        'id': recipe_id,
        'name': data.get('name'),
        'description': data.get('description', ''),
        'ingredients': data.get('ingredients', []),
        'instructions': data.get('instructions', ''),
        'tags': data.get('tags', []),
        'images': images,
        'created_at': now.isoformat(),
        'updated_at': now.isoformat()
    }

    return jsonify(recipe), 201

@app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get existing recipe to preserve old images
    cursor.execute("SELECT images FROM recipes WHERE id = %s", (recipe_id,))
    existing = cursor.fetchone()

    if not existing:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404

    images = parse_json_field(existing['images']) or []

    # Handle new image uploads
    if 'images' in data and data['images']:
        for img_data in data['images']:
            # Check if it's a new image (starts with 'data:' or is dict with data field)
            if isinstance(img_data, dict) and 'data' in img_data:
                # New format with filename
                filename = save_base64_image(
                    img_data['data'], 
                    'recipe', 
                    img_data.get('filename')
                )
                if filename:
                    images.append(filename)
            elif isinstance(img_data, str) and img_data.startswith('data:'):
                # Legacy format: just base64 string
                filename = save_base64_image(img_data, 'recipe')
                if filename:
                    images.append(filename)
            elif img_data:  # Existing image filename
                if img_data not in images:
                    images.append(img_data)

    # Handle image removals
    if 'removed_images' in data and data['removed_images']:
        for img in data['removed_images']:
            if img in images:
                images.remove(img)
                # Delete file from disk
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
                except:
                    pass

    query = """
        UPDATE recipes
        SET name = %s, description = %s, ingredients = %s, instructions = %s, tags = %s, images = %s, updated_at = %s
        WHERE id = %s
    """
    now = datetime.utcnow()
    params = (
        data.get('name'),
        data.get('description', ''),
        json.dumps(data.get('ingredients', [])),
        data.get('instructions', ''),
        json.dumps(data.get('tags', [])),
        json.dumps(images),
        now,
        recipe_id
    )

    cursor.execute(query, params)
    conn.commit()

    # Fetch updated recipe
    cursor.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
    recipe = cursor.fetchone()

    cursor.close()
    conn.close()

    if recipe:
        # Parse JSON fields
        recipe['tags'] = parse_json_field(recipe.get('tags'))
        recipe['images'] = parse_json_field(recipe.get('images'))
        recipe['ingredients'] = parse_json_field(recipe.get('ingredients'))
        return jsonify(serialize_doc(recipe))
    return jsonify({'error': 'Recipe not found'}), 404

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
    deleted_count = cursor.rowcount
    conn.commit()

    cursor.close()
    conn.close()

    if deleted_count:
        return jsonify({'message': 'Recipe deleted successfully'})
    return jsonify({'error': 'Recipe not found'}), 404

# ============= COLLECTIONS ENDPOINTS =============

@app.route('/api/collections', methods=['GET'])
def get_collections():
    search = request.args.get('search', '')
    tags = request.args.get('tags', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM collections WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE %s OR description LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        tag_conditions = []
        for tag in tag_list:
            tag_conditions.append("JSON_CONTAINS(tags, %s)")
            params.append(json.dumps(tag))
        query += f" AND ({' OR '.join(tag_conditions)})"

    query += " ORDER BY name ASC"

    cursor.execute(query, params)
    collections = cursor.fetchall()

    # Parse JSON fields
    for coll in collections:
        coll['tags'] = parse_json_field(coll.get('tags'))
        coll['images'] = parse_json_field(coll.get('images'))
        coll['recipe_ids'] = parse_json_field(coll.get('recipe_ids'))

    cursor.close()
    conn.close()

    return jsonify(collections)

@app.route('/api/collections/<int:collection_id>', methods=['GET'])
def get_collection(collection_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM collections WHERE id = %s", (collection_id,))
    collection = cursor.fetchone()

    cursor.close()
    conn.close()

    if collection:
        # Parse JSON fields
        collection['tags'] = parse_json_field(collection.get('tags'))
        collection['images'] = parse_json_field(collection.get('images'))
        collection['recipe_ids'] = parse_json_field(collection.get('recipe_ids'))
        return jsonify(serialize_doc(collection))
    return jsonify({'error': 'Collection not found'}), 404

# @app.route('/api/collections', methods=['POST'])
# def create_collection():
#     data = request.json

#     # Handle image uploads
#     images = []
#     if 'images' in data and data['images']:
#         for img_data in data['images']:
#             if img_data:
#                 filename = save_base64_image(img_data, 'collection')
#                 if filename:
#                     images.append(filename)

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     query = """
#         INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
#         VALUES (%s, %s, %s, %s, %s, %s, %s)
#     """
#     now = datetime.utcnow()
#     params = (
#         data.get('name'),
#         data.get('description', ''),
#         json.dumps(data.get('recipe_ids', [])),
#         json.dumps(data.get('tags', [])),
#         json.dumps(images),
#         now,
#         now
#     )

#     cursor.execute(query, params)
#     conn.commit()
#     collection_id = cursor.lastrowid

#     cursor.close()
#     conn.close()

#     collection = {
#         'id': collection_id,
#         'name': data.get('name'),
#         'description': data.get('description', ''),
#         'recipe_ids': data.get('recipe_ids', []),
#         'tags': data.get('tags', []),
#         'images': images,
#         'created_at': now.isoformat(),
#         'updated_at': now.isoformat()
#     }

#     return jsonify(collection), 201

@app.route('/api/collections/<int:collection_id>', methods=['PUT'])
def update_collection(collection_id):
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get existing collection to preserve old images
    cursor.execute("SELECT images FROM collections WHERE id = %s", (collection_id,))
    existing = cursor.fetchone()

    if not existing:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Collection not found'}), 404

    images = parse_json_field(existing['images']) or []

    # Handle new image uploads
    if 'images' in data and data['images']:
        for img_data in data['images']:
            # Check if it's a new image (starts with 'data:' or is dict with data field)
            if isinstance(img_data, dict) and 'data' in img_data:
                # New format with filename
                filename = save_base64_image(
                    img_data['data'], 
                    'collection', 
                    img_data.get('filename')
                )
                if filename:
                    images.append(filename)
            elif isinstance(img_data, str) and img_data.startswith('data:'):
                # Legacy format: just base64 string
                filename = save_base64_image(img_data, 'collection')
                if filename:
                    images.append(filename)
            elif img_data:  # Existing image filename
                if img_data not in images:
                    images.append(img_data)

    # Handle image removals
    if 'removed_images' in data and data['removed_images']:
        for img in data['removed_images']:
            if img in images:
                images.remove(img)
                # Delete file from disk
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
                except:
                    pass

    query = """
        UPDATE collections
        SET name = %s, description = %s, recipe_ids = %s, tags = %s, images = %s, updated_at = %s
        WHERE id = %s
    """
    now = datetime.utcnow()
    params = (
        data.get('name'),
        data.get('description', ''),
        json.dumps(data.get('recipe_ids', [])),
        json.dumps(data.get('tags', [])),
        json.dumps(images),
        now,
        collection_id
    )

    cursor.execute(query, params)
    conn.commit()

    # Fetch updated collection
    cursor.execute("SELECT * FROM collections WHERE id = %s", (collection_id,))
    collection = cursor.fetchone()

    cursor.close()
    conn.close()

    if collection:
        # Parse JSON fields
        collection['tags'] = parse_json_field(collection.get('tags'))
        collection['images'] = parse_json_field(collection.get('images'))
        collection['recipe_ids'] = parse_json_field(collection.get('recipe_ids'))
        return jsonify(serialize_doc(collection))
    return jsonify({'error': 'Collection not found'}), 404

# @app.route('/api/collections/<int:collection_id>', methods=['DELETE'])
# def delete_collection(collection_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("DELETE FROM collections WHERE id = %s", (collection_id,))
#     deleted_count = cursor.rowcount
#     conn.commit()

#     cursor.close()
#     conn.close()

#     if deleted_count:
#         return jsonify({'message': 'Collection deleted successfully'})
#     return jsonify({'error': 'Collection not found'}), 404

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'app': 'Neighborhood Sips'})

# ============= FRONTEND SERVING (OPTIONAL) =============
# Uncomment these routes to serve frontend from the same Flask app
# This is useful for PythonAnywhere deployment where you want everything in one app
#
# Prerequisites:
# 1. Frontend files are already in backend/static directory
# 2. Update static/js/config.js to use relative API URL: apiUrl: '/api'
#
@app.route('/')
def index():
 return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
 try:
     return send_from_directory('static', path)
 except:
     # For SPA routing, return index.html for unknown routes
     return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
