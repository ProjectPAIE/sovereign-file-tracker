#!/usr/bin/env python3
"""
Sovereign File Tracker - File Watcher
Automation layer for monitoring _INGEST and _UPDATE folders and processing files.
"""

import os
import shutil
import logging
import time
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from logic import create_new_cal_record, find_and_create_updated_record
from config import INGEST_DIR, UPDATE_DIR, ARCHIVE_DIR, SYMLINK_DIR, CATEGORIES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sft_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SFTFileHandler(FileSystemEventHandler):
    """
    File system event handler for Sovereign File Tracker.
    Processes file creation events in _INGEST and _UPDATE folders.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize the file handler.
        
        Args:
            base_path: Optional base path. If not provided, uses settings from config.py
        """
        if base_path:
            self.base_path = Path(base_path)
            self.ingest_path = self.base_path / "_INGEST"
            self.update_path = self.base_path / "_UPDATE"
            self.archive_path = self.base_path / "SovereignArchive"
            self.symlink_path = self.base_path / "SFT_Symlink"
        else:
            # Use settings from config.py
            self.base_path = INGEST_DIR.parent
            self.ingest_path = INGEST_DIR
            self.update_path = UPDATE_DIR
            self.archive_path = ARCHIVE_DIR
            self.symlink_path = SYMLINK_DIR
        
        # Ensure all required directories exist
        self._ensure_directories()
        
        logger.info(f"Initialized SFT File Handler")
        logger.info(f"Base path: {self.base_path}")
        logger.info(f"Ingest path: {self.ingest_path}")
        logger.info(f"Update path: {self.update_path}")
        logger.info(f"Archive path: {self.archive_path}")
        logger.info(f"Symlink path: {self.symlink_path}")
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.ingest_path,
            self.update_path,
            self.archive_path,
            self.symlink_path
        ]
        
        # Create ingest subdirectories
        for subdir in CATEGORIES:
            directories.append(self.ingest_path / subdir)
            directories.append(self.archive_path / subdir)
            directories.append(self.symlink_path / subdir)
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def _get_file_category(self, file_path: Path) -> Optional[str]:
        """
        Determine the category of a file based on its location or extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Category string (AUDIO, BLOBS, IMAGES, TEXT) or None
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
    
    def _move_to_archive(self, source_path: Path, category: str) -> Optional[Path]:
        """
        Move a file to the appropriate archive directory.
        
        Args:
            source_path: Source file path
            category: File category (AUDIO, BLOBS, IMAGES, TEXT)
            
        Returns:
            New archive path if successful, None if failed
        """
        try:
            # Create a unique filename to avoid conflicts
            timestamp = int(time.time())
            filename = f"{timestamp}_{source_path.name}"
            archive_file_path = self.archive_path / category / filename
            
            # Move the file to archive
            shutil.move(str(source_path), str(archive_file_path))
            logger.info(f"Moved {source_path} to archive: {archive_file_path}")
            
            return archive_file_path
            
        except Exception as e:
            logger.error(f"Failed to move {source_path} to archive: {e}")
            return None
    
    def _create_symlink(self, archive_path: Path, file_uuid: str, category: str) -> bool:
        """
        Create a symbolic link in the SFT_Symlink directory.
        
        Args:
            archive_path: Path to the archived file
            file_uuid: UUID of the file for the symlink name
            category: File category
            
        Returns:
            True if successful, False otherwise
        """
        try:
            symlink_path = self.symlink_path / category / f"{file_uuid}{archive_path.suffix}"
            
            # Remove existing symlink if it exists
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
            
            # Create new symlink
            symlink_path.symlink_to(archive_path)
            logger.info(f"Created symlink: {symlink_path} -> {archive_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create symlink for UUID {file_uuid}: {e}")
            return False
    
    def _process_ingest_file(self, file_path: Path):
        """
        Process a new file in the _INGEST directory.
        
        Args:
            file_path: Path to the new file
        """
        try:
            logger.info(f"Processing new ingest file: {file_path}")
            
            # Determine file category
            category = self._get_file_category(file_path)
            logger.info(f"File category: {category}")
            
            # Move file to archive
            archive_path = self._move_to_archive(file_path, category)
            if not archive_path:
                logger.error(f"Failed to move file to archive: {file_path}")
                return
            
            # Create CalRecord
            cal_record = create_new_cal_record(file_path.name, str(archive_path))
            if not cal_record:
                logger.error(f"Failed to create CalRecord for: {file_path.name}")
                return
            
            # Create symlink using the UUID from the CalRecord
            if not self._create_symlink(archive_path, str(cal_record.id), category):
                logger.error(f"Failed to create symlink for: {file_path.name}")
                return
            
            logger.info(f"Successfully processed ingest file: {file_path.name}")
            
        except Exception as e:
            logger.error(f"Error processing ingest file {file_path}: {e}")
    
    def _process_update_file(self, file_path: Path):
        """
        Process a new file in the _UPDATE directory.
        
        Args:
            file_path: Path to the new file
        """
        try:
            logger.info(f"Processing update file: {file_path}")
            
            # Determine file category
            category = self._get_file_category(file_path)
            logger.info(f"File category: {category}")
            
            # Move file to archive
            archive_path = self._move_to_archive(file_path, category)
            if not archive_path:
                logger.error(f"Failed to move file to archive: {file_path}")
                return
            
            # Create updated CalRecord
            cal_record = find_and_create_updated_record(file_path.name, str(archive_path))
            if not cal_record:
                logger.error(f"Failed to create updated CalRecord for: {file_path.name}")
                return
            
            # Update symlink using the UUID from the updated CalRecord
            if not self._create_symlink(archive_path, str(cal_record.id), category):
                logger.error(f"Failed to update symlink for: {file_path.name}")
                return
            
            logger.info(f"Successfully processed update file: {file_path.name}")
            
        except Exception as e:
            logger.error(f"Error processing update file {file_path}: {e}")
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Ignore hidden files (files starting with a dot)
        if file_path.name.startswith('.'):
            logger.debug(f"Ignoring hidden file: {file_path}")
            return
        
        try:
            # Check if file is in _INGEST directory or its subdirectories
            if self.ingest_path in file_path.parents:
                self._process_ingest_file(file_path)
            
            # Check if file is in _UPDATE directory
            elif file_path.parent == self.update_path:
                self._process_update_file(file_path)
            
            else:
                logger.debug(f"Ignoring file creation outside monitored directories: {file_path}")
                
        except Exception as e:
            logger.error(f"Error handling file creation event for {file_path}: {e}")


class SFTWatcher:
    """
    Main watcher class for Sovereign File Tracker.
    Manages the file system observer and event handler.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize the SFT watcher.
        
        Args:
            base_path: Optional base path. If not provided, uses settings from config.py
        """
        self.base_path = Path(base_path) if base_path else INGEST_DIR.parent
        self.observer = Observer()
        self.handler = SFTFileHandler(base_path)
        
        logger.info(f"Initialized SFT Watcher for: {self.base_path}")
    
    def start(self):
        """Start watching the directories."""
        try:
            # Watch _INGEST directory and all subdirectories
            self.observer.schedule(
                self.handler,
                str(self.handler.ingest_path),
                recursive=True
            )
            
            # Watch _UPDATE directory
            self.observer.schedule(
                self.handler,
                str(self.handler.update_path),
                recursive=False
            )
            
            self.observer.start()
            logger.info("SFT Watcher started successfully")
            logger.info(f"Monitoring: {self.handler.ingest_path} (recursive)")
            logger.info(f"Monitoring: {self.handler.update_path}")
            
        except Exception as e:
            logger.error(f"Failed to start SFT Watcher: {e}")
            raise
    
    def stop(self):
        """Stop watching the directories."""
        try:
            self.observer.stop()
            self.observer.join()
            logger.info("SFT Watcher stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping SFT Watcher: {e}")
    
    def run(self):
        """Run the watcher in a loop."""
        try:
            self.start()
            
            logger.info("SFT Watcher is running. Press Ctrl+C to stop.")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error in SFT Watcher: {e}")
        finally:
            self.stop()


def main():
    """Main entry point for the SFT Watcher."""
    import sys
    
    # Get base path from command line argument or use config settings
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
        # Validate custom base path
        if not os.path.exists(base_path):
            logger.error(f"Base path does not exist: {base_path}")
            sys.exit(1)
    else:
        # Use config settings (no validation needed as config handles this)
        base_path = None
    
    # Create and run the watcher
    watcher = SFTWatcher(base_path)
    
    try:
        watcher.run()
    except Exception as e:
        logger.error(f"Fatal error in SFT Watcher: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
