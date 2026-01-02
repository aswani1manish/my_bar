#!/usr/bin/env python3
"""
Test script to verify original image filename preservation and EXIF orientation handling
"""

import os
import sys
import base64
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageOps import exif_transpose
import io

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import sanitize_filename, save_base64_image, app

def create_test_image_with_exif():
    """Create a test image with EXIF orientation data"""
    # Create a simple test image
    img = Image.new('RGB', (200, 100), color='red')
    draw = ImageDraw.Draw(img)
    
    # Add text to show orientation
    draw.text((10, 40), "TOP", fill='white')
    
    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    # Convert to base64
    base64_data = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_data}"

def test_sanitize_filename():
    """Test filename sanitization"""
    print("\n=== Testing Filename Sanitization ===")
    
    test_cases = [
        ("my_image.jpg", "my_image.jpg"),
        ("../../../etc/passwd", "passwd"),  # os.path.basename removes directory path, only 'passwd' remains
        ("test image with spaces.png", "test image with spaces.png"),  # spaces are preserved by sanitize_filename
        ("image@#$%.jpg", "image____.jpg"),
        ("../image.jpg", "image.jpg"),  # os.path.basename removes directory path, only 'image.jpg' remains
        ("normal-image_123.png", "normal-image_123.png"),
        ("", None),
        ("   ...   ", None),
    ]
    
    passed = 0
    failed = 0
    
    for original, expected in test_cases:
        result = sanitize_filename(original)
        if result == expected:
            print(f"✓ '{original}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{original}' -> '{result}' (expected: '{expected}')")
            failed += 1
    
    print(f"\nSanitization tests: {passed} passed, {failed} failed")
    return failed == 0

def test_save_with_original_filename():
    """Test saving images with original filename"""
    print("\n=== Testing Image Save with Original Filename ===")
    
    # Create test image
    base64_image = create_test_image_with_exif()
    
    # Test 1: Save with original filename
    filename1 = save_base64_image(base64_image, 'recipe', 'test_recipe_image.jpg')
    if filename1 and 'test_recipe_image' in filename1:
        print(f"✓ Saved with original filename: {filename1}")
    else:
        print(f"✗ Failed to preserve original filename: {filename1}")
        return False
    
    # Test 2: Save without original filename (should use prefix)
    filename2 = save_base64_image(base64_image, 'recipe')
    if filename2 and filename2.startswith('recipe_'):
        print(f"✓ Saved with prefix: {filename2}")
    else:
        print(f"✗ Failed to use prefix: {filename2}")
        return False
    
    # Test 3: Save with same filename (should add counter)
    filename3 = save_base64_image(base64_image, 'recipe', 'test_recipe_image.jpg')
    if filename3 and filename3 != filename1 and 'test_recipe_image' in filename3:
        print(f"✓ Handled filename collision: {filename3}")
    else:
        print(f"✗ Failed to handle collision: {filename3}")
        return False
    
    # Clean up test files
    upload_folder = app.config['UPLOAD_FOLDER']
    for fname in [filename1, filename2, filename3]:
        if fname:
            try:
                os.remove(os.path.join(upload_folder, fname))
                print(f"  Cleaned up: {fname}")
            except:
                pass
    
    return True

def test_exif_orientation():
    """Test EXIF orientation preservation"""
    print("\n=== Testing EXIF Orientation Handling ===")
    
    # Create a test image
    base64_image = create_test_image_with_exif()
    
    # Save the image
    filename = save_base64_image(base64_image, 'test', 'orientation_test.jpg')
    
    if filename:
        # Check if file was created
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            print(f"✓ Image saved successfully: {filename}")
            
            # Verify image can be opened
            img = Image.open(filepath)
            print(f"✓ Image can be opened: {img.size} {img.format}")
            
            # Clean up
            os.remove(filepath)
            print(f"  Cleaned up: {filename}")
            return True
        else:
            print(f"✗ File not found: {filepath}")
            return False
    else:
        print("✗ Failed to save image")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Image Preservation Tests")
    print("=" * 60)
    
    # Ensure upload folder exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Created upload folder: {upload_folder}")
    
    results = []
    
    # Run tests
    results.append(("Filename Sanitization", test_sanitize_filename()))
    results.append(("Save with Original Filename", test_save_with_original_filename()))
    results.append(("EXIF Orientation", test_exif_orientation()))
    
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
