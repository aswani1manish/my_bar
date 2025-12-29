#!/usr/bin/env python3
"""
Load ingredients from Bar Assistant data repository
https://github.com/bar-assistant/data/tree/v5/data/ingredients
"""

import os
import sys
import json
import requests
from datetime import datetime
from pymongo import MongoClient

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')

# Bar Assistant data repository - using direct raw URLs
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/bar-assistant/data/v5/data/ingredients"

# List of known ingredient files from the repository
# We'll fetch this list directly from the repository's file listing
INGREDIENT_FILES_URL = "https://raw.githubusercontent.com/bar-assistant/data/v5/data/ingredients/_files.json"

def fetch_ingredient_files():
    """Fetch list of ingredient files from Bar Assistant"""
    print("Fetching ingredient files from Bar Assistant repository...")
    
    try:
        # First, try to get the _files.json if it exists
        response = requests.get(INGREDIENT_FILES_URL, timeout=10)
        if response.status_code == 200:
            files = response.json()
            print(f"Found {len(files)} ingredient files from _files.json")
            return files
    except:
        pass
    
    # If _files.json doesn't exist, use a predefined list of common ingredients
    # This is a fallback approach - we'll fetch the main ingredients file
    print("Fetching main ingredients list...")
    try:
        # Try to get ingredients from a known consolidated file
        url = "https://raw.githubusercontent.com/bar-assistant/data/v5/ingredients.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"Found {len(data)} ingredients in consolidated file")
                return [{'name': f"ingredient_{i}.json", 'data': ing} for i, ing in enumerate(data)]
    except Exception as e:
        print(f"Note: {e}")
    
    # Final fallback: scrape the directory listing
    print("Attempting to fetch individual ingredient files...")
    # We'll try common ingredient file names
    common_ingredients = [
        'gin.json', 'vodka.json', 'rum.json', 'whiskey.json', 'tequila.json',
        'bourbon.json', 'scotch.json', 'brandy.json', 'cognac.json',
        'triple-sec.json', 'cointreau.json', 'vermouth.json',
        'campari.json', 'aperol.json', 'amaretto.json',
        'simple-syrup.json', 'lime-juice.json', 'lemon-juice.json',
        'angostura-bitters.json', 'orange-bitters.json',
        'grenadine.json', 'tonic-water.json', 'club-soda.json',
        'ginger-beer.json', 'cola.json'
    ]
    
    return [{'name': f} for f in common_ingredients]

def fetch_ingredient_data(file_info):
    """Fetch individual ingredient data"""
    
    # If data is already included in file_info
    if 'data' in file_info:
        return file_info['data']
    
    filename = file_info['name']
    url = f"{GITHUB_RAW_BASE}/{filename}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Silently skip 404s for our fallback list
        if "404" not in str(e):
            print(f"  ⚠ Error fetching {filename}: {e}")
        return None

def convert_ingredient(bar_assistant_data):
    """Convert Bar Assistant ingredient format to Neighborhood Sips format"""
    
    # Extract relevant fields
    ingredient = {
        'name': bar_assistant_data.get('name', ''),
        'description': bar_assistant_data.get('description', ''),
        'category': bar_assistant_data.get('category', ''),
        'tags': [],
        'images': [],
        'source': 'bar-assistant',
        'external_id': bar_assistant_data.get('_id', ''),
        'strength': bar_assistant_data.get('strength', 0),
        'origin': bar_assistant_data.get('origin', ''),
        'color': bar_assistant_data.get('color', ''),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Add variety as tag if available
    if 'variety' in bar_assistant_data and bar_assistant_data['variety']:
        ingredient['tags'].append(bar_assistant_data['variety'])
    
    # Add parent category as tag
    parent_category = bar_assistant_data.get('parent_category', '')
    if parent_category:
        ingredient['tags'].append(parent_category)
    
    # Store images if available
    if 'images' in bar_assistant_data and bar_assistant_data['images']:
        for img in bar_assistant_data['images']:
            if isinstance(img, dict) and 'url' in img:
                ingredient['images'].append(img['url'])
            elif isinstance(img, str):
                ingredient['images'].append(img)
    
    return ingredient

def load_ingredients_to_db(dry_run=False):
    """Load ingredients from Bar Assistant into MongoDB"""
    
    # Fetch file list
    files = fetch_ingredient_files()
    if not files:
        print("No ingredient files found")
        return 0
    
    if dry_run:
        print("\n=== DRY RUN MODE - No data will be saved ===\n")
    else:
        # Connect to MongoDB
        print(f"\nConnecting to MongoDB at {MONGO_URI}")
        try:
            client = MongoClient(MONGO_URI)
            db = client['neighborhood_sips']
            ingredients_collection = db['ingredients']
            print("✓ Connected to MongoDB")
        except Exception as e:
            print(f"✗ Error connecting to MongoDB: {e}")
            print("Make sure MongoDB is running!")
            return 0
    
    # Process each ingredient file
    print(f"\nProcessing {len(files)} ingredient files...\n")
    loaded_count = 0
    skipped_count = 0
    
    for file_info in files:
        filename = file_info.get('name', 'unknown')
        
        # Fetch ingredient data
        bar_data = fetch_ingredient_data(file_info)
        if not bar_data:
            skipped_count += 1
            continue
        
        # Convert to our format
        ingredient = convert_ingredient(bar_data)
        
        if not ingredient['name']:
            print(f"  ⚠ Skipping {filename}: No name found")
            skipped_count += 1
            continue
        
        if dry_run:
            print(f"  ✓ Would load: {ingredient['name']} ({ingredient['category']})")
            loaded_count += 1
        else:
            # Check if ingredient already exists
            existing = ingredients_collection.find_one({'name': ingredient['name']})
            if existing:
                print(f"  ⚠ Skipping {ingredient['name']}: Already exists")
                skipped_count += 1
                continue
            
            # Insert into database
            try:
                ingredients_collection.insert_one(ingredient)
                print(f"  ✓ Loaded: {ingredient['name']} ({ingredient['category']})")
                loaded_count += 1
            except Exception as e:
                print(f"  ✗ Error loading {ingredient['name']}: {e}")
                skipped_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  - Total files: {len(files)}")
    print(f"  - Loaded: {loaded_count}")
    print(f"  - Skipped: {skipped_count}")
    
    if not dry_run:
        print(f"\n✓ Ingredients loaded into 'neighborhood_sips' database")
    
    return loaded_count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Load ingredients from Bar Assistant data repository'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be loaded without actually loading'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Bar Assistant Ingredients Loader")
    print("Neighborhood Sips Application")
    print("=" * 60)
    
    count = load_ingredients_to_db(dry_run=args.dry_run)
    
    if count > 0:
        print(f"\n✓ Successfully processed {count} ingredients")
        return 0
    else:
        print("\n⚠ No ingredients were loaded")
        return 1

if __name__ == '__main__':
    sys.exit(main())
