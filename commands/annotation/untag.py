"""
Untag command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import remove_tags_from_record


@command(name='untag', description='Remove tags from a file record')
@handle_command_error
def untag_command(args: argparse.Namespace):
    """
    Handle the untag command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    tags = args.tags
    
    # Validate arguments
    if not identifier:
        raise ValueError("Identifier is required")
    if not tags:
        raise ValueError("At least one tag is required")
    
    print(f"🏷️  Removing tags from: '{identifier}'")
    print(f"   Tags to remove: {', '.join(tags)}")
    
    # Call the remove_tags_from_record function from logic.py
    success = remove_tags_from_record(identifier, tags)
    
    if success:
        print(f"✅ Successfully removed tags!")
        print(f"   File: {identifier}")
        print(f"   Tags removed: {', '.join(tags)}")
    else:
        print(f"❌ Failed to remove tags.")
        print("   Possible reasons:")
        print("   - File not found")
        print("   - Multiple files found (try using UUID)")
        print("   - Database connection error")
        print("   - Tags don't exist on the file")
        raise Exception(f"Failed to remove tags from: {identifier}")


def add_arguments(parser: argparse.ArgumentParser):
    """Add untag command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to remove tags from'
    )
    parser.add_argument(
        'tags',
        nargs='+',
        type=str,
        help='Tags to remove (space-separated)'
    ) 