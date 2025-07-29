import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import shutil
import time
import uuid
import subprocess
import tempfile
import os
from pathlib import Path

from schemas import CalRecord
from database import get_database_connection
from config import INGEST_DIR, UPDATE_DIR, ARCHIVE_DIR, SYMLINK_DIR, CATEGORIES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_new_cal_record(original_filename: str, archive_path: str) -> Optional[CalRecord]:
    """
    Create a new CalRecord and insert it into the file_lineage table.
    
    Args:
        original_filename: The original human-readable name of the file
        archive_path: The absolute path where the file is stored
        
    Returns:
        CalRecord: The created record if successful, None if failed
    """
    connection = None
    try:
        # Create a new CalRecord with default revision 1
        cal_record = CalRecord(
            original_filename=original_filename,
            archive_path=archive_path
        )
        
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Insert the record into the file_lineage table
        insert_sql = """
        INSERT INTO file_lineage (id, revision, original_filename, archive_path, tags, notes, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            str(cal_record.id),
            cal_record.revision,
            cal_record.original_filename,
            cal_record.archive_path,
            cal_record.tags,
            cal_record.notes,
            cal_record.timestamp
        ))
        
        connection.commit()
        logger.info(f"Successfully created new CalRecord for file: {original_filename}")
        return cal_record
        
    except psycopg2.Error as e:
        logger.error(f"Database error creating CalRecord for {original_filename}: {e}")
        if connection:
            connection.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating CalRecord for {original_filename}: {e}")
        if connection:
            connection.rollback()
        return None
    finally:
        if connection:
            connection.close()


def _get_file_category(file_path: Path) -> str:
    """
    Determine the category of a file based on its location or extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Category string (AUDIO, BLOBS, IMAGES, TEXT)
    """
    # First check if it's in a specific ingest subdirectory
    if file_path.parent.name in CATEGORIES:
        return file_path.parent.name
    
    # Fallback to extension-based categorization
    extension = file_path.suffix.lower()
    
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'}
    text_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.rtf', '.odt', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.c', '.h', '.sql'}
    
    if extension in audio_extensions:
        return "AUDIO"
    elif extension in image_extensions:
        return "IMAGES"
    elif extension in text_extensions:
        return "TEXT"
    else:
        return "BLOBS"  # Default category for unknown file types


def ingest_new_file(filepath: str) -> Optional[CalRecord]:
    """
    Ingest a new file into the SFT system.
    
    Args:
        filepath: Path to the file to ingest
        
    Returns:
        CalRecord: The created record if successful, None if failed
    """
    try:
        file_path = Path(filepath)
        
        # Validate file exists
        if not file_path.exists():
            logger.error(f"File does not exist: {filepath}")
            return None
        
        if not file_path.is_file():
            logger.error(f"Path is not a file: {filepath}")
            return None
        
        # Determine file category
        category = _get_file_category(file_path)
        logger.info(f"File category determined: {category}")
        
        # Create archive directory if it doesn't exist
        archive_category_dir = ARCHIVE_DIR / category
        archive_category_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique filename for archive
        timestamp = int(time.time())
        archive_filename = f"{timestamp}_{file_path.name}"
        archive_path = archive_category_dir / archive_filename
        
        # Move file to archive
        shutil.move(str(file_path), str(archive_path))
        logger.info(f"Moved file to archive: {archive_path}")
        
        # Create CalRecord
        cal_record = create_new_cal_record(file_path.name, str(archive_path))
        
        if cal_record:
            logger.info(f"Successfully ingested file: {file_path.name}")
            return cal_record
        else:
            logger.error(f"Failed to create CalRecord for: {file_path.name}")
            return None
            
    except Exception as e:
        logger.error(f"Error ingesting file {filepath}: {e}")
        return None


def get_records_by_identifier(identifier: str) -> List[Dict[str, Any]]:
    """
    Get records by identifier (UUID or filename).
    
    Args:
        identifier: UUID or filename to search for
        
    Returns:
        List of record dictionaries
    """
    connection = None
    try:
        # Check if identifier is a UUID
        try:
            uuid.UUID(identifier)
            is_uuid = True
        except ValueError:
            is_uuid = False
        
        connection = get_database_connection()
        cursor = connection.cursor()
        
        if is_uuid:
            # Search by UUID
            select_sql = """
            SELECT id, revision, original_filename, archive_path, tags, notes, timestamp
            FROM file_lineage 
            WHERE id = %s 
            ORDER BY revision DESC
            """
            cursor.execute(select_sql, (identifier,))
        else:
            # Search by filename
            select_sql = """
            SELECT id, revision, original_filename, archive_path, tags, notes, timestamp
            FROM file_lineage 
            WHERE original_filename ILIKE %s 
            ORDER BY revision DESC
            """
            cursor.execute(select_sql, (f"%{identifier}%",))
        
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        records = []
        for result in results:
            records.append({
                'id': result['id'],
                'revision': result['revision'],
                'original_filename': result['original_filename'],
                'archive_path': result['archive_path'],
                'tags': result['tags'] or [],
                'notes': result['notes'],
                'timestamp': result['timestamp']
            })
        
        return records
        
    except Exception as e:
        logger.error(f"Error getting records by identifier {identifier}: {e}")
        return []
    finally:
        if connection:
            connection.close()


def update_record_notes(record_id: str, revision: int, new_notes: str) -> bool:
    """
    Update the notes for a specific record.
    
    Args:
        record_id: UUID of the record
        revision: Revision number
        new_notes: New notes content
        
    Returns:
        bool: True if successful, False otherwise
    """
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        
        update_sql = """
        UPDATE file_lineage 
        SET notes = %s 
        WHERE id = %s AND revision = %s
        """
        
        cursor.execute(update_sql, (new_notes, record_id, revision))
        connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Successfully updated notes for record {record_id} revision {revision}")
            return True
        else:
            logger.warning(f"No record found to update: {record_id} revision {revision}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating notes for record {record_id}: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def edit_notes_interactive(identifier: str) -> bool:
    """
    Edit notes for a record interactively using the user's default text editor.
    
    Args:
        identifier: UUID or filename to edit notes for
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get records by identifier
        records = get_records_by_identifier(identifier)
        
        if not records:
            print(f"No records found for identifier: {identifier}")
            return False
        
        if len(records) > 1:
            print(f"Multiple records found for '{identifier}'. Please be more specific.")
            for record in records:
                print(f"  - {record['id']} (revision {record['revision']}): {record['original_filename']}")
            return False
        
        record = records[0]
        current_notes = record['notes'] or ""
        
        # Create temporary file with current notes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(current_notes)
            temp_file_path = temp_file.name
        
        try:
            # Open in default editor
            if os.name == 'nt':  # Windows
                os.startfile(temp_file_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open', temp_file_path], check=True)
            else:
                # Fallback to common editors
                for editor in ['nano', 'vim', 'vi']:
                    try:
                        subprocess.run([editor, temp_file_path], check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    print("No suitable text editor found. Please edit the file manually.")
                    print(f"File location: {temp_file_path}")
            
            # Wait for user to finish editing
            input("Press Enter when you're done editing the notes...")
            
            # Read the edited content
            with open(temp_file_path, 'r') as temp_file:
                new_notes = temp_file.read()
            
            # Update the record
            success = update_record_notes(record['id'], record['revision'], new_notes)
            
            if success:
                print("Notes updated successfully!")
                return True
            else:
                print("Failed to update notes.")
                return False
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
    except Exception as e:
        logger.error(f"Error editing notes for {identifier}: {e}")
        print(f"Error: {e}")
        return False


def find_and_create_updated_record(original_filename: str, new_archive_path: str) -> Optional[CalRecord]:
    """
    Find the latest revision for a filename and create a new updated record.
    
    Args:
        original_filename: The original filename to search for
        new_archive_path: The new archive path for the updated file
        
    Returns:
        CalRecord: The new updated record if successful, None if failed
    """
    connection = None
    try:
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Find the latest revision for this filename
        select_sql = """
        SELECT id, revision, original_filename, archive_path, tags, notes, timestamp
        FROM file_lineage 
        WHERE original_filename = %s 
        ORDER BY revision DESC 
        LIMIT 1
        """
        
        cursor.execute(select_sql, (original_filename,))
        result = cursor.fetchone()
        
        if not result:
            logger.warning(f"No existing record found for filename: {original_filename}")
            return None
        
        # Create a new CalRecord with incremented revision
        new_cal_record = CalRecord(
            id=result['id'],  # Use the same UUID
            revision=result['revision'] + 1,  # Increment revision
            original_filename=result['original_filename'],
            archive_path=new_archive_path,
            tags=result['tags'] or [],
            notes=result['notes']
        )
        
        # Insert the new revision record
        insert_sql = """
        INSERT INTO file_lineage (id, revision, original_filename, archive_path, tags, notes, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            str(new_cal_record.id),
            new_cal_record.revision,
            new_cal_record.original_filename,
            new_cal_record.archive_path,
            new_cal_record.tags,
            new_cal_record.notes,
            new_cal_record.timestamp
        ))
        
        connection.commit()
        logger.info(f"Successfully created updated CalRecord for file: {original_filename} (revision {new_cal_record.revision})")
        return new_cal_record
        
    except psycopg2.Error as e:
        logger.error(f"Database error updating CalRecord for {original_filename}: {e}")
        if connection:
            connection.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error updating CalRecord for {original_filename}: {e}")
        if connection:
            connection.rollback()
        return None
    finally:
        if connection:
            connection.close()
