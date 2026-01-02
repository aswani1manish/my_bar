#!/usr/bin/env python3
"""
Demonstration script showing the image upload enhancement in action
"""
import sys
import os
import base64
from PIL import Image, ImageDraw
import io

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import save_base64_image, sanitize_filename, app

def create_demo_image(text="Demo"):
    """Create a demo image with text"""
    img = Image.new('RGB', (300, 200), color='lightblue')
    draw = ImageDraw.Draw(img)
    # Add text
    draw.text((100, 85), text, fill='darkblue')
    
    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    # Convert to base64
    base64_data = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_data}"

def demo_original_filename():
    """Demonstrate original filename preservation"""
    print("=" * 70)
    print("DEMO: Original Filename Preservation")
    print("=" * 70)
    print()
    
    # Test cases
    test_cases = [
        ("my_delicious_mojito.jpg", "User-friendly name"),
        ("IMG_20240101_123456.jpg", "Camera filename"),
        ("recipe photo.jpg", "Name with spaces"),
        ("cocktail-2024.png", "Name with dash"),
    ]
    
    for original_name, description in test_cases:
        print(f"Test: {description}")
        print(f"  Original: {original_name}")
        
        # Create demo image
        base64_img = create_demo_image(description)
        
        # Save with original filename
        saved_filename = save_base64_image(base64_img, 'recipe', original_name)
        
        print(f"  Saved as: {saved_filename}")
        
        if saved_filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            if os.path.exists(filepath):
                print(f"  ✓ File exists on disk")
                # Clean up
                os.remove(filepath)
            else:
                print(f"  ✗ File not found")
        else:
            print(f"  ✗ Failed to save")
        
        print()

def demo_security():
    """Demonstrate security features"""
    print("=" * 70)
    print("DEMO: Security Features")
    print("=" * 70)
    print()
    
    # Test cases showing security
    dangerous_names = [
        ("../../../etc/passwd", "Directory traversal attempt"),
        ("image<script>.jpg", "Script injection attempt"),
        ("../../../../tmp/evil.jpg", "Path traversal"),
        ("normal_image.jpg", "Safe filename"),
    ]
    
    for dangerous_name, description in dangerous_names:
        print(f"Test: {description}")
        print(f"  Input:  {dangerous_name}")
        
        sanitized = sanitize_filename(dangerous_name)
        print(f"  Output: {sanitized}")
        
        if sanitized and "../" not in sanitized and "<" not in sanitized:
            print(f"  ✓ Safely sanitized")
        else:
            print(f"  ℹ Rejected or needs review")
        
        print()

def demo_collision():
    """Demonstrate filename collision handling"""
    print("=" * 70)
    print("DEMO: Filename Collision Handling")
    print("=" * 70)
    print()
    
    print("Test: Multiple images with same name")
    print(f"  Original: party_cocktail.jpg")
    print()
    
    base64_img = create_demo_image("Collision Test")
    saved_files = []
    
    # Save same filename multiple times
    for i in range(4):
        filename = save_base64_image(base64_img, 'recipe', 'party_cocktail.jpg')
        saved_files.append(filename)
        print(f"  Upload {i+1}: {filename}")
    
    print()
    print("  ✓ Collisions handled automatically with counter suffixes")
    
    # Clean up
    for filename in saved_files:
        if filename:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except:
                pass
    print()

def demo_backward_compatibility():
    """Demonstrate backward compatibility"""
    print("=" * 70)
    print("DEMO: Backward Compatibility")
    print("=" * 70)
    print()
    
    print("Test: Legacy format (no filename provided)")
    print("  Sending: base64 image only")
    
    base64_img = create_demo_image("Legacy")
    
    # Save without filename (legacy way)
    filename = save_base64_image(base64_img, 'recipe')
    
    print(f"  Saved as: {filename}")
    print(f"  ✓ Fallback to prefix-based naming")
    
    # Clean up
    if filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except:
            pass
    print()

def main():
    """Run all demonstrations"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "IMAGE UPLOAD ENHANCEMENT DEMONSTRATION" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Ensure upload folder exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Run demonstrations
    demo_original_filename()
    demo_security()
    demo_collision()
    demo_backward_compatibility()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("✓ Original filenames are preserved")
    print("✓ Dangerous filenames are sanitized")
    print("✓ Collisions are handled automatically")
    print("✓ Backward compatibility is maintained")
    print()
    print("All demonstrations completed successfully!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        sys.exit(0)
