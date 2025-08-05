"""
Trace command module for the SFT CLI.
"""

import argparse
from datetime import datetime
from commands.core import command, handle_command_error
from logic import trace_path_between_files


@command(name='trace', description='Trace a path between two files and show threaded notes')
@handle_command_error
def trace_command(args: argparse.Namespace):
    """
    Handle the trace command.
    
    Args:
        args: Parsed command line arguments
    """
    start_identifier = args.start_identifier
    end_identifier = args.end_identifier
    
    if not start_identifier:
        raise ValueError("Start identifier is required")
    if not end_identifier:
        raise ValueError("End identifier is required")
    
    print(f"🔍 Tracing path from '{start_identifier}' to '{end_identifier}'")
    print("=" * 80)
    
    try:
        # Get the path between the two files
        path_info = trace_path_between_files(start_identifier, end_identifier)
        
        if not path_info:
            print(f"❌ No path found between '{start_identifier}' and '{end_identifier}'")
            print("   Try creating links between the files first using the 'link' command.")
            raise Exception(f"No path found between {start_identifier} and {end_identifier}")
        
        print(f"✅ Found path with {len(path_info)} steps")
        print()
        
        # Display the threaded view
        print("🧵 THREADED VIEW - Notes and Links in Chronological Order")
        print("=" * 80)
        
        for i, file_info in enumerate(path_info):
            step = file_info['step']
            filename = file_info['filename']
            uuid = file_info['uuid']
            timestamp = file_info['timestamp']
            notes = file_info['notes']
            tags = file_info['tags']
            revision = file_info['revision']
            link_notes = file_info['link_notes']
            
            # Format timestamp
            if timestamp:
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_time = "Unknown"
            
            # Display file information
            print(f"📄 STEP {step}: {filename}")
            print(f"   UUID: {uuid}")
            print(f"   Revision: {revision}")
            print(f"   Timestamp: {formatted_time}")
            
            # Display tags if any
            if tags and len(tags) > 0:
                tags_str = ", ".join(tags)
                print(f"   Tags: {tags_str}")
            
            # Display file notes if any
            if notes and notes.strip():
                print(f"   📝 File Notes:")
                # Indent the notes for better readability
                for line in notes.split('\n'):
                    if line.strip():
                        print(f"      {line}")
            else:
                print(f"   📝 File Notes: None")
            
            # Display link notes if any (for connections between files)
            if link_notes and link_notes.strip():
                print(f"   🔗 Link Notes:")
                # Indent the link notes for better readability
                for line in link_notes.split('\n'):
                    if line.strip():
                        print(f"      {line}")
            
            # Add separator between files (except for the last one)
            if i < len(path_info) - 1:
                print("   " + "─" * 60)
                print()
        
        print("=" * 80)
        print(f"🎯 Path completed: {start_identifier} → {end_identifier}")
        
    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    except Exception as e:
        print(f"❌ Error tracing path: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add trace command arguments to the parser."""
    parser.add_argument(
        'start_identifier',
        type=str,
        help='UUID or filename of the starting file'
    )
    parser.add_argument(
        'end_identifier',
        type=str,
        help='UUID or filename of the ending file'
    ) 