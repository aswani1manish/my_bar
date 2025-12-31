# Recipe Management Page - User Guide

## Overview
A new admin page has been added to manage cocktail recipes. This page allows you to create, read, update, and delete recipes with full ingredient management and image upload support.

## Accessing the Recipe Management Page

1. Navigate to the admin panel: `http://your-domain/admin.html`
2. Click on **"Recipes"** in the navigation menu
3. You'll be taken to the Recipe Management page

## Features

### 1. Create a New Recipe

To create a new recipe:

1. Click the **"Create New Recipe"** button or ensure the form is clear
2. Fill in the recipe details:
   - **Name** (required): The name of your cocktail
   - **Description**: A brief description of the recipe
   - **Instructions**: Step-by-step instructions for making the cocktail
3. Add ingredients:
   - Click **"Add Ingredient"**
   - Select an ingredient from the dropdown (loaded from the ingredients table)
   - Enter the quantity (e.g., "2")
   - Enter the unit (e.g., "oz", "ml", "dash")
   - Repeat for all ingredients
4. Add images (optional):
   - Click the upload area
   - Select one or more images from your computer
   - Images will be previewed
5. Add tags (optional):
   - Type a tag name and click "Add"
   - Tags help with organization and searching
6. Click **"Create"** to save the recipe

The system will display a success message with the new recipe's ID.

### 2. Edit an Existing Recipe

To edit a recipe:

1. Enter the recipe ID in the **"Lookup Recipe"** field
2. Click **"Lookup"** or press Enter
3. The recipe details will be loaded into the form
4. Make your changes:
   - Update any field (name, description, instructions)
   - Add/remove ingredients
   - Add/remove images
   - Modify tags
5. Click **"Update"** to save changes

### 3. Delete a Recipe

To delete a recipe:

1. Lookup the recipe (see "Edit an Existing Recipe" above)
2. Click the **"Delete"** button
3. Confirm the deletion when prompted

**Warning**: Deletion is permanent and cannot be undone.

### 4. View Recipe Collections

When editing a recipe, the page will automatically display which collections contain this recipe. This is a read-only view. To add a recipe to a collection, go to the Collections page.

## Tips and Best Practices

### Ingredient Selection
- All ingredients must be selected from the pre-loaded ingredients table
- If an ingredient is missing, add it to the ingredients table first
- You can view all available ingredients by going to the Ingredients page

### Image Upload
- Supported formats: PNG, JPG, GIF
- Maximum file size: 16MB total
- You can upload multiple images at once
- Images can be removed by clicking the X button on the preview

### Tags
- Use tags to categorize recipes (e.g., "classic", "tequila", "refreshing")
- Tags make it easier to search and filter recipes later
- Common tag categories:
  - Spirit type: "gin", "vodka", "rum", "whiskey"
  - Flavor profile: "citrus", "sweet", "bitter", "herbal"
  - Occasion: "party", "nightcap", "brunch"
  - Difficulty: "easy", "intermediate", "advanced"

### Instructions Format
- Write clear, numbered steps
- Include timing information where relevant
- Mention specific techniques (shake, stir, muddle)
- Include garnish instructions

## Example: Creating a Margarita

Here's an example of creating a classic Margarita:

1. **Name**: Classic Margarita
2. **Description**: A refreshing tequila-based cocktail with lime and orange liqueur
3. **Instructions**:
   ```
   1. Add ice to a cocktail shaker
   2. Add tequila, lime juice, and triple sec
   3. Shake vigorously for 15 seconds
   4. Strain into a salt-rimmed glass over fresh ice
   5. Garnish with a lime wheel
   ```
4. **Ingredients**:
   - Tequila - 2 - oz
   - Lime Juice - 1 - oz
   - Triple Sec - 0.5 - oz
5. **Tags**: classic, tequila, citrus, shaken

## API Integration

The recipe management page uses the following API endpoints:

- `POST /api/recipes` - Create a new recipe
- `GET /api/recipes/:id` - Get a recipe by ID
- `PUT /api/recipes/:id` - Update a recipe
- `DELETE /api/recipes/:id` - Delete a recipe
- `GET /api/ingredients` - List all ingredients (for selection)
- `GET /api/collections` - List all collections (for display)

## Troubleshooting

### Recipe Not Loading
- Verify the recipe ID is correct
- Check that the backend server is running
- Check browser console for errors

### Ingredients Not Appearing
- Ensure the ingredients table has been populated
- Go to the Ingredients page to verify ingredients exist
- Check that the backend API is accessible

### Images Not Uploading
- Check file size (must be under 16MB)
- Verify file format (PNG, JPG, or GIF)
- Ensure the backend has write permissions to the uploads folder

### Can't Find Recipe ID
- Use the public recipes page to browse recipes
- Check the database directly if you have access
- Create a new recipe if needed

## Technical Notes

### Data Validation
- Recipe name is required
- Each ingredient requires name, quantity, and unit
- All other fields are optional

### Image Storage
- Images are stored in the `backend/uploads/` directory
- Filenames are auto-generated to prevent conflicts
- Old images are automatically deleted when removed from a recipe

### Database Schema
Recipes are stored with the following structure:
```json
{
  "id": 1,
  "name": "Recipe Name",
  "description": "Description text",
  "instructions": "Step by step instructions",
  "ingredients": [
    {"name": "Ingredient 1", "quantity": "2", "unit": "oz"}
  ],
  "tags": ["tag1", "tag2"],
  "images": ["image1.jpg", "image2.jpg"],
  "created_at": "2025-12-31T19:00:00",
  "updated_at": "2025-12-31T19:30:00"
}
```

## Support

For issues or questions:
1. Check this user guide
2. Review the test suite in `backend/test_recipe_api.py`
3. Check the application logs
4. Contact the development team
