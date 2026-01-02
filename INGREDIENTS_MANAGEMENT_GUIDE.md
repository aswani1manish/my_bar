# Ingredients Management Guide

This guide explains how to use the ingredients management feature in the admin interface.

## Overview

The ingredients management page allows administrators to create, read, update, and delete ingredients in the Neighborhood Sips database. All ingredients include support for the complete database schema including the `bar_shelf_availability` field.

## Accessing the Feature

1. Navigate to the admin interface: `/admin.html`
2. Click on "Ingredients" in the navigation menu
3. The ingredients management page will load at `#!/ingredients`

## Features

### View All Ingredients

- The main view displays all ingredients in a table format
- Each row shows:
  - Image (first image if available)
  - Name
  - Category
  - Description
  - Tags
  - Bar Shelf availability (checkbox)
  - Action buttons (Edit/Delete)

### Search and Filter

- **Search**: Enter text to search by ingredient name or description
- **Filter by Tags**: Enter comma-separated tags to filter ingredients

### Create New Ingredient

1. Fill in the form at the top of the page:
   - **Name** (required): The ingredient name
   - **Category**: e.g., Spirit, Liqueur, Mixer
   - **Description**: Detailed description of the ingredient
   - **Bar Shelf Availability**: Select "Yes" or "No" (default: "Yes")
   - **Images**: Click to upload ingredient images (PNG, JPG, GIF up to 16MB)
   - **Tags**: Add tags by typing and clicking "Add"
2. Click "Create" to save the ingredient

### Edit Ingredient

1. Click the Edit button (pencil icon) on any ingredient row
2. The form at the top will populate with the ingredient's current data
3. Modify any fields as needed
4. Click "Update" to save changes
5. Click "Cancel" to discard changes

### Delete Ingredient

1. Click the Delete button (trash icon) on any ingredient row
2. Confirm the deletion when prompted
3. The ingredient will be permanently removed

### Toggle Bar Shelf Availability

You can quickly toggle the bar shelf availability for any ingredient:
- Click the checkbox in the "Bar Shelf" column
- The change is saved immediately
- No need to edit the full ingredient

## Database Schema

All ingredient records include the following fields:

| Field | Type | Description |
|-------|------|-------------|
| id | int | Auto-generated unique identifier |
| name | varchar(255) | Ingredient name (required) |
| description | text | Detailed description |
| category | varchar(100) | Category (e.g., Spirit, Liqueur) |
| tags | json | Array of tags |
| images | json | Array of image filenames |
| bar_shelf_availability | varchar(1) | 'Y' or 'N' (default: 'Y') |
| created_at | datetime | Auto-generated creation timestamp |
| updated_at | datetime | Auto-updated modification timestamp |

## API Endpoints

The following REST API endpoints are available:

- `GET /api/ingredients` - List all ingredients (supports search and tag filters)
- `GET /api/ingredients/<id>` - Get a single ingredient
- `POST /api/ingredients` - Create a new ingredient
- `PUT /api/ingredients/<id>` - Update an ingredient
- `DELETE /api/ingredients/<id>` - Delete an ingredient
- `PATCH /api/ingredients/<id>/bar-shelf` - Toggle bar shelf availability only

## Integration with Recipes

The `bar_shelf_availability` field integrates with the recipe filtering system:
- When viewing recipes, you can filter by "Bar Shelf Mode"
- Only recipes with all ingredients marked as available (bar_shelf_availability = 'Y') will be shown
- This helps bartenders know which drinks they can make with current inventory

## Tips

- **Images**: Upload clear, high-quality images of ingredients for better visual identification
- **Tags**: Use consistent tags across ingredients (e.g., "spirit", "base", "sweet") for easier filtering
- **Categories**: Standardize categories (Spirit, Liqueur, Mixer, Bitters, etc.) for better organization
- **Bar Shelf**: Keep this updated to reflect your current inventory
- **Description**: Include relevant information like origin, flavor profile, typical uses

## Technical Details

- **Frontend**: AngularJS application with Bootstrap styling
- **Backend**: Flask REST API with MySQL database
- **Image Storage**: Images are saved to the `backend/uploads` directory
- **Security**: All inputs are validated; SQL injection protection via parameterized queries
- **Image Processing**: Images are automatically resized to max 1024x1024 pixels
