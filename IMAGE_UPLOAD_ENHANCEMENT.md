# Image Upload Enhancement: Original Filename Preservation and EXIF Orientation Handling

## Overview

This document describes the changes made to preserve original image filenames during recipe and collection creation/update operations, as well as the handling of EXIF orientation metadata.

## Problem Statement

Previously, the application would:
1. Generate new filenames using UUID and timestamps, losing the original filename
2. Not handle EXIF orientation metadata, causing some images to display with incorrect orientation

## Solution

### Backend Changes (`app.py`)

#### 1. New `sanitize_filename()` Function

Safely sanitizes user-provided filenames to prevent security issues:
- Uses `os.path.basename()` to prevent directory traversal attacks
- Removes potentially problematic characters
- Preserves alphanumeric characters, dots, dashes, and underscores
- Returns `None` for invalid filenames

```python
def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal and other security issues.
    Preserves original filename while ensuring safety.
    """
    if not filename:
        return None
    
    # Get the basename to prevent directory traversal
    filename = os.path.basename(filename)
    
    # Remove any remaining path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Replace any potentially problematic characters
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
    
    # Remove any leading/trailing whitespace or dots
    filename = filename.strip().strip('.')
    
    return filename if filename else None
```

#### 2. Enhanced `save_base64_image()` Function

Updated to accept and preserve original filenames:
- New parameter: `original_filename` (optional)
- Uses `exif_transpose()` to automatically handle EXIF orientation
- Handles filename collisions by appending a counter
- Maintains backward compatibility with old format

Key features:
- **EXIF Orientation**: Uses PIL's `exif_transpose()` to automatically rotate images based on EXIF orientation tag and reset it to normal (1)
- **Filename Preservation**: Uses sanitized original filename when provided
- **Collision Handling**: Adds `_1`, `_2`, etc. suffix when filename already exists
- **Format Preservation**: Saves images in their original format (JPEG, PNG, GIF) when possible
- **Backward Compatible**: Falls back to prefix-based naming when no filename provided

#### 3. Updated API Endpoints

Modified to accept image data in new format while maintaining backward compatibility:

**Recipe Creation (`POST /api/recipes`)**:
```python
# New format (with filename)
images: [
    {
        "data": "data:image/jpeg;base64,...",
        "filename": "my_cocktail.jpg"
    }
]

# Legacy format (still supported)
images: ["data:image/jpeg;base64,..."]
```

**Recipe Update (`PUT /api/recipes/<id>`)**:
- Same format as creation
- Preserves existing images by filename string
- Adds new images with original filenames

**Collection Update (`PUT /api/collections/<id>`)**:
- Same enhancements as recipe update

### Frontend Changes (`image-upload.js`)

Modified the AngularJS directive to:
1. Capture the original filename from the file input
2. Send both the base64 data and filename to the backend
3. Maintain backward compatibility with existing saved images

Key changes:
- Stores `file.name` along with base64 data
- Sends new images as `{data: "...", filename: "..."}` objects
- Keeps existing images as simple filename strings

## Testing

Three comprehensive test files were created:

### 1. `test_image_preservation.py`
Tests core functionality:
- Filename sanitization with various inputs
- Image saving with original filename
- Filename collision handling
- EXIF orientation preservation

### 2. `test_api_image_handling.py`
Tests API integration:
- Recipe creation with new format
- Recipe creation with legacy format (backward compatibility)
- Recipe update with mixed formats

### 3. `test_exif_orientation.py`
Tests EXIF handling:
- Multiple orientation values (1, 3, 6, 8)
- Automatic rotation based on EXIF data
- Dimension swapping for rotated images
- EXIF data preservation

All tests pass successfully.

## Security Considerations

1. **Directory Traversal Prevention**: `os.path.basename()` prevents path traversal attacks
2. **Character Sanitization**: Special characters are replaced to prevent injection attacks
3. **Filename Validation**: Empty or invalid filenames are rejected
4. **Size Limits**: Existing image size limits still apply (max 1024x1024)

## Backward Compatibility

The implementation maintains full backward compatibility:
- Legacy image upload format (just base64 string) still works
- Existing images stored with old filenames continue to work
- Frontend can progressively adopt the new format
- No database schema changes required

## Benefits

1. **User Experience**: Users can identify images by their original names
2. **Image Orientation**: Photos from phones/cameras display correctly
3. **Organization**: Easier to manage and identify uploaded images
4. **No Breaking Changes**: Existing functionality continues to work

## Example Usage

### Frontend (AngularJS)
```javascript
// The directive automatically handles this
// When user selects a file, it captures both data and filename
scope.images = [
    {
        data: "data:image/jpeg;base64,/9j/4AAQ...",
        filename: "mojito_recipe.jpg"
    }
];
```

### Backend (Flask)
```python
# API endpoint receives the data and processes it
if isinstance(img_data, dict) and 'data' in img_data:
    filename = save_base64_image(
        img_data['data'], 
        'recipe', 
        img_data.get('filename')
    )
    # Saves as: mojito_recipe.jpg (or mojito_recipe_1.jpg if collision)
```

## Files Modified

1. `backend/app.py` - Core functionality
2. `backend/static/js/directives/image-upload.js` - Frontend directive
3. `backend/test_image_preservation.py` - New test file
4. `backend/test_api_image_handling.py` - New test file
5. `backend/test_exif_orientation.py` - New test file

## Future Enhancements

Possible future improvements:
1. Add more image format support (WebP, AVIF)
2. Provide option to disable filename preservation
3. Add configurable filename sanitization rules
4. Support additional EXIF metadata preservation
