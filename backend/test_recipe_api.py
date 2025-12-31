#!/usr/bin/env python3
"""
Test script for Recipe Management API endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_create_recipe():
    """Test creating a new recipe"""
    print("\n=== Testing CREATE Recipe ===")
    recipe_data = {
        "name": "Test Mojito",
        "description": "A refreshing mint cocktail",
        "instructions": "1. Muddle mint and sugar\n2. Add rum and lime juice\n3. Top with soda water",
        "ingredients": [
            {"name": "White Rum", "quantity": "2", "unit": "oz"},
            {"name": "Lime Juice", "quantity": "1", "unit": "oz"},
            {"name": "Simple Syrup", "quantity": "0.5", "unit": "oz"}
        ],
        "tags": ["rum", "mint", "refreshing"]
    }
    
    response = requests.post(f"{BASE_URL}/recipes", json=recipe_data)
    if response.status_code == 201:
        recipe = response.json()
        print(f"✓ Recipe created successfully with ID: {recipe['id']}")
        return recipe['id']
    else:
        print(f"✗ Failed to create recipe: {response.status_code}")
        return None

def test_get_recipe(recipe_id):
    """Test getting a recipe by ID"""
    print(f"\n=== Testing GET Recipe (ID: {recipe_id}) ===")
    response = requests.get(f"{BASE_URL}/recipes/{recipe_id}")
    if response.status_code == 200:
        recipe = response.json()
        print(f"✓ Recipe retrieved: {recipe['name']}")
        print(f"  - Ingredients: {len(recipe['ingredients'])}")
        print(f"  - Tags: {', '.join(recipe['tags'])}")
        return True
    else:
        print(f"✗ Failed to get recipe: {response.status_code}")
        return False

def test_update_recipe(recipe_id):
    """Test updating a recipe"""
    print(f"\n=== Testing UPDATE Recipe (ID: {recipe_id}) ===")
    update_data = {
        "name": "Test Mojito Updated",
        "description": "An updated refreshing mint cocktail",
        "instructions": "1. Muddle mint leaves with sugar\n2. Add white rum and fresh lime juice\n3. Fill glass with ice\n4. Top with soda water and stir",
        "ingredients": [
            {"name": "White Rum", "quantity": "2", "unit": "oz"},
            {"name": "Lime Juice", "quantity": "1", "unit": "oz"},
            {"name": "Simple Syrup", "quantity": "0.75", "unit": "oz"}
        ],
        "tags": ["rum", "mint", "refreshing", "updated"]
    }
    
    response = requests.put(f"{BASE_URL}/recipes/{recipe_id}", json=update_data)
    if response.status_code == 200:
        recipe = response.json()
        print(f"✓ Recipe updated: {recipe['name']}")
        print(f"  - Description: {recipe['description'][:50]}...")
        return True
    else:
        print(f"✗ Failed to update recipe: {response.status_code}")
        return False

def test_list_recipes():
    """Test listing all recipes"""
    print("\n=== Testing LIST Recipes ===")
    response = requests.get(f"{BASE_URL}/recipes")
    if response.status_code == 200:
        recipes = response.json()
        print(f"✓ Retrieved {len(recipes)} recipes")
        for recipe in recipes[:3]:  # Show first 3
            print(f"  - ID {recipe['id']}: {recipe['name']}")
        return True
    else:
        print(f"✗ Failed to list recipes: {response.status_code}")
        return False

def test_delete_recipe(recipe_id):
    """Test deleting a recipe"""
    print(f"\n=== Testing DELETE Recipe (ID: {recipe_id}) ===")
    response = requests.delete(f"{BASE_URL}/recipes/{recipe_id}")
    if response.status_code == 200:
        print(f"✓ Recipe deleted successfully")
        return True
    else:
        print(f"✗ Failed to delete recipe: {response.status_code}")
        return False

def test_ingredients_available():
    """Test that ingredients are available for selection"""
    print("\n=== Testing Ingredients Availability ===")
    response = requests.get(f"{BASE_URL}/ingredients")
    if response.status_code == 200:
        ingredients = response.json()
        print(f"✓ Retrieved {len(ingredients)} ingredients for recipe creation")
        # Show a few examples
        for ing in ingredients[:5]:
            print(f"  - {ing['name']} ({ing.get('category', 'N/A')})")
        return True
    else:
        print(f"✗ Failed to get ingredients: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Recipe Management API Test Suite")
    print("=" * 60)
    
    # Test ingredients are available
    if not test_ingredients_available():
        print("\n✗ Ingredients test failed. Stopping tests.")
        sys.exit(1)
    
    # Test create
    recipe_id = test_create_recipe()
    if not recipe_id:
        print("\n✗ Create test failed. Stopping tests.")
        sys.exit(1)
    
    # Test get
    if not test_get_recipe(recipe_id):
        print("\n✗ Get test failed. Stopping tests.")
        sys.exit(1)
    
    # Test update
    if not test_update_recipe(recipe_id):
        print("\n✗ Update test failed. Stopping tests.")
        sys.exit(1)
    
    # Test list
    if not test_list_recipes():
        print("\n✗ List test failed. Stopping tests.")
        sys.exit(1)
    
    # Test delete
    if not test_delete_recipe(recipe_id):
        print("\n✗ Delete test failed. Stopping tests.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
