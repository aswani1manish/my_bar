# Bar Shelf Availability Filter

## Overview

This feature adds a toggle switch to the public recipes page that allows filtering recipes based on ingredient availability. When enabled, only recipes that can be made with ingredients available on the bar shelf are shown.

## Database Changes

### New Column: `bar_shelf_availability`

Added to the `ingredients` table:
- **Type**: `CHAR(1)`
- **Default**: `'N'`
- **Values**: 
  - `'Y'` = Ingredient is available on bar shelf
  - `'N'` = Ingredient is not available

## Backend Changes

### API Endpoint Update

**Endpoint**: `GET /api/recipes`

**New Query Parameter**: `bar_shelf_mode`
- When set to `'Y'` (case-insensitive), only returns recipes where all ingredients have `bar_shelf_availability = 'Y'`
- When not set or set to any other value, returns all recipes (no filtering)

### Implementation Details

The filter works as follows:
1. Fetches all recipes based on existing search/tag filters
2. If `bar_shelf_mode=Y`, iterates through each recipe's ingredients
3. For each ingredient, queries the ingredients table for `bar_shelf_availability`
4. Only includes recipes where ALL ingredients have `bar_shelf_availability = 'Y'`

## Frontend Changes

### UI Component

Added a toggle switch in the search/filter section:
- **Label**: "Bar Shelf Mode"
- **Icon**: Wine bottle icon (fas fa-wine-bottle)
- **Location**: Right side of the filter row

### Controller Update

- Added `$scope.barShelfMode` boolean variable
- Added `toggleBarShelfMode()` function to reload recipes when toggled
- Updated `loadRecipes()` to pass bar shelf mode parameter to API

### API Service Update

Updated `getRecipes()` function to accept optional `barShelfMode` parameter:
```javascript
getRecipes: function(search, tags, barShelfMode)
```

## Migration

For existing databases, run the migration script:

```bash
python3 backend/add_bar_shelf_column.py
```

For new installations, the column is automatically created by `init_db.py`.

## Setting Ingredient Availability

To mark ingredients as available on the bar shelf, update the database:

```sql
UPDATE ingredients 
SET bar_shelf_availability = 'Y' 
WHERE name IN ('Vodka', 'Gin', 'Rum', ...);
```

## Testing

Run the bar shelf filter tests:

```bash
python3 backend/test_bar_shelf.py
```

The test suite verifies:
1. Recipes are returned without filter when bar shelf mode is off
2. Only recipes with available ingredients are returned when bar shelf mode is on
3. Case-insensitivity of the filter parameter
4. Correct filtering logic

## User Experience

1. By default, all recipes are shown
2. When user toggles "Bar Shelf Mode" ON:
   - Only recipes that can be made with available ingredients are displayed
   - Recipe count updates accordingly
3. When user toggles "Bar Shelf Mode" OFF:
   - All recipes are shown again
4. The filter works in combination with search, tags, and collection filters
