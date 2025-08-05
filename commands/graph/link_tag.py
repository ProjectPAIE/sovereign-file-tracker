"""
Link-tag command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import add_tags_to_link


@command(name='link-tag', description='Add tags to a link between two files')
@handle_command_error
def link_tag_command(args: argparse.Namespace):
    """
    Handle the link-tag command.
    
    Args:
        args: Parsed command line arguments
    """
    source_identifier = args.source_identifier
    target_identifier = args.target_identifier
    tags = args.tags
    
    if not source_identifier:
        raise ValueError("Source identifier is required")
    if not target_identifier:
        raise ValueError("Target identifier is required")
    if not tags:
        raise ValueError("At least one tag is required")
    
    print(f"🏷️  Adding tags to link from '{source_identifier}' to '{target_identifier}'")
    print(f"   Tags to add: {', '.join(tags)}")
    print("=" * 80)
    
    try:
        # Add tags to the link
        success = add_tags_to_link(source_identifier, target_identifier, tags)
        
        if success:
            print("✅ Successfully added tags to the link!")
            print(f"   Link: {source_identifier} → {target_identifier}")
            print(f"   Tags added: {', '.join(tags)}")
            print()
            print("💡 Use 'sft all-links' to see the updated link with tags.")
        
    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    except Exception as e:
        print(f"❌ Error adding tags to link: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add link-tag command arguments to the parser."""
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
        'tags',
        nargs='+',
        type=str,
        help='Tags to add to the link (one or more tags)'
    ) 