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


def get_records_by_identifier(identifier: str, limit: int = 25, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get records by identifier (UUID or filename) with pagination support.
    
    Args:
        identifier: UUID or filename to search for
        limit: Maximum number of records to return (default: 25)
        offset: Number of records to skip (default: 0)
        
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
            LIMIT %s OFFSET %s
            """
            cursor.execute(select_sql, (identifier, limit, offset))
        else:
            # Search by filename
            select_sql = """
            SELECT id, revision, original_filename, archive_path, tags, notes, timestamp
            FROM file_lineage 
            WHERE original_filename ILIKE %s 
            ORDER BY revision DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(select_sql, (f"%{identifier}%", limit, offset))
        
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


def get_links_by_source(identifier: str) -> List[Dict[str, Any]]:
    """
    Get all links where the given identifier's UUID is the source.
    
    Args:
        identifier: UUID or filename to find links for
        
    Returns:
        List of dictionaries containing link information and target file details
    """
    connection = None
    try:
        # First, get the UUID for the identifier
        source_records = get_records_by_identifier(identifier)
        
        if not source_records:
            logger.warning(f"No records found for identifier: {identifier}")
            return []
        
        if len(source_records) > 1:
            logger.warning(f"Multiple records found for identifier: {identifier}, using the latest revision")
        
        # Use the latest revision (first in the list)
        source_uuid = source_records[0]['id']
        
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Query the sft_links table to find all links where source_uuid is the source
        # Join with file_lineage to get target file details
        select_sql = """
        SELECT 
            l.source_uuid,
            l.target_uuid,
            l.notes as link_notes,
            l.tags as link_tags,
            fl.original_filename as target_filename,
            fl.revision as target_revision,
            fl.timestamp as target_timestamp,
            fl.notes as target_notes
        FROM sft_links l
        JOIN file_lineage fl ON l.target_uuid = fl.id
        WHERE l.source_uuid = %s
        ORDER BY fl.original_filename, fl.revision DESC
        """
        
        cursor.execute(select_sql, (str(source_uuid),))
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        links = []
        for result in results:
            links.append({
                'source_uuid': result['source_uuid'],
                'target_uuid': result['target_uuid'],
                'link_notes': result['link_notes'],
                'link_tags': result['link_tags'],
                'target_filename': result['target_filename'],
                'target_revision': result['target_revision'],
                'target_timestamp': result['target_timestamp'],
                'target_notes': result['target_notes']
            })
        
        logger.info(f"Found {len(links)} links for source identifier: {identifier}")
        return links
        
    except Exception as e:
        logger.error(f"Error getting links for identifier {identifier}: {e}")
        return []
    finally:
        if connection:
            connection.close()


def remove_link(source_identifier: str, target_identifier: str) -> bool:
    """
    Remove a link between two files from the sft_links table.
    
    Args:
        source_identifier: UUID or filename of the source file
        target_identifier: UUID or filename of the target file
        
    Returns:
        bool: True if link was removed successfully, False otherwise
    """
    connection = None
    try:
        # First, get the UUIDs for both identifiers
        source_records = get_records_by_identifier(source_identifier)
        
        if not source_records:
            logger.warning(f"No records found for source identifier: {source_identifier}")
            return False
        
        if len(source_records) > 1:
            logger.warning(f"Multiple records found for source identifier: {source_identifier}, using the latest revision")
        
        target_records = get_records_by_identifier(target_identifier)
        
        if not target_records:
            logger.warning(f"No records found for target identifier: {target_identifier}")
            return False
        
        if len(target_records) > 1:
            logger.warning(f"Multiple records found for target identifier: {target_identifier}, using the latest revision")
        
        # Use the latest revision for both (first in the list)
        source_uuid = source_records[0]['id']
        target_uuid = target_records[0]['id']
        
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Check if the link exists before trying to delete it
        check_sql = """
        SELECT source_uuid, target_uuid 
        FROM sft_links 
        WHERE source_uuid = %s AND target_uuid = %s
        """
        cursor.execute(check_sql, (str(source_uuid), str(target_uuid)))
        
        if not cursor.fetchone():
            logger.warning(f"Link does not exist between {source_identifier} and {target_identifier}")
            return False
        
        # Delete the link
        delete_sql = """
        DELETE FROM sft_links 
        WHERE source_uuid = %s AND target_uuid = %s
        """
        cursor.execute(delete_sql, (str(source_uuid), str(target_uuid)))
        connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Successfully removed link between {source_identifier} and {target_identifier}")
            return True
        else:
            logger.warning(f"No link was removed between {source_identifier} and {target_identifier}")
            return False
        
    except Exception as e:
        logger.error(f"Error removing link between {source_identifier} and {target_identifier}: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def add_tags_to_record(identifier: str, new_tags: list) -> bool:
    """
    Add tags to a file record, avoiding duplicates.
    
    Args:
        identifier: UUID or filename to find the record
        new_tags: List of tags to add
        
    Returns:
        bool: True if tags were added successfully, False otherwise
    """
    connection = None
    try:
        # First, get the record for the identifier
        records = get_records_by_identifier(identifier)
        
        if not records:
            logger.warning(f"No records found for identifier: {identifier}")
            return False
        
        if len(records) > 1:
            logger.warning(f"Multiple records found for identifier: {identifier}, using the latest revision")
        
        # Use the latest revision (first in the list)
        record = records[0]
        record_id = record['id']
        record_revision = record['revision']
        existing_tags = record['tags'] or []
        
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Combine existing tags with new tags, avoiding duplicates
        combined_tags = list(existing_tags)
        added_tags = []
        
        for tag in new_tags:
            if tag not in combined_tags:
                combined_tags.append(tag)
                added_tags.append(tag)
        
        if not added_tags:
            logger.info(f"No new tags to add for identifier: {identifier}")
            return True
        
        # Update the record with the new tags
        update_sql = """
        UPDATE file_lineage 
        SET tags = %s 
        WHERE id = %s AND revision = %s
        """
        
        cursor.execute(update_sql, (combined_tags, str(record_id), record_revision))
        connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Successfully added tags to record {identifier}: {added_tags}")
            return True
        else:
            logger.warning(f"No record was updated for identifier: {identifier}")
            return False
        
    except Exception as e:
        logger.error(f"Error adding tags to record {identifier}: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def remove_tags_from_record(identifier: str, tags_to_remove: list) -> bool:
    """
    Remove tags from a file record.
    
    Args:
        identifier: UUID or filename to find the record
        tags_to_remove: List of tags to remove
        
    Returns:
        bool: True if tags were removed successfully, False otherwise
    """
    connection = None
    try:
        # First, get the record for the identifier
        records = get_records_by_identifier(identifier)
        
        if not records:
            logger.warning(f"No records found for identifier: {identifier}")
            return False
        
        if len(records) > 1:
            logger.warning(f"Multiple records found for identifier: {identifier}, using the latest revision")
        
        # Use the latest revision (first in the list)
        record = records[0]
        record_id = record['id']
        record_revision = record['revision']
        existing_tags = record['tags'] or []
        
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Remove specified tags from existing tags
        updated_tags = list(existing_tags)
        removed_tags = []
        
        for tag in tags_to_remove:
            if tag in updated_tags:
                updated_tags.remove(tag)
                removed_tags.append(tag)
        
        if not removed_tags:
            logger.info(f"No tags to remove for identifier: {identifier}")
            return True
        
        # Update the record with the modified tags
        update_sql = """
        UPDATE file_lineage 
        SET tags = %s 
        WHERE id = %s AND revision = %s
        """
        
        cursor.execute(update_sql, (updated_tags, str(record_id), record_revision))
        connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Successfully removed tags from record {identifier}: {removed_tags}")
            return True
        else:
            logger.warning(f"No record was updated for identifier: {identifier}")
            return False
        
    except Exception as e:
        logger.error(f"Error removing tags from record {identifier}: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()


def get_all_records(limit: int = 25, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get the most recent file records from the file_lineage table with pagination support.
    
    Args:
        limit: Maximum number of records to return (default: 25)
        offset: Number of records to skip (default: 0)
        
    Returns:
        List of record dictionaries ordered by timestamp (most recent first)
    """
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Query the file_lineage table for the most recent records
        select_sql = """
        SELECT id, revision, original_filename, archive_path, tags, notes, timestamp
        FROM file_lineage 
        ORDER BY timestamp DESC 
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(select_sql, (limit, offset))
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
        
        logger.info(f"Retrieved {len(records)} recent records (limit: {limit}, offset: {offset})")
        return records
        
    except Exception as e:
        logger.error(f"Error getting recent records: {e}")
        return []
    finally:
        if connection:
            connection.close()


def get_file_paths_for_revisions(identifier: str, rev1: int, rev2: int) -> Dict[str, Any]:
    """
    Get the file paths for two specific revisions of the same file.
    
    Args:
        identifier: UUID or filename to find revisions for
        rev1: First revision number
        rev2: Second revision number
        
    Returns:
        Dictionary containing file paths and metadata for both revisions
    """
    try:
        # Get all records for this identifier
        all_records = get_records_by_identifier(identifier, limit=1000)  # Get all revisions
        if not all_records:
            return None
        
        # Find the specific revisions
        rev1_record = None
        rev2_record = None
        
        for record in all_records:
            if record['revision'] == rev1:
                rev1_record = record
            elif record['revision'] == rev2:
                rev2_record = record
        
        if not rev1_record:
            raise ValueError(f"Revision {rev1} not found for file: {identifier}")
        if not rev2_record:
            raise ValueError(f"Revision {rev2} not found for file: {identifier}")
        
        # Verify both revisions belong to the same file (same UUID)
        if rev1_record['id'] != rev2_record['id']:
            raise ValueError(f"Revisions {rev1} and {rev2} belong to different files")
        
        # Construct full file paths
        archive_base = Path("SovereignArchive")
        rev1_path = archive_base / rev1_record['archive_path']
        rev2_path = archive_base / rev2_record['archive_path']
        
        return {
            'file_uuid': str(rev1_record['id']),
            'original_filename': rev1_record['original_filename'],
            'rev1': {
                'revision': rev1,
                'path': str(rev1_path),
                'timestamp': rev1_record['timestamp'],
                'notes': rev1_record['notes']
            },
            'rev2': {
                'revision': rev2,
                'path': str(rev2_path),
                'timestamp': rev2_record['timestamp'],
                'notes': rev2_record['notes']
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting file paths for revisions {rev1} and {rev2} of {identifier}: {e}")
        raise


def create_link_with_notes(source_identifier: str, target_identifier: str, notes: str = None) -> bool:
    """
    Create a link between two files with optional notes.
    
    Args:
        source_identifier: UUID or filename of the source file
        target_identifier: UUID or filename of the target file
        notes: Optional notes for the link
        
    Returns:
        bool: True if successful, False otherwise
    """
    connection = None
    try:
        # Get source records
        source_records = get_records_by_identifier(source_identifier)
        if not source_records:
            raise ValueError(f"Source file not found: {source_identifier}")
        if len(source_records) > 1:
            raise ValueError(f"Multiple source files found for '{source_identifier}'. Please use a more specific identifier.")
        
        # Get target records
        target_records = get_records_by_identifier(target_identifier)
        if not target_records:
            raise ValueError(f"Target file not found: {target_identifier}")
        if len(target_records) > 1:
            raise ValueError(f"Multiple target files found for '{target_identifier}'. Please use a more specific identifier.")
        
        source_uuid = source_records[0]['id']
        target_uuid = target_records[0]['id']
        source_filename = source_records[0]['original_filename']
        target_filename = target_records[0]['original_filename']
        
        # Prevent self-linking
        if source_uuid == target_uuid:
            raise ValueError(f"Cannot link a file to itself: '{source_filename}'")
        
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Check if link already exists
        check_sql = "SELECT source_uuid, target_uuid FROM sft_links WHERE source_uuid = %s AND target_uuid = %s"
        cursor.execute(check_sql, (str(source_uuid), str(target_uuid)))
        if cursor.fetchone():
            raise ValueError(f"Link already exists between '{source_filename}' and '{target_filename}'")
        
        # Create the link with notes
        insert_sql = "INSERT INTO sft_links (source_uuid, target_uuid, notes) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (str(source_uuid), str(target_uuid), notes))
        connection.commit()
        
        logger.info(f"Successfully created link with notes from {source_filename} to {target_filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating link with notes from {source_identifier} to {target_identifier}: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


def update_link_notes(source_identifier: str, target_identifier: str, notes: str) -> bool:
    """
    Update the notes for an existing link.
    
    Args:
        source_identifier: UUID or filename of the source file
        target_identifier: UUID or filename of the target file
        notes: New notes for the link
        
    Returns:
        bool: True if successful, False otherwise
    """
    connection = None
    try:
        # Get source records
        source_records = get_records_by_identifier(source_identifier)
        if not source_records:
            raise ValueError(f"Source file not found: {source_identifier}")
        if len(source_records) > 1:
            raise ValueError(f"Multiple source files found for '{source_identifier}'. Please use a more specific identifier.")
        
        # Get target records
        target_records = get_records_by_identifier(target_identifier)
        if not target_records:
            raise ValueError(f"Target file not found: {target_identifier}")
        if len(target_records) > 1:
            raise ValueError(f"Multiple target files found for '{target_identifier}'. Please use a more specific identifier.")
        
        source_uuid = source_records[0]['id']
        target_uuid = target_records[0]['id']
        
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Update the link notes
        update_sql = "UPDATE sft_links SET notes = %s WHERE source_uuid = %s AND target_uuid = %s"
        cursor.execute(update_sql, (notes, str(source_uuid), str(target_uuid)))
        connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Successfully updated notes for link from {source_identifier} to {target_identifier}")
            return True
        else:
            raise ValueError(f"Link not found between {source_identifier} and {target_identifier}")
        
    except Exception as e:
        logger.error(f"Error updating link notes from {source_identifier} to {target_identifier}: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


def edit_link_notes_interactive(source_identifier: str, target_identifier: str) -> bool:
    """
    Edit notes for a link interactively using the user's default text editor.
    
    Args:
        source_identifier: UUID or filename of the source file
        target_identifier: UUID or filename of the target file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get source records
        source_records = get_records_by_identifier(source_identifier)
        if not source_records:
            print(f"Source file not found: {source_identifier}")
            return False
        if len(source_records) > 1:
            print(f"Multiple source files found for '{source_identifier}'. Please use a more specific identifier.")
            for record in source_records:
                print(f"  - {record['id']} (revision {record['revision']}): {record['original_filename']}")
            return False
        
        # Get target records
        target_records = get_records_by_identifier(target_identifier)
        if not target_records:
            print(f"Target file not found: {target_identifier}")
            return False
        if len(target_records) > 1:
            print(f"Multiple target files found for '{target_identifier}'. Please use a more specific identifier.")
            for record in target_records:
                print(f"  - {record['id']} (revision {record['revision']}): {record['original_filename']}")
            return False
        
        source_uuid = source_records[0]['id']
        target_uuid = target_records[0]['id']
        source_filename = source_records[0]['original_filename']
        target_filename = target_records[0]['original_filename']
        
        # Get current link notes if they exist
        connection = None
        current_notes = ""
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            
            select_sql = "SELECT notes FROM sft_links WHERE source_uuid = %s AND target_uuid = %s"
            cursor.execute(select_sql, (str(source_uuid), str(target_uuid)))
            result = cursor.fetchone()
            
            if result:
                current_notes = result['notes'] or ""
            else:
                print(f"Link not found between {source_filename} and {target_filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting current link notes: {e}")
            print(f"Error: {e}")
            return False
        finally:
            if connection:
                connection.close()
        
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
            input("Press Enter when you're done editing the link notes...")
            
            # Read the edited content
            with open(temp_file_path, 'r') as temp_file:
                new_notes = temp_file.read()
            
            # Update the link notes
            success = update_link_notes(source_identifier, target_identifier, new_notes)
            
            if success:
                print("Link notes updated successfully!")
                return True
            else:
                print("Failed to update link notes.")
                return False
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
    except Exception as e:
        logger.error(f"Error editing link notes from {source_identifier} to {target_identifier}: {e}")
        print(f"Error: {e}")
        return False


def get_archive_stats() -> Dict[str, Any]:
    """
    Get comprehensive statistics about the SFT archive.
    
    Returns:
        Dictionary containing various archive statistics
    """
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        
        stats = {}
        
        # Get total number of unique files (UUIDs)
        unique_files_sql = "SELECT COUNT(DISTINCT id) as unique_files FROM file_lineage"
        cursor.execute(unique_files_sql)
        result = cursor.fetchone()
        stats['unique_files'] = result['unique_files'] if result else 0
        
        # Get total number of revisions
        total_revisions_sql = "SELECT COUNT(*) as total_revisions FROM file_lineage"
        cursor.execute(total_revisions_sql)
        result = cursor.fetchone()
        stats['total_revisions'] = result['total_revisions'] if result else 0
        
        # Get total number of links
        total_links_sql = "SELECT COUNT(*) as total_links FROM sft_links"
        cursor.execute(total_links_sql)
        result = cursor.fetchone()
        stats['total_links'] = result['total_links'] if result else 0
        
        # Get files by category (based on archive_path)
        category_sql = """
        SELECT 
            CASE 
                WHEN archive_path LIKE '%/TEXT/%' THEN 'TEXT'
                WHEN archive_path LIKE '%/IMAGES/%' THEN 'IMAGES'
                WHEN archive_path LIKE '%/AUDIO/%' THEN 'AUDIO'
                WHEN archive_path LIKE '%/BLOBS/%' THEN 'BLOBS'
                ELSE 'UNKNOWN'
            END as category,
            COUNT(DISTINCT id) as file_count
        FROM file_lineage 
        GROUP BY category
        ORDER BY file_count DESC
        """
        cursor.execute(category_sql)
        category_results = cursor.fetchall()
        stats['files_by_category'] = {row['category']: row['file_count'] for row in category_results}
        
        # Get files by tags (top tags)
        tags_sql = """
        SELECT 
            unnest(tags) as tag,
            COUNT(DISTINCT id) as file_count
        FROM file_lineage 
        WHERE tags IS NOT NULL AND array_length(tags, 1) > 0
        GROUP BY tag
        ORDER BY file_count DESC
        LIMIT 10
        """
        cursor.execute(tags_sql)
        tags_results = cursor.fetchall()
        stats['top_tags'] = {row['tag']: row['file_count'] for row in tags_results}
        
        # Get files with most revisions
        most_revisions_sql = """
        SELECT 
            original_filename,
            COUNT(*) as revision_count
        FROM file_lineage 
        GROUP BY id, original_filename
        ORDER BY revision_count DESC
        LIMIT 5
        """
        cursor.execute(most_revisions_sql)
        revision_results = cursor.fetchall()
        stats['files_with_most_revisions'] = [
            {'filename': row['original_filename'], 'revisions': row['revision_count']} 
            for row in revision_results
        ]
        
        # Get recent activity (files added in last 7 days)
        recent_activity_sql = """
        SELECT COUNT(DISTINCT id) as recent_files
        FROM file_lineage 
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        """
        cursor.execute(recent_activity_sql)
        result = cursor.fetchone()
        stats['recent_files'] = result['recent_files'] if result else 0
        
        # Get files with notes
        files_with_notes_sql = """
        SELECT COUNT(DISTINCT id) as files_with_notes
        FROM file_lineage 
        WHERE notes IS NOT NULL AND notes != ''
        """
        cursor.execute(files_with_notes_sql)
        result = cursor.fetchone()
        stats['files_with_notes'] = result['files_with_notes'] if result else 0
        
        # Get links with notes
        links_with_notes_sql = """
        SELECT COUNT(*) as links_with_notes
        FROM sft_links 
        WHERE notes IS NOT NULL AND notes != ''
        """
        cursor.execute(links_with_notes_sql)
        result = cursor.fetchone()
        stats['links_with_notes'] = result['links_with_notes'] if result else 0
        
        logger.info(f"Successfully retrieved archive statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting archive statistics: {e}")
        raise
    finally:
        if connection:
            connection.close()


def trace_path_between_files(start_identifier: str, end_identifier: str) -> List[Dict[str, Any]]:
    """
    Find a path between two files using recursive SQL queries on the sft_links table.
    
    Args:
        start_identifier: UUID or filename of the starting file
        end_identifier: UUID or filename of the ending file
        
    Returns:
        List of dictionaries containing file and link information along the path
    """
    connection = None
    try:
        # First, resolve the identifiers to UUIDs
        start_records = get_records_by_identifier(start_identifier)
        if not start_records:
            raise ValueError(f"Start file not found: {start_identifier}")
        if len(start_records) > 1:
            raise ValueError(f"Multiple start files found for '{start_identifier}'. Please use a more specific identifier.")
        
        end_records = get_records_by_identifier(end_identifier)
        if not end_records:
            raise ValueError(f"End file not found: {end_identifier}")
        if len(end_records) > 1:
            raise ValueError(f"Multiple end files found for '{end_identifier}'. Please use a more specific identifier.")
        
        start_uuid = str(start_records[0]['id'])
        end_uuid = str(end_records[0]['id'])
        
        # Check if start and end are the same
        if start_uuid == end_uuid:
            raise ValueError("Start and end files are the same. No path needed.")
        
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Use recursive CTE to find the path
        recursive_sql = """
        WITH RECURSIVE path_search AS (
            -- Base case: start with the source file
            SELECT 
                source_uuid,
                target_uuid,
                notes as link_notes,
                1 as depth,
                ARRAY[source_uuid, target_uuid] as path,
                ARRAY[notes] as link_notes_path
            FROM sft_links 
            WHERE source_uuid = %s
            
            UNION ALL
            
            -- Recursive case: continue the path
            SELECT 
                l.source_uuid,
                l.target_uuid,
                l.notes as link_notes,
                ps.depth + 1,
                ps.path || l.target_uuid,
                ps.link_notes_path || l.notes
            FROM sft_links l
            INNER JOIN path_search ps ON l.source_uuid = ps.target_uuid
            WHERE l.target_uuid != ALL(ps.path)  -- Avoid cycles
            AND ps.depth < 10  -- Limit depth to prevent infinite recursion
        )
        SELECT 
            ps.source_uuid,
            ps.target_uuid,
            ps.link_notes,
            ps.depth,
            ps.path,
            ps.link_notes_path
        FROM path_search ps
        WHERE ps.target_uuid = %s
        ORDER BY ps.depth ASC
        LIMIT 1;
        """
        
        cursor.execute(recursive_sql, (start_uuid, end_uuid))
        path_result = cursor.fetchone()
        
        if not path_result:
            raise ValueError(f"No path found between '{start_identifier}' and '{end_identifier}'")
        
        # Extract the path and link notes
        path_uuids = path_result['path']
        link_notes_path = path_result['link_notes_path']
        
        # Convert PostgreSQL array to Python list if needed
        if isinstance(path_uuids, str):
            # Remove curly braces and split by comma
            path_uuids = path_uuids.strip('{}').split(',')
        if isinstance(link_notes_path, str):
            # Remove curly braces and split by comma, but handle NULL values
            link_notes_path = link_notes_path.strip('{}').split(',')
            # Convert 'NULL' strings to None
            link_notes_path = [None if note == 'NULL' else note for note in link_notes_path]
        
        # Get file information for each UUID in the path
        path_info = []
        for i, uuid in enumerate(path_uuids):
            # Clean up UUID if it has quotes
            uuid = uuid.strip().strip('"')
            
            # Get the latest revision for this file
            file_sql = """
            SELECT 
                id,
                original_filename,
                archive_path,
                timestamp,
                notes,
                tags,
                revision
            FROM file_lineage 
            WHERE id = %s
            ORDER BY revision DESC
            LIMIT 1
            """
            cursor.execute(file_sql, (uuid,))
            file_result = cursor.fetchone()
            
            if not file_result:
                logger.warning(f"File with UUID {uuid} not found in file_lineage")
                continue
            
            # Get link notes if this is not the first file (i > 0)
            link_notes = None
            if i > 0 and i <= len(link_notes_path):
                link_notes = link_notes_path[i - 1]
            
            path_info.append({
                'uuid': str(file_result['id']),
                'filename': file_result['original_filename'],
                'archive_path': file_result['archive_path'],
                'timestamp': file_result['timestamp'],
                'notes': file_result['notes'],
                'tags': file_result['tags'],
                'revision': file_result['revision'],
                'link_notes': link_notes,
                'step': i + 1
            })
        
        logger.info(f"Successfully traced path from {start_identifier} to {end_identifier} with {len(path_info)} steps")
        return path_info
        
    except Exception as e:
        logger.error(f"Error tracing path from {start_identifier} to {end_identifier}: {e}")
        raise
    finally:
        if connection:
            connection.close()


def get_backlinks_by_target(identifier: str) -> List[Dict[str, Any]]:
    """
    Get all files that link to a specified target file.
    
    Args:
        identifier: UUID or filename of the target file
        
    Returns:
        List of dictionaries containing source file information and link details
    """
    connection = None
    try:
        # First, resolve the identifier to a UUID
        target_records = get_records_by_identifier(identifier)
        if not target_records:
            raise ValueError(f"Target file not found: {identifier}")
        if len(target_records) > 1:
            raise ValueError(f"Multiple target files found for '{identifier}'. Please use a more specific identifier.")
        
        target_uuid = str(target_records[0]['id'])
        target_filename = target_records[0]['original_filename']
        
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Query to find all source files that link to the target
        backlinks_sql = """
        SELECT 
            l.source_uuid,
            l.notes as link_notes,
            l.tags as link_tags,
            f.original_filename,
            f.archive_path,
            f.timestamp,
            f.notes,
            f.tags,
            f.revision
        FROM sft_links l
        INNER JOIN file_lineage f ON l.source_uuid = f.id
        WHERE l.target_uuid = %s
        AND f.revision = (
            SELECT MAX(revision) 
            FROM file_lineage 
            WHERE id = l.source_uuid
        )
        ORDER BY f.timestamp DESC
        """
        
        cursor.execute(backlinks_sql, (target_uuid,))
        backlinks_results = cursor.fetchall()
        
        backlinks = []
        for row in backlinks_results:
            backlinks.append({
                'source_uuid': str(row['source_uuid']),
                'source_filename': row['original_filename'],
                'archive_path': row['archive_path'],
                'timestamp': row['timestamp'],
                'source_notes': row['notes'],
                'tags': row['tags'],
                'revision': row['revision'],
                'link_notes': row['link_notes'],
                'link_tags': row['link_tags']
            })
        
        logger.info(f"Found {len(backlinks)} backlinks for target identifier: {identifier}")
        return backlinks
        
    except Exception as e:
        logger.error(f"Error getting backlinks for {identifier}: {e}")
        raise
    finally:
        if connection:
            connection.close()


def add_tags_to_link(source_identifier: str, target_identifier: str, new_tags: list) -> bool:
    """
    Add tags to a specific link between two files.
    
    Args:
        source_identifier: UUID or filename of the source file
        target_identifier: UUID or filename of the target file
        new_tags: List of tags to add to the link
        
    Returns:
        bool: True if tags were added successfully, False otherwise
    """
    connection = None
    try:
        # First, resolve the identifiers to UUIDs
        source_records = get_records_by_identifier(source_identifier)
        if not source_records:
            raise ValueError(f"Source file not found: {source_identifier}")
        if len(source_records) > 1:
            raise ValueError(f"Multiple source files found for '{source_identifier}'. Please use a more specific identifier.")
        
        target_records = get_records_by_identifier(target_identifier)
        if not target_records:
            raise ValueError(f"Target file not found: {target_identifier}")
        if len(target_records) > 1:
            raise ValueError(f"Multiple target files found for '{target_identifier}'. Please use a more specific identifier.")
        
        source_uuid = str(source_records[0]['id'])
        target_uuid = str(target_records[0]['id'])
        source_filename = source_records[0]['original_filename']
        target_filename = target_records[0]['original_filename']
        
        # Check if start and end are the same
        if source_uuid == target_uuid:
            raise ValueError("Cannot add tags to a self-link. Source and target files are the same.")
        
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # First, check if the link exists and get current tags
        select_sql = """
        SELECT tags FROM sft_links 
        WHERE source_uuid = %s AND target_uuid = %s
        """
        
        cursor.execute(select_sql, (source_uuid, target_uuid))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError(f"Link not found between '{source_filename}' and '{target_filename}'")
        
        # Get current tags (handle NULL case)
        current_tags = result['tags'] or []
        
        # Add new tags, avoiding duplicates
        updated_tags = current_tags.copy()
        for tag in new_tags:
            if tag not in updated_tags:
                updated_tags.append(tag)
        
        # Check if any new tags were actually added
        if len(updated_tags) == len(current_tags):
            logger.info(f"No new tags to add for link from {source_filename} to {target_filename}")
            return True  # No new tags, but not an error
        
        # Update the link with new tags
        update_sql = """
        UPDATE sft_links 
        SET tags = %s 
        WHERE source_uuid = %s AND target_uuid = %s
        """
        
        cursor.execute(update_sql, (updated_tags, source_uuid, target_uuid))
        connection.commit()
        
        # Calculate how many new tags were added
        new_tags_added = len(updated_tags) - len(current_tags)
        
        logger.info(f"Successfully added {new_tags_added} tags to link from {source_filename} to {target_filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding tags to link from {source_identifier} to {target_identifier}: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


def remove_tags_from_link(source_identifier: str, target_identifier: str, tags_to_remove: list) -> bool:
    """
    Remove tags from a specific link between two files.

    Args:
        source_identifier: UUID or filename of the source file
        target_identifier: UUID or filename of the target file
        tags_to_remove: List of tags to remove from the link

    Returns:
        bool: True if tags were removed successfully, False otherwise
    """
    connection = None
    try:
        # First, resolve the identifiers to UUIDs
        source_records = get_records_by_identifier(source_identifier)
        if not source_records:
            raise ValueError(f"Source file not found: {source_identifier}")
        if len(source_records) > 1:
            raise ValueError(f"Multiple source files found for '{source_identifier}'. Please use a more specific identifier.")

        target_records = get_records_by_identifier(target_identifier)
        if not target_records:
            raise ValueError(f"Target file not found: {target_identifier}")
        if len(target_records) > 1:
            raise ValueError(f"Multiple target files found for '{target_identifier}'. Please use a more specific identifier.")

        source_uuid = str(source_records[0]['id'])
        target_uuid = str(target_records[0]['id'])
        source_filename = source_records[0]['original_filename']
        target_filename = target_records[0]['original_filename']

        # Check if start and end are the same
        if source_uuid == target_uuid:
            raise ValueError("Cannot remove tags from a self-link. Source and target files are the same.")

        connection = get_database_connection()
        cursor = connection.cursor()

        # First, check if the link exists and get current tags
        select_sql = """
        SELECT tags FROM sft_links
        WHERE source_uuid = %s AND target_uuid = %s
        """

        cursor.execute(select_sql, (source_uuid, target_uuid))
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Link not found between '{source_filename}' and '{target_filename}'")

        # Get current tags (handle NULL case)
        current_tags = result['tags'] or []

        # Remove specified tags
        updated_tags = [tag for tag in current_tags if tag not in tags_to_remove]

        # Check if any tags were actually removed
        if len(updated_tags) == len(current_tags):
            logger.info(f"No tags to remove for link from {source_filename} to {target_filename}")
            return True  # No tags removed, but not an error

        # Update the link with remaining tags
        update_sql = """
        UPDATE sft_links
        SET tags = %s
        WHERE source_uuid = %s AND target_uuid = %s
        """

        cursor.execute(update_sql, (updated_tags, source_uuid, target_uuid))
        connection.commit()

        # Calculate how many tags were removed
        tags_removed = len(current_tags) - len(updated_tags)

        logger.info(f"Successfully removed {tags_removed} tags from link from {source_filename} to {target_filename}")
        return True

    except Exception as e:
        logger.error(f"Error removing tags from link from {source_identifier} to {target_identifier}: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


def soft_delete_record(identifier: str) -> bool:
    """
    Soft delete a file record by adding a 'status:deleted' tag and moving files to _TRASH.

    Args:
        identifier: UUID or filename of the file to soft delete

    Returns:
        bool: True if soft delete was successful, False otherwise
    """
    connection = None
    try:
        # First, resolve the identifier to a UUID
        records = get_records_by_identifier(identifier)
        if not records:
            raise ValueError(f"File not found: {identifier}")
        if len(records) > 1:
            raise ValueError(f"Multiple files found for '{identifier}'. Please use a more specific identifier.")

        # Get the latest revision
        latest_record = records[0]
        file_uuid = str(latest_record['id'])
        filename = latest_record['original_filename']
        current_tags = latest_record['tags'] or []

        # Check if already deleted
        if 'status:deleted' in current_tags:
            raise ValueError(f"File '{filename}' is already marked as deleted")

        connection = get_database_connection()
        cursor = connection.cursor()

        # Add the 'status:deleted' tag
        updated_tags = current_tags.copy()
        if 'status:deleted' not in updated_tags:
            updated_tags.append('status:deleted')

        # Update the record with the new tag
        update_sql = """
        UPDATE file_lineage
        SET tags = %s
        WHERE id = %s AND revision = %s
        """

        cursor.execute(update_sql, (updated_tags, file_uuid, latest_record['revision']))
        connection.commit()

        # Move physical files to _TRASH
        move_files_to_trash(file_uuid, filename)

        logger.info(f"Successfully soft deleted file: {filename} (UUID: {file_uuid})")
        return True

    except Exception as e:
        logger.error(f"Error soft deleting file {identifier}: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


def move_files_to_trash(file_uuid: str, filename: str):
    """
    Move all physical files associated with a UUID from SovereignArchive to _TRASH.

    Args:
        file_uuid: UUID of the file to move
        filename: Original filename for logging purposes
    """
    try:
        # Create _TRASH directory if it doesn't exist
        trash_dir = Path("_TRASH")
        trash_dir.mkdir(exist_ok=True)

        # Get all records for this UUID to find all physical files
        connection = get_database_connection()
        cursor = connection.cursor()

        select_sql = """
        SELECT archive_path FROM file_lineage
        WHERE id = %s
        ORDER BY revision
        """

        cursor.execute(select_sql, (file_uuid,))
        records = cursor.fetchall()

        moved_files = []
        for record in records:
            archive_path = record['archive_path']
            if archive_path and Path(archive_path).exists():
                # Create destination path in _TRASH
                source_path = Path(archive_path)
                dest_path = trash_dir / source_path.name

                # Handle filename conflicts by adding a number suffix
                counter = 1
                original_dest = dest_path
                while dest_path.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_path = trash_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                # Move the file
                shutil.move(str(source_path), str(dest_path))
                moved_files.append(str(dest_path))

        connection.close()

        if moved_files:
            logger.info(f"Moved {len(moved_files)} file(s) to _TRASH for {filename}")
        else:
            logger.warning(f"No physical files found to move to _TRASH for {filename}")

    except Exception as e:
        logger.error(f"Error moving files to trash for {filename}: {e}")
        raise


def audit_archive(fix_issues: bool = False) -> Dict[str, Any]:
    """
    Audit the archive by checking symbolic links in SFT_Symlink directory.

    Args:
        fix_issues: If True, attempt to fix broken or incorrect symbolic links

    Returns:
        Dictionary containing audit summary and details
    """
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Get the latest revision of every file
        select_sql = """
        SELECT DISTINCT ON (id) 
            id, original_filename, archive_path, revision
        FROM file_lineage
        ORDER BY id, revision DESC
        """

        cursor.execute(select_sql)
        records = cursor.fetchall()

        audit_results = {
            'total_files': len(records),
            'valid_links': 0,
            'broken_links': 0,
            'missing_links': 0,
            'incorrect_links': 0,
            'fixed_links': 0,
            'failed_fixes': 0,
            'broken_details': [],
            'missing_details': [],
            'incorrect_details': [],
            'fixed_details': [],
            'failed_details': []
        }

        symlink_dir = Path("SFT_Symlink")
        if not symlink_dir.exists():
            logger.warning("SFT_Symlink directory does not exist")
            audit_results['missing_links'] = len(records)
            audit_results['missing_details'] = [f"Directory SFT_Symlink does not exist" for _ in records]
            return audit_results

        for record in records:
            file_uuid = str(record['id'])
            filename = record['original_filename']
            archive_path = record['archive_path']
            revision = record['revision']

            # Determine the expected symlink path
            category = _get_file_category(Path(archive_path)) if archive_path else "UNKNOWN"
            symlink_path = symlink_dir / category / file_uuid

            # Check if symlink exists
            if not symlink_path.exists():
                audit_results['missing_links'] += 1
                audit_results['missing_details'].append({
                    'uuid': file_uuid,
                    'filename': filename,
                    'expected_path': str(symlink_path),
                    'archive_path': archive_path
                })

                if fix_issues:
                    if _create_symlink(symlink_path, archive_path, filename):
                        audit_results['fixed_links'] += 1
                        audit_results['fixed_details'].append({
                            'uuid': file_uuid,
                            'filename': filename,
                            'symlink_path': str(symlink_path),
                            'target_path': archive_path
                        })
                    else:
                        audit_results['failed_fixes'] += 1
                        audit_results['failed_details'].append({
                            'uuid': file_uuid,
                            'filename': filename,
                            'symlink_path': str(symlink_path),
                            'target_path': archive_path
                        })

            elif symlink_path.is_symlink():
                # Check if symlink points to the correct target
                try:
                    target_path = symlink_path.resolve()
                    expected_target = Path(archive_path).resolve() if archive_path else None

                    if not expected_target or not target_path.samefile(expected_target):
                        audit_results['incorrect_links'] += 1
                        audit_results['incorrect_details'].append({
                            'uuid': file_uuid,
                            'filename': filename,
                            'symlink_path': str(symlink_path),
                            'current_target': str(target_path),
                            'expected_target': str(expected_target) if expected_target else 'None'
                        })

                        if fix_issues:
                            if _create_symlink(symlink_path, archive_path, filename):
                                audit_results['fixed_links'] += 1
                                audit_results['fixed_details'].append({
                                    'uuid': file_uuid,
                                    'filename': filename,
                                    'symlink_path': str(symlink_path),
                                    'target_path': archive_path
                                })
                            else:
                                audit_results['failed_fixes'] += 1
                                audit_results['failed_details'].append({
                                    'uuid': file_uuid,
                                    'filename': filename,
                                    'symlink_path': str(symlink_path),
                                    'target_path': archive_path
                                })
                    else:
                        audit_results['valid_links'] += 1

                except (OSError, RuntimeError) as e:
                    # Symlink is broken (target doesn't exist)
                    audit_results['broken_links'] += 1
                    audit_results['broken_details'].append({
                        'uuid': file_uuid,
                        'filename': filename,
                        'symlink_path': str(symlink_path),
                        'error': str(e)
                    })

                    if fix_issues:
                        if _create_symlink(symlink_path, archive_path, filename):
                            audit_results['fixed_links'] += 1
                            audit_results['fixed_details'].append({
                                'uuid': file_uuid,
                                'filename': filename,
                                'symlink_path': str(symlink_path),
                                'target_path': archive_path
                            })
                        else:
                            audit_results['failed_fixes'] += 1
                            audit_results['failed_details'].append({
                                'uuid': file_uuid,
                                'filename': filename,
                                'symlink_path': str(symlink_path),
                                'target_path': archive_path
                            })

            else:
                # Path exists but is not a symlink
                audit_results['incorrect_links'] += 1
                audit_results['incorrect_details'].append({
                    'uuid': file_uuid,
                    'filename': filename,
                    'symlink_path': str(symlink_path),
                    'error': 'Path exists but is not a symbolic link'
                })

                if fix_issues:
                    if _create_symlink(symlink_path, archive_path, filename):
                        audit_results['fixed_links'] += 1
                        audit_results['fixed_details'].append({
                            'uuid': file_uuid,
                            'filename': filename,
                            'symlink_path': str(symlink_path),
                            'target_path': archive_path
                        })
                    else:
                        audit_results['failed_fixes'] += 1
                        audit_results['failed_details'].append({
                            'uuid': file_uuid,
                            'filename': filename,
                            'symlink_path': str(symlink_path),
                            'target_path': archive_path
                        })

        logger.info(f"Archive audit completed: {audit_results['total_files']} files checked")
        return audit_results

    except Exception as e:
        logger.error(f"Error during archive audit: {e}")
        raise
    finally:
        if connection:
            connection.close()


def _create_symlink(symlink_path: Path, target_path: str, filename: str) -> bool:
    """
    Create a symbolic link from symlink_path to target_path.

    Args:
        symlink_path: Path where the symlink should be created
        target_path: Path that the symlink should point to
        filename: Original filename for logging purposes

    Returns:
        bool: True if symlink was created successfully, False otherwise
    """
    try:
        # Ensure the target file exists
        if not target_path or not Path(target_path).exists():
            logger.warning(f"Target file does not exist for {filename}: {target_path}")
            return False

        # Ensure the parent directory exists
        symlink_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing file/symlink if it exists
        if symlink_path.exists():
            if symlink_path.is_symlink():
                symlink_path.unlink()
            else:
                symlink_path.unlink()

        # Create the symbolic link
        symlink_path.symlink_to(Path(target_path).resolve())
        logger.info(f"Created symlink for {filename}: {symlink_path} -> {target_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating symlink for {filename}: {e}")
        return False
