#!/usr/bin/env python3
"""
Test script for convert_ml_to_oz.py conversion logic
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from convert_ml_to_oz import convert_ingredient_units


def test_basic_ml_conversion():
    """Test basic ml to Oz conversion"""
    print("\n=== Test 1: Basic ml to Oz conversion ===")
    
    ingredients = [
        {'name': 'Vodka', 'amount': 30, 'units': 'ml'},
        {'name': 'Lime Juice', 'amount': 15, 'units': 'ml'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 2, f"Expected 2 conversions, got {count}"
    assert converted[0]['amount'] == 1.0, f"Expected 1.0 Oz, got {converted[0]['amount']}"
    assert converted[0]['units'] == 'Oz', f"Expected 'Oz', got {converted[0]['units']}"
    assert converted[1]['amount'] == 0.5, f"Expected 0.5 Oz, got {converted[1]['amount']}"
    assert converted[1]['units'] == 'Oz', f"Expected 'Oz', got {converted[1]['units']}"
    
    print("✓ PASS: Basic ml to Oz conversion works correctly")
    print(f"  - 30 ml → {converted[0]['amount']} Oz")
    print(f"  - 15 ml → {converted[1]['amount']} Oz")
    return True


def test_decimal_ml_conversion():
    """Test decimal ml values"""
    print("\n=== Test 2: Decimal ml to Oz conversion ===")
    
    ingredients = [
        {'name': 'Gin', 'amount': 22.5, 'units': 'ml'},
        {'name': 'Vermouth', 'amount': 7.5, 'units': 'ml'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 2, f"Expected 2 conversions, got {count}"
    assert abs(converted[0]['amount'] - 0.75) < 0.001, f"Expected 0.75 Oz, got {converted[0]['amount']}"
    assert abs(converted[1]['amount'] - 0.25) < 0.001, f"Expected 0.25 Oz, got {converted[1]['amount']}"
    
    print("✓ PASS: Decimal ml values convert correctly")
    print(f"  - 22.5 ml → {converted[0]['amount']} Oz")
    print(f"  - 7.5 ml → {converted[1]['amount']} Oz")
    return True


def test_string_amount_conversion():
    """Test string amounts are converted properly"""
    print("\n=== Test 3: String amount conversion ===")
    
    ingredients = [
        {'name': 'Rum', 'amount': '60', 'units': 'ml'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 1, f"Expected 1 conversion, got {count}"
    assert converted[0]['amount'] == 2.0, f"Expected 2.0 Oz, got {converted[0]['amount']}"
    
    print("✓ PASS: String amounts convert correctly")
    print(f"  - '60' ml → {converted[0]['amount']} Oz")
    return True


def test_case_insensitive_ml():
    """Test that ML, Ml, ml are all recognized"""
    print("\n=== Test 4: Case-insensitive ml recognition ===")
    
    ingredients = [
        {'name': 'Vodka', 'amount': 30, 'units': 'ML'},
        {'name': 'Gin', 'amount': 30, 'units': 'Ml'},
        {'name': 'Rum', 'amount': 30, 'units': 'ml'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 3, f"Expected 3 conversions, got {count}"
    for ing in converted:
        assert ing['units'] == 'Oz', f"Expected 'Oz', got {ing['units']}"
        assert ing['amount'] == 1.0, f"Expected 1.0, got {ing['amount']}"
    
    print("✓ PASS: Case-insensitive ml recognition works")
    print(f"  - ML, Ml, ml all converted to Oz")
    return True


def test_non_ml_units_unchanged():
    """Test that non-ml units are not converted"""
    print("\n=== Test 5: Non-ml units remain unchanged ===")
    
    ingredients = [
        {'name': 'Whiskey', 'amount': 2, 'units': 'oz'},
        {'name': 'Bitters', 'amount': 2, 'units': 'dashes'},
        {'name': 'Sugar', 'amount': 1, 'units': 'tsp'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 0, f"Expected 0 conversions, got {count}"
    assert converted[0]['amount'] == 2, f"Expected 2, got {converted[0]['amount']}"
    assert converted[0]['units'] == 'oz', f"Expected 'oz', got {converted[0]['units']}"
    assert converted[1]['units'] == 'dashes', f"Expected 'dashes', got {converted[1]['units']}"
    assert converted[2]['units'] == 'tsp', f"Expected 'tsp', got {converted[2]['units']}"
    
    print("✓ PASS: Non-ml units remain unchanged")
    print(f"  - oz, dashes, tsp preserved")
    return True


def test_mixed_units():
    """Test recipe with mixed units (some ml, some not)"""
    print("\n=== Test 6: Mixed units in recipe ===")
    
    ingredients = [
        {'name': 'Vodka', 'amount': 45, 'units': 'ml'},
        {'name': 'Lime Juice', 'amount': 1, 'units': 'oz'},
        {'name': 'Simple Syrup', 'amount': 15, 'units': 'ml'},
        {'name': 'Bitters', 'amount': 2, 'units': 'dashes'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 2, f"Expected 2 conversions, got {count}"
    assert converted[0]['units'] == 'Oz', "Vodka should be Oz"
    assert converted[1]['units'] == 'oz', "Lime Juice should remain oz"
    assert converted[2]['units'] == 'Oz', "Simple Syrup should be Oz"
    assert converted[3]['units'] == 'dashes', "Bitters should remain dashes"
    
    print("✓ PASS: Mixed units handled correctly")
    print(f"  - Converted: 45 ml → {converted[0]['amount']} Oz, 15 ml → {converted[2]['amount']} Oz")
    print(f"  - Preserved: 1 oz, 2 dashes")
    return True


def test_empty_or_missing_amount():
    """Test handling of missing or invalid amounts"""
    print("\n=== Test 7: Missing or invalid amounts ===")
    
    ingredients = [
        {'name': 'Vodka', 'amount': None, 'units': 'ml'},
        {'name': 'Gin', 'units': 'ml'},  # No amount field
        {'name': 'Rum', 'amount': 'invalid', 'units': 'ml'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    # These should not crash and should not be converted
    assert count == 0, f"Expected 0 conversions, got {count}"
    
    print("✓ PASS: Missing/invalid amounts handled gracefully")
    print(f"  - Script does not crash on invalid data")
    return True


def test_empty_ingredients_list():
    """Test empty ingredients list"""
    print("\n=== Test 8: Empty ingredients list ===")
    
    ingredients = []
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 0, f"Expected 0 conversions, got {count}"
    assert len(converted) == 0, f"Expected empty list, got {len(converted)} items"
    
    print("✓ PASS: Empty ingredients list handled correctly")
    return True


def test_additional_ingredient_fields():
    """Test that other ingredient fields are preserved"""
    print("\n=== Test 9: Additional fields preserved ===")
    
    ingredients = [
        {
            'id': 123,
            'name': 'Vodka',
            'amount': 30,
            'units': 'ml',
            'optional': False,
            'note': 'Chilled'
        }
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 1, f"Expected 1 conversion, got {count}"
    assert converted[0]['id'] == 123, "ID should be preserved"
    assert converted[0]['name'] == 'Vodka', "Name should be preserved"
    assert converted[0]['optional'] == False, "Optional field should be preserved"
    assert converted[0]['note'] == 'Chilled', "Note should be preserved"
    assert converted[0]['amount'] == 1.0, "Amount should be converted"
    assert converted[0]['units'] == 'Oz', "Units should be converted"
    
    print("✓ PASS: Additional ingredient fields preserved")
    print(f"  - id, name, optional, note all intact")
    return True


def test_special_ml_conversions():
    """Test special conversions for 10ml and 20ml"""
    print("\n=== Test 10: Special ML conversions (10ml, 20ml) ===")
    
    ingredients = [
        {'name': 'Ingredient A', 'amount': 10, 'units': 'ml'},
        {'name': 'Ingredient B', 'amount': 20, 'units': 'ml'},
        {'name': 'Ingredient C', 'amount': 10.0, 'units': 'ml'},
        {'name': 'Ingredient D', 'amount': '20', 'units': 'ml'}
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 4, f"Expected 4 conversions, got {count}"
    assert converted[0]['amount'] == 0.25, f"Expected 0.25 Oz for 10ml, got {converted[0]['amount']}"
    assert converted[1]['amount'] == 0.75, f"Expected 0.75 Oz for 20ml, got {converted[1]['amount']}"
    assert converted[2]['amount'] == 0.25, f"Expected 0.25 Oz for 10.0ml, got {converted[2]['amount']}"
    assert converted[3]['amount'] == 0.75, f"Expected 0.75 Oz for '20'ml, got {converted[3]['amount']}"
    
    print("✓ PASS: Special ML conversions work correctly")
    print(f"  - 10 ml → {converted[0]['amount']} Oz")
    print(f"  - 20 ml → {converted[1]['amount']} Oz")
    return True


def test_rounding_to_quarter_oz():
    """Test that other values round to nearest 0.25 Oz"""
    print("\n=== Test 11: Rounding to nearest 0.25 Oz ===")
    
    ingredients = [
        {'name': 'Test 1', 'amount': 11, 'units': 'ml'},  # 11/30 = 0.367 → should round to 0.25 or 0.5
        {'name': 'Test 2', 'amount': 16, 'units': 'ml'},  # 16/30 = 0.533 → should round to 0.5
        {'name': 'Test 3', 'amount': 25, 'units': 'ml'},  # 25/30 = 0.833 → should round to 0.75 or 1.0
        {'name': 'Test 4', 'amount': 40, 'units': 'ml'},  # 40/30 = 1.333 → should round to 1.25
        {'name': 'Test 5', 'amount': 50, 'units': 'ml'},  # 50/30 = 1.667 → should round to 1.75
    ]
    
    converted, count = convert_ingredient_units(ingredients)
    
    assert count == 5, f"Expected 5 conversions, got {count}"
    
    # Verify all amounts are in 0.25 increments
    for idx, ing in enumerate(converted):
        amount = ing['amount']
        # Check if amount is a multiple of 0.25
        assert (amount * 4) % 1 == 0, f"Amount {amount} is not in 0.25 increments"
    
    print("✓ PASS: Values round to nearest 0.25 Oz")
    print(f"  - 11 ml → {converted[0]['amount']} Oz")
    print(f"  - 16 ml → {converted[1]['amount']} Oz")
    print(f"  - 25 ml → {converted[2]['amount']} Oz")
    print(f"  - 40 ml → {converted[3]['amount']} Oz")
    print(f"  - 50 ml → {converted[4]['amount']} Oz")
    return True


def main():
    """Run all tests"""
    print("=" * 80)
    print("Testing convert_ml_to_oz Conversion Logic")
    print("=" * 80)
    
    tests = [
        test_basic_ml_conversion,
        test_decimal_ml_conversion,
        test_string_amount_conversion,
        test_case_insensitive_ml,
        test_non_ml_units_unchanged,
        test_mixed_units,
        test_empty_or_missing_amount,
        test_empty_ingredients_list,
        test_additional_ingredient_fields,
        test_special_ml_conversions,
        test_rounding_to_quarter_oz
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
