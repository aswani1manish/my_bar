#!/usr/bin/env python3
"""
Load cocktail recipes from bar-data-copy repository
https://github.com/aswani1manish/bar-data-copy/tree/main/data/cocktails

Each folder represents a recipe with:
- data.json: Recipe information including ingredients
- Image files: Recipe images
"""

import os
import sys
import json
import shutil
import uuid
from datetime import datetime
import mysql.connector
from config import Config

def find_recipe_folders(data_dir):
    """Find all recipe folders in the data directory"""
    cocktails_dir = os.path.join(data_dir, 'data', 'cocktails')
    
    if not os.path.exists(cocktails_dir):
        print(f"Error: Directory not found: {cocktails_dir}")
        return []
    
    recipe_folders = []
    for folder_name in os.listdir(cocktails_dir):
        folder_path = os.path.join(cocktails_dir, folder_name)
        if os.path.isdir(folder_path):
            data_json = os.path.join(folder_path, 'data.json')
            if os.path.exists(data_json):
                recipe_folders.append({
                    'name': folder_name,
                    'path': folder_path,
                    'data_file': data_json
                })
    
    return recipe_folders

def load_recipe_data(data_file):
    """Load recipe data from JSON file"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠ Error reading {data_file}: {e}")
        return None

def find_or_create_ingredient(cursor, conn, ingredient_data):
    """Find existing ingredient or create a new one"""
    ingredient_name = ingredient_data.get('name', '')
    
    if not ingredient_name:
        return None
    
    # Check if ingredient exists
    cursor.execute("SELECT id FROM ingredients WHERE name = %s", (ingredient_name,))
    result = cursor.fetchone()
    
    if result:
        return result['id']
    
    # Create new ingredient
    try:
        query = """
            INSERT INTO ingredients (name, description, category, tags, images, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        tags = []
        
        # Add category as tag if available
        if ingredient_data.get('category'):
            tags.append(ingredient_data['category'])
        
        # Add origin as tag if available
        if ingredient_data.get('origin'):
            tags.append(ingredient_data['origin'])
        
        params = (
            ingredient_name,
            ingredient_data.get('description', ''),
            ingredient_data.get('category', ''),
            json.dumps(tags),
            json.dumps([]),  # Empty images array
            now,
            now
        )
        
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        print(f"  ⚠ Error creating ingredient {ingredient_name}: {e}")
        return None

def copy_recipe_images(recipe_folder, upload_folder):
    """Copy recipe images to upload folder and return list of filenames"""
    images = []
    
    # Find all image files in the recipe folder
    for filename in os.listdir(recipe_folder):
        file_path = os.path.join(recipe_folder, filename)
        
        # Check if it's an image file
        if os.path.isfile(file_path) and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            try:
                # Generate a unique filename using timestamp and UUID (16 chars for better uniqueness)
                ext = os.path.splitext(filename)[1]
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = uuid.uuid4().hex[:16]
                unique_filename = f"recipe_{timestamp}_{unique_id}{ext}"
                dest_path = os.path.join(upload_folder, unique_filename)
                
                # Copy the image
                shutil.copy2(file_path, dest_path)
                images.append(unique_filename)
            except Exception as e:
                print(f"  ⚠ Error copying image {filename}: {e}")
    
    return images

def convert_recipe(recipe_data, recipe_folder, cursor, conn, upload_folder, copy_images=False):
    """Convert recipe from bar-data-copy format to my_bar format"""
    
    # Process ingredients
    ingredients_list = []
    for ing_data in recipe_data.get('ingredients', []):
        # Find or create the ingredient in the database
        ingredient_id = find_or_create_ingredient(cursor, conn, ing_data)
        
        if ingredient_id:
            # Format the ingredient with amount and unit
            ingredient_entry = {
                'id': ingredient_id,
                'name': ing_data.get('name', ''),
                'amount': ing_data.get('amount'),
                'units': ing_data.get('units', ''),
                'optional': ing_data.get('optional', False)
            }
            
            # Add note if available
            if ing_data.get('note'):
                ingredient_entry['note'] = ing_data['note']
            
            ingredients_list.append(ingredient_entry)
    
    # Copy images if requested
    images = []
    if copy_images:
        images = copy_recipe_images(recipe_folder, upload_folder)
    
    # Build tags list
    tags = recipe_data.get('tags', [])
    
    # Add method as tag if available
    if recipe_data.get('method'):
        tags.append(recipe_data['method'])
    
    # Add glass type as tag if available
    if recipe_data.get('glass'):
        tags.append(recipe_data['glass'])
    
    # Build instructions
    instructions = recipe_data.get('instructions', '')
    
    # Add garnish to instructions if available
    if recipe_data.get('garnish'):
        instructions += f"\n\nGarnish: {recipe_data['garnish']}"
    
    # Prepare recipe object
    recipe = {
        'name': recipe_data.get('name', ''),
        'description': recipe_data.get('description', ''),
        'ingredients': ingredients_list,
        'instructions': instructions,
        'tags': tags,
        'images': images,
        'source': recipe_data.get('source', ''),
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    return recipe

def load_recipes_to_db(data_dir, dry_run=False, copy_images=False):
    """Load recipes from bar-data-copy repository into MySQL database"""
    
    # Find all recipe folders
    print(f"\nScanning for recipes in: {data_dir}")
    recipe_folders = find_recipe_folders(data_dir)
    
    if not recipe_folders:
        print("No recipe folders found")
        return 0
    
    print(f"Found {len(recipe_folders)} recipe folders")
    
    if dry_run:
        print("\n=== DRY RUN MODE - No data will be saved ===\n")
    else:
        # Connect to MySQL
        config = Config()
        database_name = config.MYSQL_DATABASE  # Store this before connection attempt
        print(f"\nConnecting to MySQL at {config.MYSQL_HOST}:{config.MYSQL_PORT}")
        try:
            conn = mysql.connector.connect(
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                connection_timeout=30,
                autocommit=False
            )
            cursor = conn.cursor(dictionary=True)
            print("✓ Connected to MySQL")
        except mysql.connector.Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            print("Make sure MySQL is running and database is initialized (run init_db.py)!")
            return 0
        
        # Get upload folder path
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    # Process each recipe
    print(f"\nProcessing recipes...\n")
    loaded_count = 0
    skipped_count = 0
    
    for recipe_folder_info in recipe_folders:
        recipe_name = recipe_folder_info['name']
        
        # Load recipe data
        recipe_data = load_recipe_data(recipe_folder_info['data_file'])
        if not recipe_data:
            skipped_count += 1
            continue
        
        recipe_display_name = recipe_data.get('name', recipe_name)
        
        if dry_run:
            print(f"  ✓ Would load: {recipe_display_name}")
            ingredients_count = len(recipe_data.get('ingredients', []))
            print(f"    - {ingredients_count} ingredients")
            loaded_count += 1
        else:
            # Check if recipe already exists
            cursor.execute("SELECT id FROM recipes WHERE name = %s", (recipe_display_name,))
            existing = cursor.fetchone()
            if existing:
                print(f"  ⚠ Skipping {recipe_display_name}: Already exists")
                skipped_count += 1
                continue
            
            # Convert recipe
            try:
                recipe = convert_recipe(
                    recipe_data,
                    recipe_folder_info['path'],
                    cursor,
                    conn,
                    upload_folder,
                    copy_images=copy_images
                )
                
                # Insert into database
                query = """
                    INSERT INTO recipes (name, description, ingredients, instructions, tags, images, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    recipe['name'],
                    recipe['description'],
                    json.dumps(recipe['ingredients']),
                    recipe['instructions'],
                    json.dumps(recipe['tags']),
                    json.dumps(recipe['images']),
                    recipe['created_at'],
                    recipe['updated_at']
                )
                
                cursor.execute(query, params)
                conn.commit()
                
                print(f"  ✓ Loaded: {recipe_display_name}")
                print(f"    - {len(recipe['ingredients'])} ingredients")
                if copy_images:
                    print(f"    - {len(recipe['images'])} images")
                loaded_count += 1
                
            except Exception as e:
                print(f"  ✗ Error loading {recipe_display_name}: {e}")
                skipped_count += 1
    
    if not dry_run:
        cursor.close()
        conn.close()
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  - Total recipes found: {len(recipe_folders)}")
    print(f"  - Loaded: {loaded_count}")
    print(f"  - Skipped: {skipped_count}")
    
    if not dry_run:
        print(f"\n✓ Recipes loaded into '{database_name}' database")
    
    return loaded_count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Load cocktail recipes from bar-data-copy repository',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load recipes from cloned bar-data-copy repository (dry run)
  python load_recipes.py --data-dir /path/to/bar-data-copy --dry-run
  
  # Load recipes with images
  python load_recipes.py --data-dir /path/to/bar-data-copy --copy-images
  
  # Load recipes without images (faster)
  python load_recipes.py --data-dir /path/to/bar-data-copy
        """
    )
    parser.add_argument(
        '--data-dir',
        required=True,
        help='Path to bar-data-copy repository directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be loaded without actually loading'
    )
    parser.add_argument(
        '--copy-images',
        action='store_true',
        help='Copy recipe images to uploads folder (may take longer)'
    )
    
    args = parser.parse_args()
    
    # Validate data directory
    if not os.path.exists(args.data_dir):
        print(f"Error: Directory not found: {args.data_dir}")
        return 1
    
    print("=" * 60)
    print("Bar Data Copy Recipes Loader")
    print("Neighborhood Sips Application")
    print("=" * 60)
    
    count = load_recipes_to_db(
        args.data_dir,
        dry_run=args.dry_run,
        copy_images=args.copy_images
    )
    
    if count > 0 or args.dry_run:
        print(f"\n✓ Successfully processed {count} recipes")
        return 0
    else:
        print("\n⚠ No recipes were loaded")
        return 1

if __name__ == '__main__':
    sys.exit(main())
