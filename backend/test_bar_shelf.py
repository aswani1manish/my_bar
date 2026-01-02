#!/usr/bin/env python3
"""
Test bar shelf availability filter functionality
"""

import sys
import os
import json

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import mysql.connector
from config import Config

def setup_test_data():
    """Setup test data for bar shelf testing"""
    config = Config()
    
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        cursor = conn.cursor()
        
        # Clean up any existing test data
        try:
            cursor.execute("DELETE FROM recipes WHERE name LIKE 'Test Recipe%'")
            cursor.execute("DELETE FROM ingredients WHERE name LIKE 'Test Ingredient%'")
            conn.commit()
        except mysql.connector.Error as e:
            print(f"  Note: Error during initial cleanup (may be expected): {e}")
            conn.rollback()
        
        # Insert test ingredients
        cursor.execute("""
            INSERT INTO ingredients (name, description, bar_shelf_availability)
            VALUES 
                ('Test Ingredient A', 'Available ingredient', 'Y'),
                ('Test Ingredient B', 'Not available ingredient', 'N'),
                ('Test Ingredient C', 'Available ingredient', 'Y')
        """)
        conn.commit()
        
        # Insert test recipes
        cursor.execute("""
            INSERT INTO recipes (name, description, ingredients, instructions)
            VALUES 
                ('Test Recipe 1', 'Recipe with all available ingredients', %s, 'Mix and serve'),
                ('Test Recipe 2', 'Recipe with unavailable ingredient', %s, 'Mix and serve'),
                ('Test Recipe 3', 'Recipe with all available ingredients', %s, 'Mix and serve')
        """, (
            json.dumps([
                {'name': 'Test Ingredient A', 'amount': '2', 'units': 'oz'},
                {'name': 'Test Ingredient C', 'amount': '1', 'units': 'oz'}
            ]),
            json.dumps([
                {'name': 'Test Ingredient A', 'amount': '2', 'units': 'oz'},
                {'name': 'Test Ingredient B', 'amount': '1', 'units': 'oz'}
            ]),
            json.dumps([
                {'name': 'Test Ingredient C', 'amount': '1', 'units': 'oz'}
            ])
        ))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("✓ Test data setup completed")
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ Error setting up test data: {e}")
        return False

def cleanup_test_data():
    """Clean up test data after testing"""
    config = Config()
    
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM recipes WHERE name LIKE 'Test Recipe%'")
            cursor.execute("DELETE FROM ingredients WHERE name LIKE 'Test Ingredient%'")
            conn.commit()
        except mysql.connector.Error as e:
            print(f"  Note: Error during cleanup: {e}")
            conn.rollback()
        
        cursor.close()
        conn.close()
        
        print("✓ Test data cleanup completed")
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ Error cleaning up test data: {e}")
        return False

def test_bar_shelf_filter():
    """Test bar shelf availability filter"""
    with app.test_client() as client:
        
        # Test 1: Get all recipes without filter
        print("\nTest 1: Get all recipes without bar shelf filter")
        response = client.get('/api/recipes?search=Test Recipe')
        assert response.status_code == 200
        data = json.loads(response.data)
        all_recipes_count = len(data)
        print(f"  ✓ Found {all_recipes_count} test recipes without filter")
        assert all_recipes_count >= 3, "Should find at least 3 test recipes"
        
        # Test 2: Get recipes with bar shelf mode enabled
        print("\nTest 2: Get recipes with bar shelf mode = Y")
        response = client.get('/api/recipes?search=Test Recipe&bar_shelf_mode=Y')
        assert response.status_code == 200
        data = json.loads(response.data)
        filtered_count = len(data)
        print(f"  ✓ Found {filtered_count} recipes with bar shelf filter")
        
        # We expect only 2 recipes (Test Recipe 1 and Test Recipe 3)
        # Test Recipe 2 has Test Ingredient B which has bar_shelf_availability = 'N'
        assert filtered_count == 2, f"Expected 2 recipes with bar shelf filter, got {filtered_count}"
        
        # Verify the correct recipes are returned
        recipe_names = [r['name'] for r in data]
        assert 'Test Recipe 1' in recipe_names, "Test Recipe 1 should be in filtered results"
        assert 'Test Recipe 3' in recipe_names, "Test Recipe 3 should be in filtered results"
        assert 'Test Recipe 2' not in recipe_names, "Test Recipe 2 should NOT be in filtered results"
        
        print("  ✓ Correct recipes filtered based on bar shelf availability")
        
        # Test 3: Verify filtering is case-insensitive
        print("\nTest 3: Test case-insensitivity of bar_shelf_mode parameter")
        response = client.get('/api/recipes?search=Test Recipe&bar_shelf_mode=y')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2, "Should work with lowercase 'y'"
        print("  ✓ Filter works with lowercase 'y'")
        
        # Test 4: Verify no filter when bar_shelf_mode is not 'Y'
        print("\nTest 4: Verify no filter when bar_shelf_mode is 'N' or other value")
        response = client.get('/api/recipes?search=Test Recipe&bar_shelf_mode=N')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == all_recipes_count, "Should return all recipes when bar_shelf_mode is not 'Y'"
        print("  ✓ No filtering applied when bar_shelf_mode is 'N'")
        
        return True

def main():
    print("=" * 60)
    print("Bar Shelf Availability Filter Tests")
    print("=" * 60)
    
    # Setup test data
    if not setup_test_data():
        print("\n✗ Failed to setup test data. Exiting.")
        return 1
    
    try:
        # Run tests
        if test_bar_shelf_filter():
            print("\n" + "=" * 60)
            print("✓ All tests passed!")
            print("=" * 60)
            return 0
        else:
            print("\n✗ Some tests failed")
            return 1
    
    finally:
        # Cleanup test data
        cleanup_test_data()

if __name__ == '__main__':
    sys.exit(main())
