"""
Link-untag command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import remove_tags_from_link


@command(name='link-untag', description='Remove tags from a link between two files')
@handle_command_error
def link_untag_command(args: argparse.Namespace):
    """
    Handle the link-untag command.
    
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
    
    print(f"🏷️  Removing tags from link from '{source_identifier}' to '{target_identifier}'")
    print(f"   Tags to remove: {', '.join(tags)}")
    print("=" * 80)
    
    try:
        # Remove tags from the link
        success = remove_tags_from_link(source_identifier, target_identifier, tags)
        
        if success:
            print("✅ Successfully removed tags from the link!")
            print(f"   Link: {source_identifier} → {target_identifier}")
            print(f"   Tags removed: {', '.join(tags)}")
            print()
            print("💡 Use 'sft all-links' to see the updated link with remaining tags.")
        
    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    except Exception as e:
        print(f"❌ Error removing tags from link: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add link-untag command arguments to the parser."""
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
        help='Tags to remove from the link (one or more tags)'
    ) 