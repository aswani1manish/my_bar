#!/usr/bin/env python3
"""
Load sample cocktail ingredients into Neighborhood Sips
Based on common cocktail ingredients for bar management
"""

import os
import sys
import json
from datetime import datetime
import mysql.connector
from config import Config

# Sample ingredients database
SAMPLE_INGREDIENTS = [
    # Spirits
    {
        'name': 'Gin',
        'description': 'A distilled alcoholic drink that derives its predominant flavour from juniper berries',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'base', 'juniper'],
        'strength': 40.0,
        'origin': 'Various'
    },
    {
        'name': 'Vodka',
        'description': 'A clear distilled alcoholic beverage with different varieties originating in Poland and Russia',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'base', 'neutral'],
        'strength': 40.0,
        'origin': 'Russia/Poland'
    },
    {
        'name': 'White Rum',
        'description': 'Light-bodied rum that is usually very lightly aged',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'base', 'caribbean'],
        'strength': 40.0,
        'origin': 'Caribbean'
    },
    {
        'name': 'Dark Rum',
        'description': 'Aged rum with a richer, more complex flavor',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'base', 'caribbean', 'aged'],
        'strength': 40.0,
        'origin': 'Caribbean'
    },
    {
        'name': 'Tequila',
        'description': 'A distilled beverage made from the blue agave plant',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'base', 'agave', 'mexican'],
        'strength': 40.0,
        'origin': 'Mexico'
    },
    {
        'name': 'Bourbon',
        'description': 'A type of American whiskey, a barrel-aged distilled liquor made primarily from corn',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'whiskey', 'aged', 'american'],
        'strength': 40.0,
        'origin': 'USA'
    },
    {
        'name': 'Scotch Whisky',
        'description': 'Malt whisky or grain whisky made in Scotland',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'whiskey', 'aged', 'scottish'],
        'strength': 40.0,
        'origin': 'Scotland'
    },
    {
        'name': 'Cognac',
        'description': 'A variety of brandy named after the commune of Cognac, France',
        'category': 'Spirit',
        'tags': ['alcohol', 'spirit', 'brandy', 'aged', 'french'],
        'strength': 40.0,
        'origin': 'France'
    },
    
    # Liqueurs
    {
        'name': 'Triple Sec',
        'description': 'An orange-flavoured liqueur that originated in France',
        'category': 'Liqueur',
        'tags': ['alcohol', 'liqueur', 'orange', 'sweet'],
        'strength': 20.0,
        'origin': 'France'
    },
    {
        'name': 'Cointreau',
        'description': 'Premium triple sec orange liqueur',
        'category': 'Liqueur',
        'tags': ['alcohol', 'liqueur', 'orange', 'sweet', 'premium'],
        'strength': 40.0,
        'origin': 'France'
    },
    {
        'name': 'Elderflower Liqueur',
        'description': 'Sweet liqueur flavored with elderflower blossoms',
        'category': 'Liqueur',
        'tags': ['alcohol', 'liqueur', 'floral', 'sweet'],
        'strength': 20.0,
        'origin': 'Various'
    },
    {
        'name': 'Amaretto',
        'description': 'Sweet Italian liqueur that tastes like almonds',
        'category': 'Liqueur',
        'tags': ['alcohol', 'liqueur', 'almond', 'sweet', 'italian'],
        'strength': 28.0,
        'origin': 'Italy'
    },
    {
        'name': 'Kahlúa',
        'description': 'Mexican coffee-flavored liqueur',
        'category': 'Liqueur',
        'tags': ['alcohol', 'liqueur', 'coffee', 'sweet'],
        'strength': 20.0,
        'origin': 'Mexico'
    },
    {
        'name': 'Baileys Irish Cream',
        'description': 'Irish cream liqueur made with whiskey and cream',
        'category': 'Liqueur',
        'tags': ['alcohol', 'liqueur', 'cream', 'sweet', 'irish'],
        'strength': 17.0,
        'origin': 'Ireland'
    },
    
    # Vermouth & Aperitifs
    {
        'name': 'Dry Vermouth',
        'description': 'Fortified and aromatized wine, white and dry style',
        'category': 'Vermouth',
        'tags': ['alcohol', 'vermouth', 'fortified', 'dry'],
        'strength': 18.0,
        'origin': 'France/Italy'
    },
    {
        'name': 'Sweet Vermouth',
        'description': 'Fortified and aromatized wine, red and sweet style',
        'category': 'Vermouth',
        'tags': ['alcohol', 'vermouth', 'fortified', 'sweet'],
        'strength': 18.0,
        'origin': 'Italy'
    },
    {
        'name': 'Campari',
        'description': 'Italian alcoholic liqueur, considered an apéritif',
        'category': 'Aperitif',
        'tags': ['alcohol', 'aperitif', 'bitter', 'italian'],
        'strength': 25.0,
        'origin': 'Italy'
    },
    {
        'name': 'Aperol',
        'description': 'Italian bitter apéritif with orange flavor',
        'category': 'Aperitif',
        'tags': ['alcohol', 'aperitif', 'bitter', 'orange', 'italian'],
        'strength': 11.0,
        'origin': 'Italy'
    },
    
    # Bitters
    {
        'name': 'Angostura Bitters',
        'description': 'Concentrated bitters made of water, alcohol, herbs and spices',
        'category': 'Bitters',
        'tags': ['alcohol', 'bitters', 'aromatic'],
        'strength': 44.7,
        'origin': 'Trinidad and Tobago'
    },
    {
        'name': 'Orange Bitters',
        'description': 'Form of bitters with orange peel as the primary flavor',
        'category': 'Bitters',
        'tags': ['alcohol', 'bitters', 'orange'],
        'strength': 28.0,
        'origin': 'Various'
    },
    
    # Juices & Fresh Ingredients
    {
        'name': 'Lemon Juice',
        'description': 'Fresh squeezed lemon juice',
        'category': 'Juice',
        'tags': ['fresh', 'citrus', 'sour', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Lime Juice',
        'description': 'Fresh squeezed lime juice',
        'category': 'Juice',
        'tags': ['fresh', 'citrus', 'sour', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Orange Juice',
        'description': 'Fresh squeezed orange juice',
        'category': 'Juice',
        'tags': ['fresh', 'citrus', 'sweet', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Grapefruit Juice',
        'description': 'Fresh squeezed grapefruit juice',
        'category': 'Juice',
        'tags': ['fresh', 'citrus', 'tart', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Cranberry Juice',
        'description': 'Cranberry juice, fresh or bottled',
        'category': 'Juice',
        'tags': ['juice', 'tart', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Pineapple Juice',
        'description': 'Fresh or canned pineapple juice',
        'category': 'Juice',
        'tags': ['juice', 'tropical', 'sweet', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Tropical regions'
    },
    
    # Syrups & Sweeteners
    {
        'name': 'Simple Syrup',
        'description': 'Equal parts sugar and water, heated until dissolved',
        'category': 'Syrup',
        'tags': ['syrup', 'sweet', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Grenadine',
        'description': 'Sweet red syrup traditionally made from pomegranate',
        'category': 'Syrup',
        'tags': ['syrup', 'sweet', 'pomegranate', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Honey Syrup',
        'description': 'Honey diluted with water for easier mixing',
        'category': 'Syrup',
        'tags': ['syrup', 'sweet', 'honey', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    
    # Mixers
    {
        'name': 'Tonic Water',
        'description': 'Carbonated soft drink with quinine',
        'category': 'Mixer',
        'tags': ['mixer', 'carbonated', 'bitter', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Club Soda',
        'description': 'Carbonated water with added minerals',
        'category': 'Mixer',
        'tags': ['mixer', 'carbonated', 'neutral', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Ginger Beer',
        'description': 'Carbonated soft drink flavoured with ginger',
        'category': 'Mixer',
        'tags': ['mixer', 'carbonated', 'spicy', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Cola',
        'description': 'Carbonated soft drink',
        'category': 'Mixer',
        'tags': ['mixer', 'carbonated', 'sweet', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
    {
        'name': 'Ginger Ale',
        'description': 'Carbonated soft drink with ginger flavor',
        'category': 'Mixer',
        'tags': ['mixer', 'carbonated', 'ginger', 'non-alcoholic'],
        'strength': 0.0,
        'origin': 'Various'
    },
]

def load_sample_ingredients(dry_run=False):
    """Load sample ingredients into MySQL"""
    
    if dry_run:
        print("\n=== DRY RUN MODE - No data will be saved ===\n")
        for ing in SAMPLE_INGREDIENTS:
            print(f"  ✓ Would load: {ing['name']} ({ing['category']}) - {ing['description'][:50]}...")
        print(f"\nTotal: {len(SAMPLE_INGREDIENTS)} ingredients")
        return len(SAMPLE_INGREDIENTS)
    
    # Connect to MySQL
    config = Config()
    print(f"\nConnecting to MySQL at {config.MYSQL_HOST}:{config.MYSQL_PORT}")
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        cursor = conn.cursor(dictionary=True)
        print("✓ Connected to MySQL")
    except mysql.connector.Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        print("Make sure MySQL is running and database is initialized (run init_db.py)!")
        return 0
    
    # Load ingredients
    print(f"\nLoading {len(SAMPLE_INGREDIENTS)} sample ingredients...\n")
    loaded_count = 0
    skipped_count = 0
    
    for ing_data in SAMPLE_INGREDIENTS:
        # Check if ingredient already exists
        cursor.execute("SELECT id FROM ingredients WHERE name = %s", (ing_data['name'],))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Skipping {ing_data['name']}: Already exists")
            skipped_count += 1
            continue
        
        # Prepare ingredient data
        now = datetime.utcnow()
        
        # Insert into database
        try:
            query = """
                INSERT INTO ingredients (name, description, category, tags, images, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                ing_data['name'],
                ing_data['description'],
                ing_data['category'],
                json.dumps(ing_data['tags']),
                json.dumps([]),
                now,
                now
            )
            cursor.execute(query, params)
            conn.commit()
            print(f"  ✓ Loaded: {ing_data['name']} ({ing_data['category']})")
            loaded_count += 1
        except mysql.connector.Error as e:
            print(f"  ✗ Error loading {ing_data['name']}: {e}")
            skipped_count += 1
    
    cursor.close()
    conn.close()
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  - Total ingredients: {len(SAMPLE_INGREDIENTS)}")
    print(f"  - Loaded: {loaded_count}")
    print(f"  - Skipped: {skipped_count}")
    print(f"\n✓ Ingredients loaded into '{config.MYSQL_DATABASE}' database")
    
    return loaded_count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Load sample cocktail ingredients into Neighborhood Sips'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be loaded without actually loading'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Sample Ingredients Loader")
    print("Neighborhood Sips Application")
    print("=" * 60)
    
    count = load_sample_ingredients(dry_run=args.dry_run)
    
    if count > 0:
        print(f"\n✓ Successfully processed {count} ingredients")
        return 0
    else:
        print("\n⚠ No ingredients were loaded")
        return 1

if __name__ == '__main__':
    sys.exit(main())
