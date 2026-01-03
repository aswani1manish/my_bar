# Convert ML to OZ Script

This script converts recipe ingredient measurements from milliliters (ml) to fluid ounces (Oz) in the MySQL recipes table.

## What It Does

1. **Creates a Backup**: Automatically creates a timestamped backup table (e.g., `recipes_backup_20260103_165600`) with all recipe data before making any changes
2. **Processes All Recipes**: Reads all recipes from the database
3. **Converts Units**: For each ingredient with unit 'ml', converts to 'Oz' by dividing the amount by 30
   - Example: 30 ml → 1 Oz
   - Example: 22.5 ml → 0.75 Oz
   - Example: 60 ml → 2 Oz
4. **Updates Database**: Saves the converted ingredients back to the recipes table
5. **Provides Summary**: Shows detailed statistics about what was converted

## Prerequisites

- Python 3.8 or higher
- MySQL database running and accessible
- Database initialized with recipes table (run `init_db.py` first)
- Dependencies installed: `pip install -r requirements.txt`

## Usage

### 1. Preview Changes (Dry Run) - Recommended First Step

```bash
cd backend
python3 convert_ml_to_oz.py --dry-run
```

This will show you:
- How many recipes will be affected
- Which ingredients will be converted
- Preview of conversions (e.g., "45 ml → 1.5 Oz")
- **No changes are saved to the database**

### 2. Apply Conversion (With Backup)

```bash
python3 convert_ml_to_oz.py
```

This will:
- Create a backup table with timestamp
- Apply all conversions
- Show detailed summary
- **Permanently updates the database**

### 3. Apply Without Backup (Not Recommended)

```bash
python3 convert_ml_to_oz.py --no-backup
```

Only use this if you're absolutely sure or have an external backup.

## Example Output

```
Connecting to MySQL at localhost:3306
Database: neighborhood_sips
✓ Connected to MySQL

Creating backup table: recipes_backup_20260103_165600
✓ Backup created successfully: recipes_backup_20260103_165600
  - 25 records backed up

================================================================================
Converting Recipe Ingredients from ml to Oz
================================================================================

Found 25 recipes to process

  ✓ Margarita (ID: 1)
    - Converted 2 ingredient(s) from ml to Oz
  ✓ Mojito (ID: 2)
    - Converted 3 ingredient(s) from ml to Oz
  ✓ Cosmopolitan (ID: 3)
    - Converted 3 ingredient(s) from ml to Oz

================================================================================
Conversion Summary
================================================================================
Total recipes processed: 25
Recipes modified: 15
Total ingredient conversions: 42

Recipes with ml conversions:
  - Margarita (ID: 1): 2 conversion(s)
  - Mojito (ID: 2): 3 conversion(s)
  - Cosmopolitan (ID: 3): 3 conversion(s)
  ...

✓ All conversions have been applied successfully!

💾 Backup table: recipes_backup_20260103_165600
   (You can restore from this backup if needed)
```

## Features

### Robust Conversion Logic

- **Case-Insensitive**: Recognizes 'ml', 'ML', 'Ml', etc.
- **String Amounts**: Handles amounts stored as strings (e.g., "30") or numbers
- **Decimal Precision**: Correctly converts decimal amounts (e.g., 22.5 ml → 0.75 Oz)
- **Mixed Units**: Only converts ml units, preserves others (oz, dashes, tsp, etc.)
- **Error Handling**: Gracefully handles invalid or missing data

### Preserves Data Integrity

- All other ingredient fields are preserved (id, name, optional, note, etc.)
- Non-ml units remain unchanged
- Recipe metadata (name, description, instructions, etc.) is not affected

### Safety Features

- **Automatic Backup**: Creates timestamped backup before any changes
- **Dry Run Mode**: Preview changes without applying them
- **Transaction Safety**: Uses database transactions with rollback on errors
- **Detailed Logging**: Shows exactly what was converted

## Restoring from Backup

If you need to restore the original data:

```sql
-- View available backups
SHOW TABLES LIKE 'recipes_backup%';

-- Restore from a specific backup (replace with your backup table name)
DROP TABLE recipes;
CREATE TABLE recipes LIKE recipes_backup_20260103_165600;
INSERT INTO recipes SELECT * FROM recipes_backup_20260103_165600;
```

## Testing

A comprehensive test suite is included to verify the conversion logic:

```bash
python3 test_convert_ml_to_oz.py
```

This runs 9 tests covering:
- Basic ml to Oz conversions
- Decimal values
- String amounts
- Case-insensitive unit matching
- Preservation of non-ml units
- Mixed unit recipes
- Error handling for invalid data
- Empty ingredient lists
- Field preservation

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without applying them |
| `--no-backup` | Skip creating backup table (not recommended) |

## Notes

- The conversion ratio is 1 Oz = 30 ml (standard for cocktail recipes)
- The script is idempotent - running it multiple times on already-converted data won't cause issues
- Only ingredients with unit exactly matching 'ml' (case-insensitive) are converted
- The backup table name includes a timestamp for easy identification

## Troubleshooting

### "Error connecting to MySQL"
- Ensure MySQL is running: `sudo systemctl status mysql` (Linux) or check services (Windows/Mac)
- Check your `.env` file or environment variables for correct MySQL credentials
- Verify database exists: `mysql -u root -p` then `SHOW DATABASES;`

### "No recipes were found"
- Run `init_db.py` to create the database schema
- Load some recipes first using `load_recipes.py`

### "Invalid JSON"
- Some recipes may have malformed JSON in the ingredients field
- The script will skip these and continue with others
- Check the output for which recipes were skipped

## Support

For issues or questions, please create an issue in the GitHub repository.
