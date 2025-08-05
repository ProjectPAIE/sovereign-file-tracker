"""
Graph command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error

# Import the link command from the link.py file
from .link import link_command as _link_command, add_arguments as link_add_arguments

# Import the show-links command from the show_links.py file
from .show_links import show_links_command as _show_links_command, add_arguments as show_links_add_arguments

# Import the unlink command from the unlink.py file
from .unlink import unlink_command as _unlink_command, add_arguments as unlink_add_arguments

# Import the trace command from the trace.py file
from .trace import trace_command as _trace_command, add_arguments as trace_add_arguments

# Import the backlinks command from the backlinks.py file
from .backlinks import backlinks_command as _backlinks_command, add_arguments as backlinks_add_arguments

# Import the all-links command from the all_links.py file
from .all_links import all_links_command as _all_links_command, add_arguments as all_links_add_arguments

# Import the link-tag command from the link_tag.py file
from .link_tag import link_tag_command as _link_tag_command, add_arguments as link_tag_add_arguments

# Import the link-untag command from the link_untag.py file
from .link_untag import link_untag_command as _link_untag_command, add_arguments as link_untag_add_arguments


@command(name='link', description='Create a link between two files')
@handle_command_error
def link_command(args: argparse.Namespace):
    """Handle the link command."""
    return _link_command(args)


@command(name='show-links', description='Show all links from a source file')
@handle_command_error
def show_links_command(args: argparse.Namespace):
    """Handle the show-links command."""
    return _show_links_command(args)


@command(name='unlink', description='Remove a link between two files')
@handle_command_error
def unlink_command(args: argparse.Namespace):
    """Handle the unlink command."""
    return _unlink_command(args)


@command(name='trace', description='Trace a path between two files and show threaded notes')
@handle_command_error
def trace_command(args: argparse.Namespace):
    """Handle the trace command."""
    return _trace_command(args)


@command(name='backlinks', description='Show all files that link to a specified target file')
@handle_command_error
def backlinks_command(args: argparse.Namespace):
    """Handle the backlinks command."""
    return _backlinks_command(args)


@command(name='all-links', description='Show all outgoing and incoming links for a specified file')
@handle_command_error
def all_links_command(args: argparse.Namespace):
    """Handle the all-links command."""
    return _all_links_command(args)


@command(name='link-tag', description='Add tags to a link between two files')
@handle_command_error
def link_tag_command(args: argparse.Namespace):
    """Handle the link-tag command."""
    return _link_tag_command(args)


@command(name='link-untag', description='Remove tags from a link between two files')
@handle_command_error
def link_untag_command(args: argparse.Namespace):
    """Handle the link-untag command."""
    return _link_untag_command(args)
 