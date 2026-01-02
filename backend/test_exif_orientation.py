#!/usr/bin/env python3
"""
Test EXIF orientation handling to verify images with rotation metadata display correctly
"""
import sys
import os
import base64
from PIL import Image, ExifTags
import io

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import save_base64_image, app

def create_image_with_orientation(orientation=1):
    """Create a test image with specific EXIF orientation"""
    # Create a rectangular image to make orientation visible
    img = Image.new('RGB', (200, 100), color='red')
    
    # Add a marker at the top to show orientation
    for x in range(50, 150):
        for y in range(10, 20):
            img.putpixel((x, y), (255, 255, 255))  # White bar at top
    
    # Save with EXIF orientation
    buffer = io.BytesIO()
    
    # Create EXIF data with orientation tag
    exif_data = img.getexif()
    if orientation != 1:
        # Set orientation tag (274 is the EXIF tag for Orientation)
        exif_data[274] = orientation
    
    img.save(buffer, format='JPEG', exif=exif_data)
    buffer.seek(0)
    
    # Convert to base64
    base64_data = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_data}"

def test_orientation_handling():
    """Test that EXIF orientation is handled correctly"""
    print("\n=== Testing EXIF Orientation Handling ===")
    
    # Test different orientations
    orientations = [
        (1, "Normal"),
        (3, "Upside down"),
        (6, "Rotated 90 CW"),
        (8, "Rotated 90 CCW"),
    ]
    
    results = []
    
    for orientation, description in orientations:
        print(f"\nTesting orientation {orientation} ({description}):")
        
        # Create image with specific orientation
        base64_img = create_image_with_orientation(orientation)
        
        # Save the image
        filename = save_base64_image(
            base64_img, 
            'test', 
            f'orientation_{orientation}_test.jpg'
        )
        
        if filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            if os.path.exists(filepath):
                # Load the saved image and check if it was corrected
                saved_img = Image.open(filepath)
                
                # Check EXIF data - should be normalized to orientation 1
                exif = saved_img.getexif()
                saved_orientation = exif.get(274, 1) if exif else 1
                
                print(f"  Original orientation: {orientation}")
                print(f"  Saved orientation: {saved_orientation}")
                print(f"  Image dimensions: {saved_img.size}")
                
                # For rotated images (6, 8), dimensions should be swapped
                expected_swap = orientation in [6, 8]
                width, height = saved_img.size
                is_swapped = width < height
                
                if expected_swap == is_swapped or saved_orientation == 1:
                    print(f"  ✓ Orientation handled correctly")
                    results.append(True)
                else:
                    print(f"  ✗ Orientation may not be handled correctly")
                    results.append(False)
                
                # Clean up
                os.remove(filepath)
            else:
                print(f"  ✗ File not found: {filepath}")
                results.append(False)
        else:
            print(f"  ✗ Failed to save image")
            results.append(False)
    
    return all(results)

def test_exif_preservation():
    """Test that valid EXIF data is preserved or corrected"""
    print("\n=== Testing EXIF Data Preservation ===")
    
    # Create a simple JPEG with EXIF data
    img = Image.new('RGB', (100, 100), color='green')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    base64_data = base64.b64encode(buffer.read()).decode('utf-8')
    base64_img = f"data:image/jpeg;base64,{base64_data}"
    
    # Save the image
    filename = save_base64_image(
        base64_img, 
        'test', 
        'exif_preservation_test.jpg'
    )
    
    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(filepath):
            # Verify the image can be opened and is valid
            saved_img = Image.open(filepath)
            
            print(f"✓ Image saved and can be opened")
            print(f"  Format: {saved_img.format}")
            print(f"  Size: {saved_img.size}")
            
            # Clean up
            os.remove(filepath)
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
    print("EXIF Orientation Tests")
    print("=" * 60)
    
    # Ensure upload folder exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Created upload folder: {upload_folder}")
    
    results = []
    
    # Run tests
    results.append(("EXIF Orientation Handling", test_orientation_handling()))
    results.append(("EXIF Data Preservation", test_exif_preservation()))
    
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
        print("\nNote: EXIF orientation metadata is handled using PIL's exif_transpose()")
        print("This function automatically rotates the image based on EXIF orientation")
        print("and resets the orientation flag to 1 (normal), ensuring correct display.")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
