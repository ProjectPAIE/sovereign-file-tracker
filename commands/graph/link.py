"""
Link command module for the SFT CLI.
"""

import argparse
import psycopg2
from commands.core import get_records_by_identifier, command, handle_command_error
from database import get_database_connection
from logic import create_link_with_notes, edit_link_notes_interactive


@command(name='link', description='Create a link between two files')
@handle_command_error
def link_command(args: argparse.Namespace):
    """
    Handle the link command.
    
    Args:
        args: Parsed command line arguments
    """
    source_identifier = args.source_identifier
    target_identifier = args.target_identifier
    add_note = args.note
    
    # Validate arguments
    if not source_identifier:
        raise ValueError("Source identifier is required")
    if not target_identifier:
        raise ValueError("Target identifier is required")
    
    print(f"🔗 Creating link from '{source_identifier}' to '{target_identifier}'")
    
    # Create the link using the new function
    try:
        success = create_link_with_notes(source_identifier, target_identifier)
        if success:
            print(f"✅ Successfully created link!")
            
            # If --note flag is used, open editor for link notes
            if add_note:
                print("📝 Opening editor to add notes to the link...")
                print("   Make your changes and save the file, then return here.")
                print()
                
                # Use the interactive notes editing function
                notes_success = edit_link_notes_interactive(source_identifier, target_identifier)
                if notes_success:
                    print("✅ Successfully added notes to the link!")
                else:
                    print("❌ Failed to add notes to the link.")
            
    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    except Exception as e:
        print(f"❌ Error creating link: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add link command arguments to the parser."""
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
    parser.add_argument(
        '--note',
        action='store_true',
        help='Open editor to add notes to the link after creation'
    ) 