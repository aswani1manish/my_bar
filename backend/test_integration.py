#!/usr/bin/env python3
"""
Integration test to verify the fix for recipe images field loading issue.
This test simulates how MySQL Connector returns JSON fields as bytes/bytearray
and verifies that the parse_json_field function correctly handles them.
"""
import sys
import os
import json

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import parse_json_field

def simulate_mysql_response():
    """
    Simulate different ways MySQL Connector might return JSON fields
    depending on configuration (C extension vs pure Python)
    """
    
    # Scenario 1: C extension returns bytes/bytearray (most common)
    recipe_c_extension = {
        'id': 1,
        'name': 'Martini',
        'description': 'Classic cocktail',
        'tags': b'["classic", "gin", "vermouth"]',
        'images': bytearray(b'["martini_1.jpg", "martini_2.jpg"]'),
        'ingredients': b'[{"id": 1, "name": "Gin", "amount": 2.5, "units": "oz"}]'
    }
    
    # Scenario 2: Pure Python mode returns strings
    recipe_pure_python = {
        'id': 2,
        'name': 'Mojito',
        'description': 'Refreshing mint cocktail',
        'tags': '["summer", "rum", "mint"]',
        'images': '["mojito_1.jpg"]',
        'ingredients': '[{"id": 2, "name": "Rum", "amount": 2, "units": "oz"}]'
    }
    
    # Scenario 3: Some fields are None/NULL
    recipe_with_nulls = {
        'id': 3,
        'name': 'Old Fashioned',
        'description': 'Timeless whiskey cocktail',
        'tags': None,
        'images': b'[]',  # Empty array as bytes
        'ingredients': b'[{"id": 3, "name": "Whiskey", "amount": 2, "units": "oz"}]'
    }
    
    # Scenario 4: Already parsed (shouldn't happen but handle gracefully)
    recipe_already_parsed = {
        'id': 4,
        'name': 'Negroni',
        'description': 'Bitter Italian classic',
        'tags': ["bitter", "gin", "aperitif"],
        'images': ["negroni_1.jpg", "negroni_2.jpg"],
        'ingredients': [{"id": 4, "name": "Gin", "amount": 1, "units": "oz"}]
    }
    
    return [
        ("C Extension (bytes/bytearray)", recipe_c_extension),
        ("Pure Python (strings)", recipe_pure_python),
        ("With NULL fields", recipe_with_nulls),
        ("Already parsed", recipe_already_parsed)
    ]

def test_recipe_parsing():
    """Test that recipes are correctly parsed in all scenarios"""
    
    print("=" * 80)
    print("INTEGRATION TEST: Recipe Images Field Fix")
    print("=" * 80)
    print()
    
    test_scenarios = simulate_mysql_response()
    all_passed = True
    
    for scenario_name, recipe in test_scenarios:
        print(f"Testing: {scenario_name}")
        print(f"Recipe: {recipe['name']}")
        print("-" * 80)
        
        # Parse JSON fields using the new helper
        parsed_recipe = recipe.copy()
        parsed_recipe['tags'] = parse_json_field(parsed_recipe.get('tags'))
        parsed_recipe['images'] = parse_json_field(parsed_recipe.get('images'))
        parsed_recipe['ingredients'] = parse_json_field(parsed_recipe.get('ingredients'))
        
        # Verify results
        errors = []
        
        # Check tags
        if parsed_recipe['tags'] is not None:
            if not isinstance(parsed_recipe['tags'], list):
                errors.append(f"  ✗ tags: Expected list, got {type(parsed_recipe['tags'])}")
            else:
                print(f"  ✓ tags: {parsed_recipe['tags']}")
        else:
            print(f"  ✓ tags: None (expected)")
        
        # Check images (main fix)
        if parsed_recipe['images'] is not None:
            if not isinstance(parsed_recipe['images'], list):
                errors.append(f"  ✗ images: Expected list, got {type(parsed_recipe['images'])}")
            else:
                print(f"  ✓ images: {parsed_recipe['images']}")
        else:
            errors.append(f"  ✗ images: Should not be None")
        
        # Check ingredients
        if parsed_recipe['ingredients'] is not None:
            if not isinstance(parsed_recipe['ingredients'], list):
                errors.append(f"  ✗ ingredients: Expected list, got {type(parsed_recipe['ingredients'])}")
            else:
                print(f"  ✓ ingredients: {len(parsed_recipe['ingredients'])} item(s)")
        else:
            errors.append(f"  ✗ ingredients: Should not be None")
        
        if errors:
            print("\nErrors found:")
            for error in errors:
                print(error)
            all_passed = False
        
        print()
    
    print("=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nThe fix successfully handles:")
        print("  • JSON fields returned as bytes (C extension)")
        print("  • JSON fields returned as bytearray")
        print("  • JSON fields returned as strings (pure Python)")
        print("  • NULL/None values")
        print("  • Already-parsed lists and dicts")
        print("  • Empty arrays")
        print("\nThe images field will now load correctly from MySQL!")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(test_recipe_parsing())
