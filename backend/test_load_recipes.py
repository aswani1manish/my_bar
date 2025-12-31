#!/usr/bin/env python3
"""
Test the copy_recipe_images function to ensure it preserves original filenames
"""
import sys
import os
import tempfile
import shutil

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from load_recipes import copy_recipe_images

def test_copy_recipe_images_preserves_filenames():
    """Test that copy_recipe_images preserves original filenames"""
    
    print("Testing copy_recipe_images function:")
    print("=" * 80)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        recipe_folder = os.path.join(temp_dir, 'recipe')
        upload_folder = os.path.join(temp_dir, 'uploads')
        os.makedirs(recipe_folder)
        os.makedirs(upload_folder)
        
        # Create test image files with specific names
        test_images = [
            'margarita.jpg',
            'margarita_close_up.png',
            'margarita-ingredients.jpeg',
            'data.json'  # This should be ignored (not an image)
        ]
        
        expected_images = [
            'margarita.jpg',
            'margarita_close_up.png',
            'margarita-ingredients.jpeg'
        ]
        
        for filename in test_images:
            file_path = os.path.join(recipe_folder, filename)
            with open(file_path, 'w') as f:
                f.write('test content')
        
        # Call the function
        result = copy_recipe_images(recipe_folder, upload_folder)
        
        # Check results
        all_passed = True
        
        # Test 1: Check that the function returns the expected filenames
        if sorted(result) == sorted(expected_images):
            print("✓ PASS: Function returns original filenames")
            print(f"  Returned: {result}")
        else:
            print("✗ FAIL: Function did not return original filenames")
            print(f"  Expected: {expected_images}")
            print(f"  Got: {result}")
            all_passed = False
        
        print()
        
        # Test 2: Check that files exist with original names in upload folder
        for filename in expected_images:
            dest_path = os.path.join(upload_folder, filename)
            if os.path.exists(dest_path):
                print(f"✓ PASS: Image copied with original name: {filename}")
            else:
                print(f"✗ FAIL: Image not found with original name: {filename}")
                all_passed = False
        
        print()
        
        # Test 3: Check that no renamed files exist (no files with "recipe_" prefix)
        uploaded_files = os.listdir(upload_folder)
        renamed_files = [f for f in uploaded_files if f.startswith('recipe_')]
        if len(renamed_files) == 0:
            print("✓ PASS: No files were renamed with 'recipe_' prefix")
        else:
            print(f"✗ FAIL: Found renamed files: {renamed_files}")
            all_passed = False
        
        print()
        
        # Test 4: Check that non-image files were not copied
        data_json_path = os.path.join(upload_folder, 'data.json')
        if not os.path.exists(data_json_path):
            print("✓ PASS: Non-image files (data.json) were not copied")
        else:
            print("✗ FAIL: Non-image file (data.json) was copied")
            all_passed = False
    
    print("=" * 80)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(test_copy_recipe_images_preserves_filenames())
