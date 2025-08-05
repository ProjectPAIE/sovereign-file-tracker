"""
Find command module for the SFT CLI.
"""

import argparse
from . import command, handle_command_error, get_records_by_identifier


@command(name='find', description='Search for files in the SFT system')
@handle_command_error
def find_command(args: argparse.Namespace):
    """
    Handle the find command.
    
    Args:
        args: Parsed command line arguments
    """
    search_term = args.search_term
    limit = args.limit
    offset = args.offset
    
    # Validate search_term argument
    if not search_term:
        raise ValueError("Search term is required")
    
    print(f"🔍 Searching for: '{search_term}'")
    if offset > 0:
        print(f"   Showing results {offset + 1}-{offset + limit}")
    else:
        print(f"   Showing first {limit} results")
    
    # Call the get_records_by_identifier function from logic.py
    records = get_records_by_identifier(search_term, limit=limit, offset=offset)
    
    # Check if no records are found
    if not records:
        if offset > 0:
            print(f"❌ No more files found matching: '{search_term}' at this offset.")
        else:
            print(f"❌ No files found matching: '{search_term}'")
            print("   Try searching with a different term or check the spelling.")
        return
    
    # Print summary of found records
    print(f"✅ Found {len(records)} record(s):")
    print("=" * 80)
    
    # Loop through the results and print a clean, readable summary for each record
    for i, record in enumerate(records, 1):
        print(f"📄 Record {i}:")
        print(f"   UUID: {record['id']}")
        print(f"   Filename: {record['original_filename']}")
        print(f"   Revision: {record['revision']}")
        
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
        
        # Add separator between records (except for the last one)
        if i < len(records):
            print("-" * 40)
    
    print("=" * 80)
    
    # Show pagination info
    if len(records) == limit:
        print(f"💡 Use --offset {offset + limit} to see more results")


def add_arguments(parser: argparse.ArgumentParser):
    """Add find command arguments to the parser."""
    parser.add_argument(
        'search_term',
        type=str,
        help='Search term to find files'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=25,
        help='Maximum number of files to display (default: 25)'
    )
    parser.add_argument(
        '--offset',
        type=int,
        default=0,
        help='Number of files to skip (default: 0)'
    ) 