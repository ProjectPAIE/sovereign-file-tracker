"""
All-links command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import get_links_by_source, get_backlinks_by_target


@command(name='all-links', description='Show all outgoing and incoming links for a specified file')
@handle_command_error
def all_links_command(args: argparse.Namespace):
    """
    Handle the all-links command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"🔗 Showing all links for: '{identifier}'")
    print("=" * 80)
    
    try:
        # Get outgoing links (files this file links to)
        outgoing_links = get_links_by_source(identifier)
        
        # Get incoming links (files that link to this file)
        incoming_links = get_backlinks_by_target(identifier)
        
        # Check if we have any links at all
        total_links = len(outgoing_links) + len(incoming_links)
        
        if total_links == 0:
            print(f"❌ No links found for '{identifier}'")
            print("   This file has no outgoing or incoming links.")
            print("   Use 'sft link' to create connections between files.")
            return
        
        print(f"✅ Found {total_links} total link(s)")
        print()
        
        # Display outgoing links
        print("📤 OUTGOING LINKS (Linked To):")
        print("=" * 50)
        
        if outgoing_links:
            for i, link in enumerate(outgoing_links, 1):
                target_filename = link['target_filename']
                target_uuid = link['target_uuid']
                timestamp = link['target_timestamp']
                revision = link['target_revision']
                target_notes = link['target_notes']
                link_notes = link['link_notes']
                link_tags = link['link_tags']
                
                # Format timestamp
                if timestamp:
                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    formatted_time = "Unknown"
                
                print(f"🔗 Outgoing Link {i}:")
                print(f"   Target: {target_filename}")
                print(f"   UUID: {target_uuid}")
                print(f"   Revision: {revision}")
                print(f"   Timestamp: {formatted_time}")
                
                # Show link tags if they exist
                if link_tags and len(link_tags) > 0:
                    tags_str = ", ".join(link_tags)
                    print(f"   🏷️  Link Tags: {tags_str}")
                
                # Show link notes if they exist
                if link_notes and link_notes.strip():
                    print(f"   🔗 Link Notes:")
                    # Indent the link notes for better readability
                    for line in link_notes.split('\n'):
                        if line.strip():
                            print(f"      {line}")
                
                # Show target file notes
                if target_notes and target_notes.strip():
                    if len(target_notes) > 100:
                        truncated_notes = target_notes[:100] + "..."
                    else:
                        truncated_notes = target_notes
                    print(f"   📝 Target Notes: {truncated_notes}")
                else:
                    print(f"   📝 Target Notes: None")
                
                # Add separator between links (except for the last one)
                if i < len(outgoing_links):
                    print("   " + "─" * 40)
                    print()
        else:
            print("   No outgoing links found.")
            print("   Use 'sft link' to create links from this file to others.")
        
        print()
        
        # Display incoming links
        print("📥 INCOMING LINKS (Linked From):")
        print("=" * 50)
        
        if incoming_links:
            for i, backlink in enumerate(incoming_links, 1):
                source_filename = backlink['source_filename']
                source_uuid = backlink['source_uuid']
                timestamp = backlink['timestamp']
                revision = backlink['revision']
                source_notes = backlink['source_notes']
                tags = backlink['tags']
                link_notes = backlink['link_notes']
                link_tags = backlink['link_tags']
                
                # Format timestamp
                if timestamp:
                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    formatted_time = "Unknown"
                
                print(f"🔗 Incoming Link {i}:")
                print(f"   Source: {source_filename}")
                print(f"   UUID: {source_uuid}")
                print(f"   Revision: {revision}")
                print(f"   Timestamp: {formatted_time}")
                
                # Display source file tags if any
                if tags and len(tags) > 0:
                    tags_str = ", ".join(tags)
                    print(f"   Tags: {tags_str}")
                
                # Show link tags if they exist
                if link_tags and len(link_tags) > 0:
                    tags_str = ", ".join(link_tags)
                    print(f"   🏷️  Link Tags: {tags_str}")
                
                # Show link notes if they exist
                if link_notes and link_notes.strip():
                    print(f"   🔗 Link Notes:")
                    # Indent the link notes for better readability
                    for line in link_notes.split('\n'):
                        if line.strip():
                            print(f"      {line}")
                
                # Show source file notes
                if source_notes and source_notes.strip():
                    if len(source_notes) > 100:
                        truncated_notes = source_notes[:100] + "..."
                    else:
                        truncated_notes = source_notes
                    print(f"   📝 Source Notes: {truncated_notes}")
                else:
                    print(f"   📝 Source Notes: None")
                
                # Add separator between links (except for the last one)
                if i < len(incoming_links):
                    print("   " + "─" * 40)
                    print()
        else:
            print("   No incoming links found.")
            print("   Other files can link to this file using 'sft link'.")
        
        print("=" * 80)
        
        # Summary
        print(f"📊 Summary:")
        print(f"   Outgoing links: {len(outgoing_links)}")
        print(f"   Incoming links: {len(incoming_links)}")
        print(f"   Total connections: {total_links}")
        
    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    except Exception as e:
        print(f"❌ Error getting links: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add all-links command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename of the file to show all links for'
    ) 