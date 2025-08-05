#!/usr/bin/env python3
"""
Migration script to add tags column to sft_links table.

This script adds a new TEXT[] column called 'tags' to the sft_links table
to allow storing tags directly on links between files.
"""

import sys
import logging
from database import get_database_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_add_link_tags():
    """
    Add tags column to sft_links table.
    
    Returns:
        bool: True if migration was successful, False otherwise
    """
    connection = None
    try:
        logger.info("Starting migration: Adding tags column to sft_links table")
        
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Check if the column already exists
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'sft_links' 
        AND column_name = 'tags'
        """
        
        cursor.execute(check_sql)
        result = cursor.fetchone()
        
        if result:
            logger.info("Column 'tags' already exists in sft_links table. Migration not needed.")
            print("✅ Column 'tags' already exists in sft_links table.")
            return True
        
        # Add the tags column
        alter_sql = "ALTER TABLE sft_links ADD COLUMN tags TEXT[]"
        
        logger.info("Executing: ALTER TABLE sft_links ADD COLUMN tags TEXT[]")
        cursor.execute(alter_sql)
        
        # Commit the transaction
        connection.commit()
        
        logger.info("Successfully added tags column to sft_links table")
        print("✅ Successfully added 'tags' column to sft_links table!")
        print("   The sft_links table now supports storing tags on links.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        print(f"❌ Migration failed: {e}")
        
        # Rollback the transaction if there was an error
        if connection:
            connection.rollback()
        
        return False
        
    finally:
        if connection:
            connection.close()


def main():
    """Main function to run the migration."""
    print("🔧 SFT Database Migration: Add Tags to Links")
    print("=" * 50)
    
    try:
        success = migrate_add_link_tags()
        
        if success:
            print("\n🎉 Migration completed successfully!")
            print("   You can now use tags on links in the SFT system.")
        else:
            print("\n💥 Migration failed!")
            print("   Please check the error messages above and try again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 