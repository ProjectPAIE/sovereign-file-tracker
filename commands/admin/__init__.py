"""
Admin command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error

# Import the stats command from the stats.py file
from .stats import stats_command as _stats_command, add_arguments

# Import the init command from the init.py file
from .init import init_command as _init_command, add_arguments as init_add_arguments

# Import the delete command from the delete.py file
from .delete import delete_command as _delete_command, add_arguments as delete_add_arguments

# Import the repair command from the repair.py file
from .repair import repair_command as _repair_command, add_arguments as repair_add_arguments


@command(name='stats', description='Show comprehensive statistics about the SFT archive')
@handle_command_error
def stats_command(args: argparse.Namespace):
    """Handle the stats command."""
    return _stats_command(args)


@command(name='init', description='Initialize the SFT system with folder structure and database tables')
@handle_command_error
def init_command(args: argparse.Namespace):
    """Handle the init command."""
    return _init_command(args)


@command(name='delete', description='Soft delete a file (archive with status:deleted tag)')
@handle_command_error
def delete_command(args: argparse.Namespace):
    """Handle the delete command."""
    return _delete_command(args)


@command(name='repair', description='Audit and repair symbolic links in the SFT archive')
@handle_command_error
def repair_command(args: argparse.Namespace):
    """Handle the repair command."""
    return _repair_command(args) 