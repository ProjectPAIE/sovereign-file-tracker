"""
Core command functionality for the SFT CLI.
"""

import sys
import argparse
from typing import Any

# Import the core logic functions
from logic import (
    ingest_new_file, 
    get_records_by_identifier, 
    edit_notes_interactive
)

# Import the checkout command from the checkout.py file
from .checkout import checkout_command as _checkout_command, add_arguments as checkout_add_arguments



def command(name: str = None, description: str = None):
    """Decorator to mark functions as commands."""
    def decorator(func):
        func._is_command = True
        func._command_name = name or func.__name__
        func._command_description = description or func.__doc__ or f'Execute {func.__name__}'
        return func
    return decorator


def handle_command_error(func):
    """Decorator to handle command errors gracefully."""
    def wrapper(args: argparse.Namespace):
        try:
            return func(args)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    return wrapper


class BaseCommand:
    """Base class for command implementations."""
    
    def __init__(self):
        self.logger = None
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add command-specific arguments to the parser."""
        pass
    
    def execute(self, args: argparse.Namespace):
        """Execute the command with the given arguments."""
        pass
    
    def print_success(self, message: str):
        """Print a success message."""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print an error message."""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Print an info message."""
        print(f"ℹ️  {message}")


@command(name='checkout', description='Checkout a file from the archive to Desktop')
@handle_command_error
def checkout_command(args: argparse.Namespace):
    """Handle the checkout command."""
    return _checkout_command(args)





def add_arguments(parser: argparse.ArgumentParser):
    """Add checkout command arguments to the parser."""
    checkout_add_arguments(parser)
