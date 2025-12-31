# MySQL Collections Table - Sample Entries and Query Examples

This document provides sample MySQL entry formats for the Collections table in the Neighborhood Sips application.

## Table Schema

The Collections table has the following structure:

```sql
CREATE TABLE IF NOT EXISTS collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    recipe_ids JSON,
    tags JSON,
    images JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | INT | Auto | Primary key, auto-incremented |
| `name` | VARCHAR(255) | Yes | Name of the collection |
| `description` | TEXT | No | Detailed description of the collection |
| `recipe_ids` | JSON | No | Array of recipe IDs included in this collection (e.g., `[1, 5, 12]`) |
| `tags` | JSON | No | Array of tags for categorization (e.g., `["summer", "refreshing"]`) |
| `images` | JSON | No | Array of image filenames (e.g., `["collection1.jpg", "collection2.jpg"]`) |
| `created_at` | DATETIME | Auto | Timestamp when the record was created |
| `updated_at` | DATETIME | Auto | Timestamp when the record was last updated |

## Important Notes

1. **JSON Fields**: The `recipe_ids`, `tags`, and `images` fields must be valid JSON strings
2. **Recipe IDs**: Must reference existing recipe IDs in the recipes table
3. **Images**: Image filenames should correspond to files in the uploads directory
4. **Character Encoding**: UTF-8 support for international characters in names and descriptions

## Sample INSERT Queries

### Example 1: Classic Cocktails Collection

```sql
INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
VALUES (
    'Classic Cocktails',
    'A curated collection of timeless cocktail recipes that every bartender should know. From the elegant Martini to the refreshing Mojito, these are the drinks that have stood the test of time.',
    '[1, 2, 3, 5, 8]',
    '["classics", "essential", "timeless"]',
    '["classic_cocktails_1.jpg", "classic_cocktails_2.jpg"]',
    NOW(),
    NOW()
);
```

### Example 2: Summer Refreshers Collection

```sql
INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
VALUES (
    'Summer Refreshers',
    'Light and refreshing cocktails perfect for hot summer days. These drinks feature fresh citrus, cooling mint, and tropical flavors.',
    '[4, 7, 12, 15, 18]',
    '["summer", "refreshing", "citrus", "seasonal"]',
    '["summer_drinks.jpg"]',
    NOW(),
    NOW()
);
```

### Example 3: Gin-Based Cocktails Collection

```sql
INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
VALUES (
    'Gin Lovers Collection',
    'Celebrate the botanical complexity of gin with this collection of gin-forward cocktails. From classic gin and tonics to creative modern variations.',
    '[2, 6, 9, 14]',
    '["gin", "botanical", "spirits"]',
    '[]',
    NOW(),
    NOW()
);
```

### Example 4: Holiday Specials Collection

```sql
INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
VALUES (
    'Holiday Specials',
    'Festive cocktails perfect for holiday gatherings and celebrations. Warm spices, rich flavors, and beautiful presentations.',
    '[20, 21, 22]',
    '["holiday", "winter", "festive", "seasonal"]',
    '["holiday_1.jpg", "holiday_2.jpg", "holiday_3.jpg"]',
    NOW(),
    NOW()
);
```

### Example 5: Empty Collection (Template)

```sql
INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
VALUES (
    'My Custom Collection',
    'A new collection waiting to be filled with recipes.',
    '[]',
    '[]',
    '[]',
    NOW(),
    NOW()
);
```

### Example 6: Tiki Drinks Collection

```sql
INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
VALUES (
    'Tropical Tiki Paradise',
    'Transport yourself to a tropical island with these exotic tiki cocktails. Complex rum blends, tropical juices, and elaborate garnishes make these drinks a vacation in a glass.',
    '[11, 13, 16, 19, 23, 25]',
    '["tiki", "tropical", "rum", "exotic"]',
    '["tiki_bar.jpg", "tropical_drinks.jpg"]',
    NOW(),
    NOW()
);
```

## Batch Insert Example

Insert multiple collections at once:

```sql
INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
VALUES 
(
    'Aperitif Hour',
    'Pre-dinner drinks to stimulate the appetite. Light, bitter, and perfect for conversation.',
    '[30, 31, 32]',
    '["aperitif", "pre-dinner", "bitter"]',
    '["aperitif_collection.jpg"]',
    NOW(),
    NOW()
),
(
    'Nightcaps',
    'Rich, warming cocktails perfect for ending the evening. These drinks are meant to be sipped slowly.',
    '[40, 41, 42, 43]',
    '["nightcap", "after-dinner", "dessert"]',
    '["nightcap_collection.jpg"]',
    NOW(),
    NOW()
),
(
    'Low ABV Cocktails',
    'Delicious cocktails with lower alcohol content. Perfect for day drinking or extended sessions.',
    '[50, 51, 52, 53, 54]',
    '["low-alcohol", "session", "light"]',
    '[]',
    NOW(),
    NOW()
);
```

## Query Examples

### Select All Collections

```sql
SELECT * FROM collections;
```

### Select Collection with Specific ID

```sql
SELECT * FROM collections WHERE id = 1;
```

### Search Collections by Name

```sql
SELECT * FROM collections WHERE name LIKE '%summer%';
```

### Filter Collections by Tag

```sql
SELECT * FROM collections 
WHERE JSON_CONTAINS(tags, '"summer"', '$');
```

### Get Collections with Multiple Specific Tags

```sql
SELECT * FROM collections 
WHERE JSON_CONTAINS(tags, '"summer"', '$') 
  AND JSON_CONTAINS(tags, '"refreshing"', '$');
```

### Get Collections Ordered by Creation Date

```sql
SELECT * FROM collections 
ORDER BY created_at DESC;
```

### Count Total Collections

```sql
SELECT COUNT(*) as total_collections FROM collections;
```

### Get Collections with Specific Recipe

```sql
SELECT * FROM collections 
WHERE JSON_CONTAINS(recipe_ids, '5', '$');
```

### Update Collection Description

```sql
UPDATE collections 
SET description = 'Updated description for this amazing collection',
    updated_at = NOW()
WHERE id = 1;
```

### Add Recipe to Collection

```sql
UPDATE collections 
SET recipe_ids = JSON_ARRAY_APPEND(recipe_ids, '$', 99),
    updated_at = NOW()
WHERE id = 1;
```

### Add Tag to Collection

```sql
UPDATE collections 
SET tags = JSON_ARRAY_APPEND(tags, '$', 'new-tag'),
    updated_at = NOW()
WHERE id = 1;
```

### Delete Collection

```sql
DELETE FROM collections WHERE id = 1;
```

## Python Integration Example

Here's how to insert a collection using Python with mysql.connector:

```python
import mysql.connector
import json
from datetime import datetime, timezone

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='neighborhood_sips',
    password='your_password',
    database='neighborhood_sips'
)
cursor = conn.cursor()

# Collection data
collection_data = {
    'name': 'Modern Classics',
    'description': 'Contemporary takes on classic cocktails with modern techniques and ingredients.',
    'recipe_ids': [10, 15, 20, 25],
    'tags': ['modern', 'innovative', 'craft'],
    'images': ['modern_classics.jpg']
}

# INSERT query
query = """
    INSERT INTO collections (name, description, recipe_ids, tags, images, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# Execute
now = datetime.now(timezone.utc)
params = (
    collection_data['name'],
    collection_data['description'],
    json.dumps(collection_data['recipe_ids']),
    json.dumps(collection_data['tags']),
    json.dumps(collection_data['images']),
    now,
    now
)

cursor.execute(query, params)
conn.commit()

print(f"Collection '{collection_data['name']}' created with ID: {cursor.lastrowid}")

cursor.close()
conn.close()
```

## Troubleshooting

### Invalid JSON Error

If you get a JSON parsing error, ensure your JSON fields are properly formatted:

```sql
-- ❌ Wrong: Single quotes or malformed JSON
recipe_ids = '[1, 2, 3'

-- ✅ Correct: Valid JSON string
recipe_ids = '[1, 2, 3]'
```

### Character Encoding Issues

If you see garbled characters, ensure your connection uses UTF-8:

```sql
SET NAMES utf8mb4;
```

### Foreign Key Constraints

Remember that recipe_ids should reference existing recipes in the recipes table. Verify recipe IDs exist before creating the collection:

```sql
SELECT id FROM recipes WHERE id IN (1, 2, 3, 5, 8);
```

## Additional Resources

- See `init_db.py` for table creation script
- See `app.py` for API endpoint implementations
- See `MYSQL_MIGRATION.md` for migration from MongoDB
- See `README.md` for application overview
