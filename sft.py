#!/usr/bin/env python3
"""
Sovereign File Tracker - Command Line Interface
Main CLI tool for interacting with the SFT system.
"""

import argparse
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import the core logic functions
from logic import (
    ingest_new_file, 
    get_records_by_identifier, 
    edit_notes_interactive
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_command(filepath: str):
    """
    Handle the ingest command.
    
    Args:
        filepath: Path to the file to ingest
    """
    print(f"Ingesting file: {filepath}")
    
    cal_record = ingest_new_file(filepath)
    
    if cal_record:
        print(f"✅ Successfully ingested file!")
        print(f"   ID: {cal_record.id}")
        print(f"   Filename: {cal_record.original_filename}")
        print(f"   Archive path: {cal_record.archive_path}")
        print(f"   Revision: {cal_record.revision}")
    else:
        print(f"❌ Failed to ingest file: {filepath}")
        sys.exit(1)


def find_command(search_term: str):
    """
    Handle the find command.
    
    Args:
        search_term: Term to search for
    """
    print(f"Searching for: {search_term}")
    
    records = get_records_by_identifier(search_term)
    
    if not records:
        print(f"No files found matching: {search_term}")
        return
    
    print(f"Found {len(records)} record(s):")
    print("-" * 80)
    
    for record in records:
        print(f"ID: {record['id']}")
        print(f"Filename: {record['original_filename']}")
        print(f"Revision: {record['revision']}")
        print(f"Timestamp: {record['timestamp']}")
        print(f"Tags: {', '.join(record['tags']) if record['tags'] else 'None'}")
        print(f"Notes: {record['notes'][:100] + '...' if record['notes'] and len(record['notes']) > 100 else record['notes'] or 'None'}")
        print("-" * 80)


def view_command(identifier: str):
    """
    Handle the view command.
    
    Args:
        identifier: UUID or filename to view
    """
    print(f"Viewing details for: {identifier}")
    
    records = get_records_by_identifier(identifier)
    
    if not records:
        print(f"No files found for identifier: {identifier}")
        return
    
    if len(records) > 1:
        print(f"Multiple records found. Showing the latest revision:")
    
    # Show the latest revision (first in the list since it's ordered by revision DESC)
    record = records[0]
    
    print("=" * 80)
    print("FILE DETAILS")
    print("=" * 80)
    print(f"ID: {record['id']}")
    print(f"Filename: {record['original_filename']}")
    print(f"Revision: {record['revision']}")
    print(f"Archive Path: {record['archive_path']}")
    print(f"Timestamp: {record['timestamp']}")
    print(f"Tags: {', '.join(record['tags']) if record['tags'] else 'None'}")
    print(f"Notes:")
    if record['notes']:
        print(record['notes'])
    else:
        print("  None")
    print("=" * 80)


def history_command(identifier: str):
    """
    Handle the history command.
    
    Args:
        identifier: UUID or filename to show history for
    """
    print(f"Showing history for: {identifier}")
    
    records = get_records_by_identifier(identifier)
    
    if not records:
        print(f"No files found for identifier: {identifier}")
        return
    
    print(f"Version history ({len(records)} revision(s)):")
    print("=" * 80)
    
    for i, record in enumerate(records, 1):
        print(f"Revision {record['revision']} (Latest)" if i == 1 else f"Revision {record['revision']}")
        print(f"  ID: {record['id']}")
        print(f"  Filename: {record['original_filename']}")
        print(f"  Archive Path: {record['archive_path']}")
        print(f"  Timestamp: {record['timestamp']}")
        print(f"  Tags: {', '.join(record['tags']) if record['tags'] else 'None'}")
        if record['notes']:
            print(f"  Notes: {record['notes'][:100] + '...' if len(record['notes']) > 100 else record['notes']}")
        print("-" * 40)


def note_command(identifier: str):
    """
    Handle the note command.
    
    Args:
        identifier: UUID or filename to add/edit notes for
    """
    print(f"Editing notes for: {identifier}")
    
    success = edit_notes_interactive(identifier)
    
    if not success:
        sys.exit(1)


def main():
    """
    Main entry point for the SFT CLI.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Create the main parser
    parser = argparse.ArgumentParser(
        prog='sft',
        description='Sovereign File Tracker - Command Line Interface',
        epilog='Use "sft <command> --help" for more information about a command.'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Ingest command
    ingest_parser = subparsers.add_parser(
        'ingest',
        help='Ingest a new file into the SFT system'
    )
    ingest_parser.add_argument(
        'filepath',
        type=str,
        help='Path to the file to ingest'
    )
    ingest_parser.set_defaults(func=ingest_command)
    
    # Find command
    find_parser = subparsers.add_parser(
        'find',
        help='Search for files in the SFT system'
    )
    find_parser.add_argument(
        'search_term',
        type=str,
        help='Search term to find files'
    )
    find_parser.set_defaults(func=find_command)
    
    # View command
    view_parser = subparsers.add_parser(
        'view',
        help='View details of a specific file'
    )
    view_parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to view'
    )
    view_parser.set_defaults(func=view_command)
    
    # History command
    history_parser = subparsers.add_parser(
        'history',
        help='Show version history of a file'
    )
    history_parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to show history for'
    )
    history_parser.set_defaults(func=history_command)
    
    # Note command
    note_parser = subparsers.add_parser(
        'note',
        help='Add or edit notes for a file'
    )
    note_parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to add/edit notes for'
    )
    note_parser.set_defaults(func=note_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if a command was provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command
    try:
        # Extract the command-specific argument
        if args.command == 'ingest':
            args.func(args.filepath)
        elif args.command == 'find':
            args.func(args.search_term)
        elif args.command in ['view', 'history', 'note']:
            args.func(args.identifier)
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error executing command '{args.command}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
