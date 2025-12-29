from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
import base64
from datetime import datetime
import uuid
from PIL import Image, UnidentifiedImageError
import io

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['neighborhood_sips']

# Collections
ingredients_collection = db['ingredients']
recipes_collection = db['recipes']
collections_collection = db['collections']

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Helper function to save base64 image
def save_base64_image(base64_string, prefix='img'):
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Generate unique filename with UUID for security
        unique_id = uuid.uuid4().hex[:12]
        filename = f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{unique_id}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Resize if too large (max 1024x1024)
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save image
        image.save(filepath, 'PNG', optimize=True)
        
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
    
    query = {}
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        query['tags'] = {'$in': tag_list}
    
    ingredients = list(ingredients_collection.find(query))
    return jsonify([serialize_doc(ing) for ing in ingredients])

@app.route('/api/ingredients/<ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    ingredient = ingredients_collection.find_one({'_id': ObjectId(ingredient_id)})
    if ingredient:
        return jsonify(serialize_doc(ingredient))
    return jsonify({'error': 'Ingredient not found'}), 404

@app.route('/api/ingredients', methods=['POST'])
def create_ingredient():
    data = request.json
    
    # Handle image uploads
    images = []
    if 'images' in data and data['images']:
        for img_data in data['images']:
            if img_data:
                filename = save_base64_image(img_data, 'ingredient')
                if filename:
                    images.append(filename)
    
    ingredient = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'category': data.get('category', ''),
        'tags': data.get('tags', []),
        'images': images,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    result = ingredients_collection.insert_one(ingredient)
    ingredient['_id'] = str(result.inserted_id)
    return jsonify(ingredient), 201

@app.route('/api/ingredients/<ingredient_id>', methods=['PUT'])
def update_ingredient(ingredient_id):
    data = request.json
    
    # Get existing ingredient to preserve old images
    existing = ingredients_collection.find_one({'_id': ObjectId(ingredient_id)})
    images = existing.get('images', []) if existing else []
    
    # Handle new image uploads
    if 'images' in data and data['images']:
        for img_data in data['images']:
            if img_data and img_data.startswith('data:'):
                filename = save_base64_image(img_data, 'ingredient')
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
    
    update_data = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'category': data.get('category', ''),
        'tags': data.get('tags', []),
        'images': images,
        'updated_at': datetime.utcnow()
    }
    result = ingredients_collection.update_one(
        {'_id': ObjectId(ingredient_id)},
        {'$set': update_data}
    )
    if result.matched_count:
        ingredient = ingredients_collection.find_one({'_id': ObjectId(ingredient_id)})
        return jsonify(serialize_doc(ingredient))
    return jsonify({'error': 'Ingredient not found'}), 404

@app.route('/api/ingredients/<ingredient_id>', methods=['DELETE'])
def delete_ingredient(ingredient_id):
    result = ingredients_collection.delete_one({'_id': ObjectId(ingredient_id)})
    if result.deleted_count:
        return jsonify({'message': 'Ingredient deleted successfully'})
    return jsonify({'error': 'Ingredient not found'}), 404

# ============= RECIPES ENDPOINTS =============

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    search = request.args.get('search', '')
    tags = request.args.get('tags', '')
    
    query = {}
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        query['tags'] = {'$in': tag_list}
    
    recipes = list(recipes_collection.find(query))
    return jsonify([serialize_doc(recipe) for recipe in recipes])

@app.route('/api/recipes/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = recipes_collection.find_one({'_id': ObjectId(recipe_id)})
    if recipe:
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
                filename = save_base64_image(img_data, 'recipe')
                if filename:
                    images.append(filename)
    
    recipe = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'ingredients': data.get('ingredients', []),  # List of {ingredient_id, quantity, unit}
        'instructions': data.get('instructions', ''),
        'tags': data.get('tags', []),
        'images': images,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    result = recipes_collection.insert_one(recipe)
    recipe['_id'] = str(result.inserted_id)
    return jsonify(recipe), 201

@app.route('/api/recipes/<recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    data = request.json
    
    # Get existing recipe to preserve old images
    existing = recipes_collection.find_one({'_id': ObjectId(recipe_id)})
    images = existing.get('images', []) if existing else []
    
    # Handle new image uploads
    if 'images' in data and data['images']:
        for img_data in data['images']:
            if img_data and img_data.startswith('data:'):
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
    
    update_data = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'ingredients': data.get('ingredients', []),
        'instructions': data.get('instructions', ''),
        'tags': data.get('tags', []),
        'images': images,
        'updated_at': datetime.utcnow()
    }
    result = recipes_collection.update_one(
        {'_id': ObjectId(recipe_id)},
        {'$set': update_data}
    )
    if result.matched_count:
        recipe = recipes_collection.find_one({'_id': ObjectId(recipe_id)})
        return jsonify(serialize_doc(recipe))
    return jsonify({'error': 'Recipe not found'}), 404

@app.route('/api/recipes/<recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    result = recipes_collection.delete_one({'_id': ObjectId(recipe_id)})
    if result.deleted_count:
        return jsonify({'message': 'Recipe deleted successfully'})
    return jsonify({'error': 'Recipe not found'}), 404

# ============= COLLECTIONS ENDPOINTS =============

@app.route('/api/collections', methods=['GET'])
def get_collections():
    search = request.args.get('search', '')
    tags = request.args.get('tags', '')
    
    query = {}
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        query['tags'] = {'$in': tag_list}
    
    collections = list(collections_collection.find(query))
    return jsonify([serialize_doc(coll) for coll in collections])

@app.route('/api/collections/<collection_id>', methods=['GET'])
def get_collection(collection_id):
    collection = collections_collection.find_one({'_id': ObjectId(collection_id)})
    if collection:
        return jsonify(serialize_doc(collection))
    return jsonify({'error': 'Collection not found'}), 404

@app.route('/api/collections', methods=['POST'])
def create_collection():
    data = request.json
    
    # Handle image uploads
    images = []
    if 'images' in data and data['images']:
        for img_data in data['images']:
            if img_data:
                filename = save_base64_image(img_data, 'collection')
                if filename:
                    images.append(filename)
    
    collection = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'recipe_ids': data.get('recipe_ids', []),  # List of recipe IDs
        'tags': data.get('tags', []),
        'images': images,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    result = collections_collection.insert_one(collection)
    collection['_id'] = str(result.inserted_id)
    return jsonify(collection), 201

@app.route('/api/collections/<collection_id>', methods=['PUT'])
def update_collection(collection_id):
    data = request.json
    
    # Get existing collection to preserve old images
    existing = collections_collection.find_one({'_id': ObjectId(collection_id)})
    images = existing.get('images', []) if existing else []
    
    # Handle new image uploads
    if 'images' in data and data['images']:
        for img_data in data['images']:
            if img_data and img_data.startswith('data:'):
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
    
    update_data = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'recipe_ids': data.get('recipe_ids', []),
        'tags': data.get('tags', []),
        'images': images,
        'updated_at': datetime.utcnow()
    }
    result = collections_collection.update_one(
        {'_id': ObjectId(collection_id)},
        {'$set': update_data}
    )
    if result.matched_count:
        collection = collections_collection.find_one({'_id': ObjectId(collection_id)})
        return jsonify(serialize_doc(collection))
    return jsonify({'error': 'Collection not found'}), 404

@app.route('/api/collections/<collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    result = collections_collection.delete_one({'_id': ObjectId(collection_id)})
    if result.deleted_count:
        return jsonify({'message': 'Collection deleted successfully'})
    return jsonify({'error': 'Collection not found'}), 404

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'app': 'Neighborhood Sips'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
