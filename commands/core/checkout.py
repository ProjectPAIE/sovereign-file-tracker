"""
Checkout command module for the SFT CLI.
"""

import argparse
import shutil
import os
from pathlib import Path
from commands.core import get_records_by_identifier


def checkout_command(args: argparse.Namespace):
    """
    Handle the checkout command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    
    # Validate identifier argument
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"📦 Checking out file: '{identifier}'")
    
    # Find the latest revision of the file using get_records_by_identifier from logic.py
    records = get_records_by_identifier(identifier)
    
    # If the file is found, copy it to the Desktop
    if not records:
        print(f"❌ File not found: '{identifier}'")
        print("   Try searching with a different identifier or check the spelling.")
        raise Exception(f"File not found: {identifier}")
    
    # Get the latest revision (first in the list since it's ordered by revision DESC)
    record = records[0]
    
    # Get the source file path from the archive
    source_path = Path(record['archive_path'])
    
    if not source_path.exists():
        print(f"❌ Archive file not found: {source_path}")
        print("   The file may have been moved or deleted from the archive.")
        raise Exception(f"Archive file not found: {source_path}")
    
    # Get the Desktop path
    desktop_path = Path.home() / "Desktop"
    if not desktop_path.exists():
        print(f"❌ Desktop directory not found: {desktop_path}")
        raise Exception(f"Desktop directory not found: {desktop_path}")
    
    # Create the barcode filename format: original_filename._._.<uuid>.-.-.file_extension
    original_filename = record['original_filename']
    uuid_str = str(record['id'])
    
    # Split the original filename into name and extension
    if '.' in original_filename:
        name_part, extension = original_filename.rsplit('.', 1)
        barcode_filename = f"{name_part}._._.{uuid_str}.-.-.{extension}"
    else:
        # No extension case
        barcode_filename = f"{original_filename}._._.{uuid_str}"
    
    # Create the destination path
    destination_path = desktop_path / barcode_filename
    
    # Check if destination file already exists
    if destination_path.exists():
        print(f"⚠️  File already exists on Desktop: {barcode_filename}")
        print("   The existing file will be overwritten.")
    
    try:
        # Copy the file from archive to Desktop
        shutil.copy2(source_path, destination_path)
        
        print(f"✅ Successfully checked out file!")
        print(f"   Original: {original_filename}")
        print(f"   UUID: {uuid_str}")
        print(f"   Revision: {record['revision']}")
        print(f"   Destination: {destination_path}")
        print(f"   Barcode filename: {barcode_filename}")
        
    except Exception as e:
        print(f"❌ Failed to copy file: {e}")
        raise Exception(f"Failed to copy file: {e}")


def add_arguments(parser: argparse.ArgumentParser):
    """Add checkout command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to checkout'
    ) 