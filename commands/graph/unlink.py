"""
Unlink command module for the SFT CLI.
"""

import argparse
from commands.core import get_records_by_identifier, command, handle_command_error
from logic import remove_link


@command(name='unlink', description='Remove a link between two files')
@handle_command_error
def unlink_command(args: argparse.Namespace):
    """
    Handle the unlink command.
    
    Args:
        args: Parsed command line arguments
    """
    source_identifier = args.source_identifier
    target_identifier = args.target_identifier
    
    # Validate arguments
    if not source_identifier:
        raise ValueError("Source identifier is required")
    if not target_identifier:
        raise ValueError("Target identifier is required")
    
    print(f"🔗 Removing link from '{source_identifier}' to '{target_identifier}'")
    
    # First, check if both files exist and are unique
    source_records = get_records_by_identifier(source_identifier)
    
    if not source_records:
        print(f"❌ Source file not found: '{source_identifier}'")
        print("   Try searching with a different identifier or check the spelling.")
        raise Exception(f"Source file not found: {source_identifier}")
    
    if len(source_records) > 1:
        print(f"❌ Multiple source files found for '{source_identifier}':")
        for record in source_records:
            print(f"   - {record['id']} (revision {record['revision']}): {record['original_filename']}")
        print("   Please use a more specific identifier (UUID recommended).")
        raise Exception(f"Multiple source files found: {source_identifier}")
    
    target_records = get_records_by_identifier(target_identifier)
    
    if not target_records:
        print(f"❌ Target file not found: '{target_identifier}'")
        print("   Try searching with a different identifier or check the spelling.")
        raise Exception(f"Target file not found: {target_identifier}")
    
    if len(target_records) > 1:
        print(f"❌ Multiple target files found for '{target_identifier}':")
        for record in target_records:
            print(f"   - {record['id']} (revision {record['revision']}): {record['original_filename']}")
        print("   Please use a more specific identifier (UUID recommended).")
        raise Exception(f"Multiple target files found: {target_identifier}")
    
    # Get the file details for display
    source_filename = source_records[0]['original_filename']
    target_filename = target_records[0]['original_filename']
    source_uuid = source_records[0]['id']
    target_uuid = target_records[0]['id']
    
    print(f"   Source: {source_filename} ({source_uuid})")
    print(f"   Target: {target_filename} ({target_uuid})")
    
    # Call the remove_link function from logic.py
    success = remove_link(source_identifier, target_identifier)
    
    if success:
        print(f"✅ Successfully removed link!")
        print(f"   From: {source_filename} ({source_uuid})")
        print(f"   To: {target_filename} ({target_uuid})")
    else:
        print(f"❌ Failed to remove link.")
        print("   Possible reasons:")
        print("   - Link does not exist between these files")
        print("   - Database connection error")
        print("   - Insufficient permissions")
        raise Exception(f"Failed to remove link between {source_identifier} and {target_identifier}")


def add_arguments(parser: argparse.ArgumentParser):
    """Add unlink command arguments to the parser."""
    parser.add_argument(
        'source_identifier',
        type=str,
        help='UUID or filename of the source file'
    )
    parser.add_argument(
        'target_identifier',
        type=str,
        help='UUID or filename of the target file'
    ) 