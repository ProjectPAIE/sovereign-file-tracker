"""
History command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error

# Import the history command from the history.py file
from .history import history_command as _history_command, add_arguments
# Import the diff command from the diff.py file
from .diff import diff_command as _diff_command, add_arguments as diff_add_arguments


@command(name='history', description='Show version history of a file')
@handle_command_error
def history_command(args: argparse.Namespace):
    """Handle the history command."""
    return _history_command(args)


@command(name='diff', description='Compare two revisions of a file')
@handle_command_error
def diff_command(args: argparse.Namespace):
    """Handle the diff command."""
    return _diff_command(args)
