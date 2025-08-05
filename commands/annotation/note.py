"""
Note command module for the SFT CLI.
"""

import argparse
from commands.core import edit_notes_interactive


def note_command(args: argparse.Namespace):
    """
    Handle the note command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    
    # Validate identifier argument
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"📝 Editing notes for: '{identifier}'")
    print("   This will open your default text editor.")
    print("   Make your changes and save the file, then return here.")
    print()
    
    # Call the edit_notes_interactive function from logic.py
    success = edit_notes_interactive(identifier)
    
    # Handle the results
    if success:
        print("✅ Notes updated successfully!")
    else:
        print("❌ Failed to edit notes.")
        print("   Possible reasons:")
        print("   - File not found")
        print("   - Multiple files found (try using UUID)")
        print("   - Database connection error")
        print("   - Editor not available")
        raise Exception(f"Failed to edit notes for: {identifier}")


def add_arguments(parser: argparse.ArgumentParser):
    """Add note command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to add/edit notes for'
    ) 