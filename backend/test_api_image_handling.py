#!/usr/bin/env python3
"""
Test the API endpoints to verify image handling with original filenames
"""
import sys
import os
import json
import base64
from PIL import Image
import io

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import app and test client
from app import app

def create_test_base64_image(filename="test.jpg"):
    """Create a simple test image as base64"""
    img = Image.new('RGB', (100, 100), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    base64_data = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_data}"

def test_recipe_creation_with_filename():
    """Test recipe creation with original filename"""
    print("\n=== Testing Recipe Creation with Original Filename ===")
    
    client = app.test_client()
    
    # Create test data with new format (dict with data and filename)
    recipe_data = {
        "name": "Test Cocktail",
        "description": "A test cocktail",
        "instructions": "Mix ingredients",
        "ingredients": [
            {"name": "Gin", "quantity": "2", "unit": "oz"}
        ],
        "tags": ["test"],
        "images": [
            {
                "data": create_test_base64_image(),
                "filename": "my_custom_cocktail_photo.jpg"
            }
        ]
    }
    
    # Since we don't have MySQL running, we'll just test that the function can parse the data
    # Let's test the parsing logic
    from app import save_base64_image
    
    for img_data in recipe_data['images']:
        if isinstance(img_data, dict) and 'data' in img_data:
            filename = save_base64_image(
                img_data['data'], 
                'recipe', 
                img_data.get('filename')
            )
            if filename and 'my_custom_cocktail_photo' in filename:
                print(f"✓ Recipe image saved with original filename: {filename}")
                # Clean up
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                except:
                    pass
                return True
            else:
                print(f"✗ Failed to preserve filename: {filename}")
                return False
    
    return False

def test_recipe_creation_legacy_format():
    """Test recipe creation with legacy format (backward compatibility)"""
    print("\n=== Testing Recipe Creation with Legacy Format ===")
    
    # Create test data with legacy format (just base64 string)
    recipe_data = {
        "name": "Test Cocktail",
        "description": "A test cocktail",
        "instructions": "Mix ingredients",
        "ingredients": [
            {"name": "Gin", "quantity": "2", "unit": "oz"}
        ],
        "tags": ["test"],
        "images": [
            create_test_base64_image()  # Just base64 string
        ]
    }
    
    from app import save_base64_image
    
    for img_data in recipe_data['images']:
        # Should work with legacy format too
        if isinstance(img_data, str) and img_data.startswith('data:'):
            filename = save_base64_image(img_data, 'recipe')
            if filename and filename.startswith('recipe_'):
                print(f"✓ Recipe image saved with prefix: {filename}")
                # Clean up
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                except:
                    pass
                return True
            else:
                print(f"✗ Failed to save with prefix: {filename}")
                return False
    
    return False

def test_recipe_update_with_filename():
    """Test recipe update with original filename"""
    print("\n=== Testing Recipe Update with Original Filename ===")
    
    # Simulate update scenario
    from app import save_base64_image
    
    # Existing images
    existing_images = ["old_image_1.jpg", "old_image_2.jpg"]
    
    # New images to add
    new_images_data = [
        {
            "data": create_test_base64_image(),
            "filename": "new_cocktail_angle.jpg"
        }
    ]
    
    images = existing_images.copy()
    
    # Process new images
    for img_data in new_images_data:
        if isinstance(img_data, dict) and 'data' in img_data:
            filename = save_base64_image(
                img_data['data'], 
                'recipe', 
                img_data.get('filename')
            )
            if filename:
                images.append(filename)
    
    # Check results
    if len(images) == 3 and any('new_cocktail_angle' in img for img in images):
        print(f"✓ Recipe update preserved original filename: {images}")
        # Clean up
        for img in images:
            if img not in existing_images:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
                except:
                    pass
        return True
    else:
        print(f"✗ Failed to preserve filename in update: {images}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("API Image Handling Tests")
    print("=" * 60)
    
    # Ensure upload folder exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Created upload folder: {upload_folder}")
    
    results = []
    
    # Run tests
    results.append(("Recipe Creation with Filename", test_recipe_creation_with_filename()))
    results.append(("Recipe Creation Legacy Format", test_recipe_creation_legacy_format()))
    results.append(("Recipe Update with Filename", test_recipe_update_with_filename()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
