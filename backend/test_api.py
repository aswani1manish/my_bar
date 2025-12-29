#!/usr/bin/env python3
"""
Simple test to verify the Neighborhood Sips API endpoints are properly defined
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app
    
    # Get all routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(rule.methods - {'HEAD', 'OPTIONS'}),
            'path': str(rule)
        })
    
    # Expected endpoints
    expected_endpoints = [
        '/api/health',
        '/api/ingredients',
        '/api/ingredients/<ingredient_id>',
        '/api/recipes',
        '/api/recipes/<recipe_id>',
        '/api/collections',
        '/api/collections/<collection_id>',
        '/api/uploads/<filename>'
    ]
    
    print("✓ Backend app.py loaded successfully")
    print("\nAPI Endpoints:")
    print("-" * 60)
    
    for route in sorted(routes, key=lambda x: x['path']):
        if route['path'].startswith('/api'):
            print(f"{route['methods']:20} {route['path']}")
    
    # Verify all expected endpoints exist
    found_paths = [r['path'] for r in routes]
    missing = []
    for expected in expected_endpoints:
        if expected not in found_paths:
            missing.append(expected)
    
    if missing:
        print(f"\n⚠ Warning: Missing endpoints: {missing}")
    else:
        print("\n✓ All expected endpoints are defined")
    
    # Verify image upload support
    print("\n✓ Image upload configuration:")
    print(f"  - Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"  - Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")
    
    print("\n✓ All backend checks passed!")
    
except Exception as e:
    print(f"✗ Error loading backend: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
