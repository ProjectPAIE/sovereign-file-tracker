import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
import logging

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_database_connection():
    """
    Create a connection to PostgreSQL database using settings from config.py.
    
    Returns:
        psycopg2.connection: Database connection object
    """
    try:
        # Validate required database settings
        if not all([DB_NAME, DB_USER, DB_PASSWORD]):
            raise ValueError(
                "Missing required database settings in config.py. Please set DB_NAME, DB_USER, and DB_PASSWORD"
            )
        
        # Create connection using settings from config
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        
        logger.info(f"Successfully connected to PostgreSQL database: {DB_NAME}")
        return connection
        
    except psycopg2.Error as e:
        logger.error(f"Error connecting to PostgreSQL database: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database connection: {e}")
        raise


def create_file_lineage_table(connection = None):
    """
    Create the file_lineage table if it doesn't already exist.
    The table schema matches the CalRecord Pydantic model.
    
    Args:
        connection: Optional database connection. If not provided, a new one will be created.
    
    Returns:
        bool: True if table was created successfully, False if it already exists
    """
    # SQL to create the file_lineage table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS file_lineage (
        id UUID NOT NULL,
        revision INTEGER NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        archive_path TEXT NOT NULL,
        tags TEXT[], -- PostgreSQL array of strings
        notes TEXT,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
        
        -- Composite primary key on id and revision
        PRIMARY KEY(id, revision)
    );
    
    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_file_lineage_id ON file_lineage(id);
    CREATE INDEX IF NOT EXISTS idx_file_lineage_revision ON file_lineage(revision);
    CREATE INDEX IF NOT EXISTS idx_file_lineage_timestamp ON file_lineage(timestamp);
    CREATE INDEX IF NOT EXISTS idx_file_lineage_original_filename ON file_lineage(original_filename);
    """
    
    should_close_connection = False
    
    try:
        # Use provided connection or create a new one
        if connection is None:
            connection = get_database_connection()
            should_close_connection = True
        
        cursor = connection.cursor()
        
        # Execute the table creation SQL
        cursor.execute(create_table_sql)
        connection.commit()
        
        logger.info("file_lineage table created successfully (or already existed)")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Error creating file_lineage table: {e}")
        if connection:
            connection.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating file_lineage table: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if should_close_connection and connection:
            connection.close()


def test_database_connection():
    """
    Test function to verify database connection and table creation.
    """
    try:
        # Test connection
        connection = get_database_connection()
        logger.info("Database connection test successful")
        
        # Test table creation
        create_file_lineage_table(connection)
        logger.info("Table creation test successful")
        
        # Close connection
        connection.close()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False


if __name__ == "__main__":
    # Run test if script is executed directly
    test_database_connection()
