#!/usr/bin/env python3
"""
Convert recipe ingredients from ml to Oz

This script:
1. Creates a backup of the recipes table (structure and data)
2. Goes through each recipe record
3. For each recipe, processes the ingredients JSON
4. If an ingredient unit is 'ml', converts it to 'Oz' and divides amount by 30
   Example: 30 ml becomes 1 Oz, 22.5 ml becomes 0.75 Oz

USAGE:
------
# Dry run (preview changes without applying them)
python3 convert_ml_to_oz.py --dry-run

# Apply the conversion
python3 convert_ml_to_oz.py

# Apply conversion without creating backup
python3 convert_ml_to_oz.py --no-backup
"""

import sys
import json
import argparse
from datetime import datetime
import mysql.connector
from config import Config


def create_backup_table(cursor, conn):
    """Create a backup of the recipes table"""
    backup_table_name = f"recipes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\nCreating backup table: {backup_table_name}")
    
    try:
        # Create table structure
        cursor.execute(f"""
            CREATE TABLE {backup_table_name} LIKE recipes
        """)
        
        # Copy all data
        cursor.execute(f"""
            INSERT INTO {backup_table_name} SELECT * FROM recipes
        """)
        
        conn.commit()
        
        # Get count of backed up records
        cursor.execute(f"SELECT COUNT(*) as count FROM {backup_table_name}")
        count = cursor.fetchone()['count']
        
        print(f"✓ Backup created successfully: {backup_table_name}")
        print(f"  - {count} records backed up")
        
        return backup_table_name
    except mysql.connector.Error as e:
        print(f"✗ Error creating backup: {e}")
        return None


def convert_ingredient_units(ingredients):
    """
    Convert ingredients from ml to Oz
    
    Args:
        ingredients: List of ingredient dictionaries with 'units' and 'amount' fields
        
    Returns:
        Tuple of (converted_ingredients, conversion_count)
    """
    if not isinstance(ingredients, list):
        return ingredients, 0
    
    converted_count = 0
    converted_ingredients = []
    
    for ingredient in ingredients:
        if not isinstance(ingredient, dict):
            converted_ingredients.append(ingredient)
            continue
        
        # Create a copy of the ingredient
        converted_ingredient = ingredient.copy()
        
        # Check if unit is 'ml' (case-insensitive)
        unit = ingredient.get('units', '').strip()
        
        if unit.lower() == 'ml':
            # Convert ml to Oz by dividing by 30
            amount = ingredient.get('amount')
            
            if amount is not None:
                try:
                    # Handle both string and numeric amounts
                    if isinstance(amount, str):
                        amount_float = float(amount)
                    else:
                        amount_float = float(amount)
                    
                    # Convert to Oz (divide by 30)
                    oz_amount = amount_float / 30.0
                    
                    # Update the ingredient
                    converted_ingredient['amount'] = oz_amount
                    converted_ingredient['units'] = 'Oz'
                    
                    converted_count += 1
                except (ValueError, TypeError) as e:
                    # If amount cannot be converted, leave as is
                    print(f"    ⚠ Warning: Could not convert amount '{amount}' for ingredient: {e}")
        
        converted_ingredients.append(converted_ingredient)
    
    return converted_ingredients, converted_count


def convert_recipes(cursor, conn, dry_run=False):
    """
    Convert all recipes from ml to Oz
    
    Args:
        cursor: MySQL cursor
        conn: MySQL connection
        dry_run: If True, only preview changes without updating
        
    Returns:
        Dictionary with conversion statistics
    """
    print("\n" + "=" * 80)
    print("Converting Recipe Ingredients from ml to Oz")
    print("=" * 80)
    
    # Fetch all recipes
    cursor.execute("SELECT id, name, ingredients FROM recipes")
    recipes = cursor.fetchall()
    
    print(f"\nFound {len(recipes)} recipes to process")
    
    if dry_run:
        print("\n=== DRY RUN MODE - No changes will be saved ===\n")
    
    stats = {
        'total_recipes': len(recipes),
        'recipes_modified': 0,
        'total_conversions': 0,
        'recipes_with_ml': []
    }
    
    for recipe in recipes:
        recipe_id = recipe['id']
        recipe_name = recipe['name']
        ingredients_json = recipe['ingredients']
        
        # Parse ingredients JSON
        try:
            if isinstance(ingredients_json, str):
                ingredients = json.loads(ingredients_json)
            else:
                ingredients = ingredients_json
        except (json.JSONDecodeError, TypeError) as e:
            print(f"  ⚠ Skipping recipe '{recipe_name}' (ID: {recipe_id}): Invalid JSON - {e}")
            continue
        
        # Convert ingredients
        converted_ingredients, conversion_count = convert_ingredient_units(ingredients)
        
        if conversion_count > 0:
            stats['recipes_modified'] += 1
            stats['total_conversions'] += conversion_count
            stats['recipes_with_ml'].append({
                'id': recipe_id,
                'name': recipe_name,
                'conversions': conversion_count
            })
            
            print(f"  ✓ {recipe_name} (ID: {recipe_id})")
            print(f"    - Converted {conversion_count} ingredient(s) from ml to Oz")
            
            if dry_run:
                # Show preview of changes
                print(f"    - Preview of converted ingredients:")
                for idx, ing in enumerate(converted_ingredients):
                    if ing.get('units') == 'Oz':
                        original_ing = ingredients[idx] if idx < len(ingredients) else {}
                        original_amount = original_ing.get('amount', 'N/A')
                        original_unit = original_ing.get('units', 'N/A')
                        print(f"      • {ing.get('name', 'Unknown')}: {original_amount} {original_unit} → {ing.get('amount')} Oz")
            else:
                # Update the recipe in database
                try:
                    update_query = """
                        UPDATE recipes 
                        SET ingredients = %s, updated_at = %s 
                        WHERE id = %s
                    """
                    cursor.execute(
                        update_query,
                        (json.dumps(converted_ingredients), datetime.now(), recipe_id)
                    )
                    conn.commit()
                except mysql.connector.Error as e:
                    print(f"    ✗ Error updating recipe: {e}")
                    conn.rollback()
    
    return stats


def print_summary(stats, dry_run=False):
    """Print summary of conversion results"""
    print("\n" + "=" * 80)
    print("Conversion Summary")
    print("=" * 80)
    print(f"Total recipes processed: {stats['total_recipes']}")
    print(f"Recipes modified: {stats['recipes_modified']}")
    print(f"Total ingredient conversions: {stats['total_conversions']}")
    
    if stats['recipes_with_ml']:
        print(f"\nRecipes with ml conversions:")
        for recipe_info in stats['recipes_with_ml']:
            print(f"  - {recipe_info['name']} (ID: {recipe_info['id']}): {recipe_info['conversions']} conversion(s)")
    
    if dry_run:
        print("\n⚠ This was a dry run. No changes were saved to the database.")
        print("  Run without --dry-run to apply the changes.")
    else:
        print("\n✓ All conversions have been applied successfully!")


def main():
    parser = argparse.ArgumentParser(
        description='Convert recipe ingredients from ml to Oz',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes without applying them
  python3 convert_ml_to_oz.py --dry-run
  
  # Apply the conversion with backup
  python3 convert_ml_to_oz.py
  
  # Apply conversion without creating backup
  python3 convert_ml_to_oz.py --no-backup
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating a backup table before conversion'
    )
    
    args = parser.parse_args()
    
    # Connect to MySQL
    config = Config()
    print(f"\nConnecting to MySQL at {config.MYSQL_HOST}:{config.MYSQL_PORT}")
    print(f"Database: {config.MYSQL_DATABASE}")
    
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
        print("Make sure MySQL is running and database is initialized!")
        return 1
    
    try:
        # Create backup if not in dry-run mode and not disabled
        backup_table_name = None
        if not args.dry_run and not args.no_backup:
            backup_table_name = create_backup_table(cursor, conn)
            if not backup_table_name:
                print("\n✗ Failed to create backup. Aborting conversion.")
                return 1
        
        # Convert recipes
        stats = convert_recipes(cursor, conn, dry_run=args.dry_run)
        
        # Print summary
        print_summary(stats, dry_run=args.dry_run)
        
        if backup_table_name:
            print(f"\n💾 Backup table: {backup_table_name}")
            print("   (You can restore from this backup if needed)")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
