"""
Init command module for the SFT CLI.
"""

import argparse
import os
from pathlib import Path
from commands.core import command, handle_command_error
from database import create_file_lineage_table, create_links_table


@command(name='init', description='Initialize the SFT system with folder structure and database tables')
@handle_command_error
def init_command(args: argparse.Namespace):
    """
    Handle the init command.

    Args:
        args: Parsed command line arguments
    """
    print("🚀 Initializing SFT (Sovereign File Tracker) System")
    print("=" * 60)
    
    try:
        # Step 1: Create folder structure
        print("\n📁 Creating SFT folder structure...")
        create_folder_structure()
        
        # Step 2: Set up database tables
        print("\n🗄️  Setting up database tables...")
        setup_database_tables()
        
        print("\n" + "=" * 60)
        print("✅ SFT system initialization completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Place files in the _INGEST folder to automatically track them")
        print("   2. Use 'sft ingest <filepath>' to manually ingest files")
        print("   3. Use 'sft --help' to see all available commands")
        print("\n🎉 Happy file tracking!")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        raise


def create_folder_structure():
    """Create the complete SFT folder structure."""
    folders = [
        "_INGEST/AUDIO",
        "_INGEST/BLOBS", 
        "_INGEST/IMAGES",
        "_INGEST/TEXT",
        "_UPDATE",
        "SovereignArchive/AUDIO",
        "SovereignArchive/BLOBS",
        "SovereignArchive/IMAGES", 
        "SovereignArchive/TEXT",
        "SFT_Symlink/AUDIO",
        "SFT_Symlink/BLOBS",
        "SFT_Symlink/IMAGES",
        "SFT_Symlink/TEXT"
    ]
    
    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {folder}")
        else:
            print(f"   ℹ️  Already exists: {folder}")


def setup_database_tables():
    """Set up the necessary database tables."""
    try:
        # Create file_lineage table
        print("   📊 Creating file_lineage table...")
        create_file_lineage_table()
        print("   ✅ file_lineage table created successfully")
        
        # Create sft_links table
        print("   🔗 Creating sft_links table...")
        create_links_table()
        print("   ✅ sft_links table created successfully")
        
    except Exception as e:
        print(f"   ❌ Database setup failed: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add init command arguments to the parser."""
    # No arguments needed for init command
    pass 