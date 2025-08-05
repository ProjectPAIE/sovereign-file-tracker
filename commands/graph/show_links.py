"""
Show links command module for the SFT CLI.
"""

import argparse
from commands.core import get_records_by_identifier, command, handle_command_error
from logic import get_links_by_source


@command(name='show-links', description='Show all links from a source file')
@handle_command_error
def show_links_command(args: argparse.Namespace):
    """
    Handle the show-links command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    
    # Validate identifier argument
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"🔗 Showing links from: '{identifier}'")
    
    # First, check if the identifier exists and is unique
    source_records = get_records_by_identifier(identifier)
    
    if not source_records:
        print(f"❌ File not found: '{identifier}'")
        print("   Try searching with a different identifier or check the spelling.")
        raise Exception(f"File not found: {identifier}")
    
    if len(source_records) > 1:
        print(f"❌ Multiple files found for '{identifier}':")
        for record in source_records:
            print(f"   - {record['id']} (revision {record['revision']}): {record['original_filename']}")
        print("   Please use a more specific identifier (UUID recommended).")
        raise Exception(f"Multiple files found: {identifier}")
    
    # Get the source file details
    source_record = source_records[0]
    source_filename = source_record['original_filename']
    source_uuid = source_record['id']
    
    print(f"   Source: {source_filename} ({source_uuid})")
    print()
    
    # Get all links from this source using the new function from logic.py
    links = get_links_by_source(identifier)
    
    if not links:
        print(f"📭 No links found from '{source_filename}'")
        print("   Use 'sft link' to create relationships between files.")
        return
    
    # Display the links in a user-friendly format
    print(f"✅ Found {len(links)} link(s):")
    print("=" * 80)
    
    for i, link in enumerate(links, 1):
        print(f"🔗 Link {i}:")
        print(f"   Target: {link['target_filename']}")
        print(f"   UUID: {link['target_uuid']}")
        print(f"   Revision: {link['target_revision']}")
        print(f"   Timestamp: {link['target_timestamp']}")
        
        # Show link notes if they exist
        link_notes = link['link_notes']
        if link_notes:
            print(f"   Link Notes: {link_notes}")
        
        # Show target file notes
        notes = link['target_notes']
        if notes:
            if len(notes) > 100:
                truncated_notes = notes[:100] + "..."
            else:
                truncated_notes = notes
            print(f"   Target Notes: {truncated_notes}")
        else:
            print(f"   Target Notes: None")
        
        # Add separator between links (except for the last one)
        if i < len(links):
            print("-" * 40)
    
    print("=" * 80)


def add_arguments(parser: argparse.ArgumentParser):
    """Add show-links command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to show links for'
    ) 