#!/usr/bin/env python3
"""
Test the parse_json_field function to ensure it handles all cases correctly
"""
import sys
import os
import json

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import parse_json_field

def test_parse_json_field():
    """Test parse_json_field with various inputs"""
    
    test_cases = [
        # (input, expected_output, description)
        (None, None, "None input"),
        ([], [], "Empty list"),
        (['img1.jpg'], ['img1.jpg'], "List with values"),
        ({}, {}, "Empty dict"),
        ({'key': 'value'}, {'key': 'value'}, "Dict with values"),
        ('[]', [], "Empty JSON array string"),
        ('["img1.jpg", "img2.jpg"]', ["img1.jpg", "img2.jpg"], "JSON array string"),
        ('{}', {}, "Empty JSON object string"),
        ('{"key": "value"}', {"key": "value"}, "JSON object string"),
        (b'[]', [], "Empty JSON array bytes"),
        (b'["img1.jpg", "img2.jpg"]', ["img1.jpg", "img2.jpg"], "JSON array bytes"),
        (bytearray(b'[]'), [], "Empty JSON array bytearray"),
        (bytearray(b'["img1.jpg", "img2.jpg"]'), ["img1.jpg", "img2.jpg"], "JSON array bytearray"),
        ('', '', "Empty string (invalid JSON)"),
        ('not json', 'not json', "Invalid JSON string"),
    ]
    
    print("Testing parse_json_field function:")
    print("=" * 80)
    
    all_passed = True
    for input_val, expected, description in test_cases:
        try:
            result = parse_json_field(input_val)
            passed = result == expected
            
            if passed:
                print(f"✓ PASS: {description}")
                print(f"  Input: {repr(input_val)[:60]}")
                print(f"  Output: {repr(result)[:60]}")
            else:
                print(f"✗ FAIL: {description}")
                print(f"  Input: {repr(input_val)[:60]}")
                print(f"  Expected: {repr(expected)[:60]}")
                print(f"  Got: {repr(result)[:60]}")
                all_passed = False
        except Exception as e:
            print(f"✗ ERROR: {description}")
            print(f"  Input: {repr(input_val)[:60]}")
            print(f"  Exception: {e}")
            all_passed = False
        
        print()
    
    print("=" * 80)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(test_parse_json_field())
