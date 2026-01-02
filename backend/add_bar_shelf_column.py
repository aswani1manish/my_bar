#!/usr/bin/env python3
"""
Add bar_shelf_availability column to ingredients table
"""

import mysql.connector
from config import Config

def add_bar_shelf_column():
    """Add bar_shelf_availability column to ingredients table"""
    config = Config()
    
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'ingredients' 
            AND COLUMN_NAME = 'bar_shelf_availability'
        """, (config.MYSQL_DATABASE,))
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✓ Column 'bar_shelf_availability' already exists in ingredients table")
        else:
            # Add the column with default value 'N'
            cursor.execute("""
                ALTER TABLE ingredients 
                ADD COLUMN bar_shelf_availability CHAR(1) DEFAULT 'N'
            """)
            conn.commit()
            print("✓ Added 'bar_shelf_availability' column to ingredients table")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Adding bar_shelf_availability column to ingredients table")
    print("=" * 60)
    add_bar_shelf_column()
