"""
Note command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error

# Import the note command from the note.py file
from .note import note_command as _note_command, add_arguments
# Import the tag command from the tag.py file
from .tag import tag_command as _tag_command, add_arguments as tag_add_arguments
# Import the untag command from the untag.py file
from .untag import untag_command as _untag_command, add_arguments as untag_add_arguments


@command(name='note', description='Add or edit notes for a file')
@handle_command_error
def note_command(args: argparse.Namespace):
    """Handle the note command."""
    return _note_command(args)


@command(name='tag', description='Add tags to a file record')
@handle_command_error
def tag_command(args: argparse.Namespace):
    """Handle the tag command."""
    return _tag_command(args)


@command(name='untag', description='Remove tags from a file record')
@handle_command_error
def untag_command(args: argparse.Namespace):
    """Handle the untag command."""
    return _untag_command(args)
