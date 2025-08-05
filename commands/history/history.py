"""
History command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error, get_records_by_identifier


def history_command(args: argparse.Namespace):
    """
    Handle the history command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    
    # Validate identifier argument
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"📜 Showing history for: '{identifier}'")
    
    # Call get_records_by_identifier to get all revisions for the file
    records = get_records_by_identifier(identifier)
    
    # If no records are found, print a 'File not found' error
    if not records:
        print(f"❌ File not found: '{identifier}'")
        print("   Try searching with a different identifier or check the spelling.")
        return
    
    # If records are found, loop through all of them and print a chronological summary
    print(f"✅ Found {len(records)} revision(s):")
    print("=" * 80)
    
    # Loop through all revisions (they're already ordered by revision DESC from the database)
    for i, record in enumerate(records, 1):
        # Determine if this is the latest revision
        is_latest = i == 1
        
        # Print revision header
        if is_latest:
            print(f"🆕 Revision {record['revision']} (Latest)")
        else:
            print(f"📄 Revision {record['revision']}")
        
        # Print revision details
        print(f"   UUID: {record['id']}")
        print(f"   Filename: {record['original_filename']}")
        print(f"   Archive Path: {record['archive_path']}")
        print(f"   Timestamp: {record['timestamp']}")
        print(f"   Tags: {', '.join(record['tags']) if record['tags'] else 'None'}")
        
        # Handle notes with truncation
        notes = record['notes']
        if notes:
            # Truncate notes if they're longer than 100 characters
            if len(notes) > 100:
                truncated_notes = notes[:100] + "..."
            else:
                truncated_notes = notes
            print(f"   Notes: {truncated_notes}")
        else:
            print(f"   Notes: None")
        
        # Add separator between revisions (except for the last one)
        if i < len(records):
            print("-" * 40)
    
    print("=" * 80)


def add_arguments(parser: argparse.ArgumentParser):
    """Add history command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to show history for'
    )
