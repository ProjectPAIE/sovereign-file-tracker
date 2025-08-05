"""
View command module for the SFT CLI.
"""

import argparse
from . import command, handle_command_error, get_records_by_identifier


@command(name='view', description='View details of a specific file')
@handle_command_error
def view_command(args: argparse.Namespace):
    """
    Handle the view command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    
    # Validate identifier argument
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"👁️  Viewing details for: '{identifier}'")
    
    # Call get_records_by_identifier to find the file
    records = get_records_by_identifier(identifier)
    
    # Handle the results gracefully
    if not records:
        print(f"❌ File not found: '{identifier}'")
        print("   Try searching with a different identifier or check the spelling.")
        return
    
    # Display the details for the latest revision only (first item in the returned list)
    record = records[0]
    
    # Format the output in a clean, readable, multi-line block
    print("=" * 80)
    print("📄 FILE DETAILS")
    print("=" * 80)
    print(f"UUID: {record['id']}")
    print(f"Filename: {record['original_filename']}")
    print(f"Revision: {record['revision']}")
    print(f"Archive Path: {record['archive_path']}")
    print(f"Timestamp: {record['timestamp']}")
    print(f"Tags: {', '.join(record['tags']) if record['tags'] else 'None'}")
    print(f"Notes:")
    
    # Show the full, un-truncated Notes
    if record['notes']:
        # Indent the notes for better readability
        notes_lines = record['notes'].split('\n')
        for line in notes_lines:
            print(f"  {line}")
    else:
        print("  None")
    
    print("=" * 80)


def add_arguments(parser: argparse.ArgumentParser):
    """Add view command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to view'
    ) 