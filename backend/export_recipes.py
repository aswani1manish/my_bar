#!/usr/bin/env python3
"""
Export all recipes from MySQL database to a text file.

The output file is formatted so that tools like ChatGPT can easily read and
understand each recipe including its name, description, ingredients (with
quantities and units), instructions, and tags.

USAGE:
------
# Export to default file (recipes_export.txt in current directory)
python3 export_recipes.py

# Export to a specific file
python3 export_recipes.py --output /path/to/recipes.txt

DATABASE CONFIGURATION:
-----------------------
Uses MySQL connection settings from environment variables or .env file:
- MYSQL_HOST (default: localhost)
- MYSQL_PORT (default: 3306)
- MYSQL_USER (default: root)
- MYSQL_PASSWORD (default: empty)
- MYSQL_DATABASE (default: neighborhood_sips)
"""

import sys
import json
import argparse
from datetime import datetime
import mysql.connector
from config import Config


def connect_to_db():
    """Connect to MySQL and return (conn, cursor) or exit on failure."""
    config = Config()
    print(f"Connecting to MySQL at {config.MYSQL_HOST}:{config.MYSQL_PORT} …")
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            connection_timeout=30,
        )
        cursor = conn.cursor(dictionary=True)
        print("✓ Connected to MySQL")
        return conn, cursor
    except mysql.connector.Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        print("Make sure MySQL is running and the database is initialised (run init_db.py).")
        sys.exit(1)


def fetch_recipes(cursor):
    """Fetch all recipes from the database."""
    cursor.execute("SELECT * FROM recipes")
    return cursor.fetchall()


def format_ingredients(ingredients_raw):
    """
    Parse and format the ingredients JSON field.

    The field may be stored as:
    - a Python list (already decoded by mysql-connector with dictionary=True)
    - a JSON string that needs decoding

    Each ingredient entry is expected to have at least a 'name' key and
    optionally 'amount', 'units', and 'notes' keys.
    """
    if isinstance(ingredients_raw, str):
        try:
            ingredients = json.loads(ingredients_raw)
        except (json.JSONDecodeError, TypeError):
            return ["  (could not parse ingredients)"]
    else:
        ingredients = ingredients_raw or []

    lines = []
    for ing in ingredients:
        if isinstance(ing, dict):
            name = ing.get("name", "Unknown")
            amount = ing.get("amount", "")
            units = ing.get("units", "")
            notes = ing.get("notes", "")

            parts = [f"  - {name}"]
            if amount or units:
                parts.append(f"({amount} {units})".strip())
            if notes:
                parts.append(f"[{notes}]")
            lines.append(" ".join(parts))
        else:
            lines.append(f"  - {ing}")

    return lines if lines else ["  (no ingredients listed)"]


def format_tags(tags_raw):
    """Parse and return a comma-separated tag string."""
    if isinstance(tags_raw, str):
        try:
            tags = json.loads(tags_raw)
        except (json.JSONDecodeError, TypeError):
            return tags_raw
    else:
        tags = tags_raw or []

    return ", ".join(str(t) for t in tags) if tags else "none"


def recipe_to_text(recipe):
    """Convert a single recipe row into a human-readable text block."""
    lines = []
    separator = "=" * 60

    lines.append(separator)
    lines.append(f"RECIPE: {recipe.get('name', 'Unnamed Recipe')}")
    lines.append(separator)

    description = (recipe.get("description") or "").strip()
    if description:
        lines.append(f"Description: {description}")

    lines.append("")
    lines.append("Ingredients:")
    lines.extend(format_ingredients(recipe.get("ingredients")))

    instructions = (recipe.get("instructions") or "").strip()
    if instructions:
        lines.append("")
        lines.append("Instructions:")
        for step in instructions.splitlines():
            lines.append(f"  {step}")

    tags_str = format_tags(recipe.get("tags"))
    if tags_str and tags_str != "none":
        lines.append("")
        lines.append(f"Tags: {tags_str}")

    lines.append("")
    return "\n".join(lines)


def export_recipes(output_path):
    """Main export routine."""
    conn, cursor = connect_to_db()

    try:
        recipes = fetch_recipes(cursor)
        print(f"Found {len(recipes)} recipe(s) in the database.")

        if not recipes:
            print("Nothing to export.")
            return

        header_lines = [
            "RECIPES EXPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total recipes: {len(recipes)}",
            "",
        ]

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(header_lines) + "\n")
            for recipe in recipes:
                f.write(recipe_to_text(recipe))

        print(f"✓ Exported {len(recipes)} recipe(s) to: {output_path}")

    finally:
        cursor.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Export all recipes from MySQL to a text file."
    )
    parser.add_argument(
        "--output",
        default="recipes_export.txt",
        help="Path to the output text file (default: recipes_export.txt)",
    )
    args = parser.parse_args()

    export_recipes(args.output)


if __name__ == "__main__":
    sys.exit(main())
