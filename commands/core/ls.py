"""
List command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import get_all_records


@command(name='ls', description='List the most recently tracked files')
@handle_command_error
def ls_command(args: argparse.Namespace):
    """
    Handle the ls command.
    
    Args:
        args: Parsed command line arguments
    """
    limit = args.limit
    offset = args.offset
    
    print(f"📋 Listing most recently tracked files...")
    if offset > 0:
        print(f"   Showing results {offset + 1}-{offset + limit}")
    else:
        print(f"   Showing first {limit} results")
    
    # Call the get_all_records function from logic.py
    records = get_all_records(limit=limit, offset=offset)
    
    if not records:
        if offset > 0:
            print("📭 No more files found at this offset.")
        else:
            print("📭 No files found in the system.")
        return
    
    # Print header
    print(f"✅ Found {len(records)} recent file(s):")
    print("=" * 100)
    print(f"{'UUID':<36} {'Filename':<30} {'Revision':<10}")
    print("-" * 100)
    
    # Print each record in a clean table format
    for record in records:
        uuid_str = str(record['id'])
        filename = record['original_filename']
        revision = str(record['revision'])
        
        # Truncate filename if it's too long
        if len(filename) > 28:
            filename = filename[:25] + "..."
        
        print(f"{uuid_str:<36} {filename:<30} {revision:<10}")
    
    print("=" * 100)
    
    # Show pagination info
    if len(records) == limit:
        print(f"💡 Use --offset {offset + limit} to see more results")


def add_arguments(parser: argparse.ArgumentParser):
    """Add ls command arguments to the parser."""
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