"""
Ingest command module for the SFT CLI.
"""

import argparse
from . import command, handle_command_error, ingest_new_file


@command(name='ingest', description='Ingest a new file into the SFT system')
@handle_command_error
def ingest_command(args: argparse.Namespace):
    """
    Handle the ingest command.
    
    Args:
        args: Parsed command line arguments
    """
    filepath = args.filepath
    
    # Validate filepath argument
    if not filepath:
        raise ValueError("Filepath is required")
    
    print(f"🔄 Ingesting file: {filepath}")
    
    # Call the ingest_new_file function from logic.py
    cal_record = ingest_new_file(filepath)
    
    # Check if the function was successful
    if cal_record:
        print(f"✅ Successfully ingested file!")
        print(f"   UUID: {cal_record.id}")
        print(f"   Filename: {cal_record.original_filename}")
        print(f"   Archive path: {cal_record.archive_path}")
        print(f"   Revision: {cal_record.revision}")
        print(f"   Timestamp: {cal_record.timestamp}")
        print(f"   Tags: {', '.join(cal_record.tags) if cal_record.tags else 'None'}")
        print(f"   Notes: {cal_record.notes or 'None'}")
    else:
        # Print a user-friendly error message
        print(f"❌ Failed to ingest file: {filepath}")
        print("   Possible reasons:")
        print("   - File does not exist")
        print("   - Path is not a valid file")
        print("   - Database connection error")
        print("   - Insufficient permissions")
        raise Exception(f"Failed to ingest file: {filepath}")


def add_arguments(parser: argparse.ArgumentParser):
    """Add ingest command arguments to the parser."""
    parser.add_argument(
        'filepath',
        type=str,
        help='Path to the file to ingest'
    ) 