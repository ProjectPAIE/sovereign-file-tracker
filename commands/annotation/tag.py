"""
Tag command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import add_tags_to_record


@command(name='tag', description='Add tags to a file record')
@handle_command_error
def tag_command(args: argparse.Namespace):
    """
    Handle the tag command.
    
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
    
    print(f"🏷️  Adding tags to: '{identifier}'")
    print(f"   Tags to add: {', '.join(tags)}")
    
    # Call the add_tags_to_record function from logic.py
    success = add_tags_to_record(identifier, tags)
    
    if success:
        print(f"✅ Successfully added tags!")
        print(f"   File: {identifier}")
        print(f"   Tags added: {', '.join(tags)}")
    else:
        print(f"❌ Failed to add tags.")
        print("   Possible reasons:")
        print("   - File not found")
        print("   - Multiple files found (try using UUID)")
        print("   - Database connection error")
        print("   - All tags already exist")
        raise Exception(f"Failed to add tags to: {identifier}")


def add_arguments(parser: argparse.ArgumentParser):
    """Add tag command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to add tags to'
    )
    parser.add_argument(
        'tags',
        nargs='+',
        type=str,
        help='Tags to add (space-separated)'
    ) 