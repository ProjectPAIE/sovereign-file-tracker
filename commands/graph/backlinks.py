"""
Backlinks command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import get_backlinks_by_target


@command(name='backlinks', description='Show all files that link to a specified target file')
@handle_command_error
def backlinks_command(args: argparse.Namespace):
    """
    Handle the backlinks command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"🔗 Showing backlinks to: '{identifier}'")
    print("=" * 80)
    
    try:
        # Get backlinks for the specified file
        backlinks = get_backlinks_by_target(identifier)
        
        if not backlinks:
            print(f"❌ No backlinks found for '{identifier}'")
            print("   This file is not linked to by any other files.")
            return
        
        print(f"✅ Found {len(backlinks)} backlink(s):")
        print("=" * 80)
        
        for i, backlink in enumerate(backlinks, 1):
            source_filename = backlink['source_filename']
            source_uuid = backlink['source_uuid']
            timestamp = backlink['timestamp']
            revision = backlink['revision']
            source_notes = backlink['source_notes']
            tags = backlink['tags']
            link_notes = backlink['link_notes']
            
            # Format timestamp
            if timestamp:
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_time = "Unknown"
            
            print(f"🔗 Backlink {i}:")
            print(f"   Source: {source_filename}")
            print(f"   UUID: {source_uuid}")
            print(f"   Revision: {revision}")
            print(f"   Timestamp: {formatted_time}")
            
            # Display tags if any
            if tags and len(tags) > 0:
                tags_str = ", ".join(tags)
                print(f"   Tags: {tags_str}")
            
            # Display link notes if they exist
            if link_notes and link_notes.strip():
                print(f"   🔗 Link Notes:")
                # Indent the link notes for better readability
                for line in link_notes.split('\n'):
                    if line.strip():
                        print(f"      {line}")
            
            # Display source file notes
            if source_notes and source_notes.strip():
                if len(source_notes) > 100:
                    truncated_notes = source_notes[:100] + "..."
                else:
                    truncated_notes = source_notes
                print(f"   📝 Source Notes: {truncated_notes}")
            else:
                print(f"   📝 Source Notes: None")
            
            # Add separator between backlinks (except for the last one)
            if i < len(backlinks):
                print("   " + "─" * 60)
                print()
        
        print("=" * 80)
        
    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    except Exception as e:
        print(f"❌ Error getting backlinks: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add backlinks command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename of the target file'
    ) 