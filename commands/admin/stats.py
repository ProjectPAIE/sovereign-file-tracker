"""
Stats command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import get_archive_stats


@command(name='stats', description='Show comprehensive statistics about the SFT archive')
@handle_command_error
def stats_command(args: argparse.Namespace):
    """
    Handle the stats command.
    
    Args:
        args: Parsed command line arguments
    """
    print("📊 SFT Archive Statistics")
    print("=" * 60)
    
    try:
        # Get archive statistics
        stats = get_archive_stats()
        
        # Display basic statistics
        print("📈 BASIC STATISTICS")
        print("-" * 30)
        print(f"📁 Unique Files:     {stats['unique_files']:,}")
        print(f"📄 Total Revisions:  {stats['total_revisions']:,}")
        print(f"🔗 Total Links:      {stats['total_links']:,}")
        print(f"📝 Files with Notes: {stats['files_with_notes']:,}")
        print(f"🔗 Links with Notes: {stats['links_with_notes']:,}")
        print(f"🆕 Recent Files (7d): {stats['recent_files']:,}")
        
        # Display files by category
        if stats['files_by_category']:
            print("\n📂 FILES BY CATEGORY")
            print("-" * 30)
            for category, count in stats['files_by_category'].items():
                print(f"   {category:<10}: {count:,}")
        
        # Display top tags
        if stats['top_tags']:
            print("\n🏷️  TOP TAGS")
            print("-" * 30)
            for tag, count in stats['top_tags'].items():
                print(f"   {tag:<15}: {count:,} files")
        
        # Display files with most revisions
        if stats['files_with_most_revisions']:
            print("\n📋 FILES WITH MOST REVISIONS")
            print("-" * 30)
            for i, file_info in enumerate(stats['files_with_most_revisions'], 1):
                filename = file_info['filename']
                revisions = file_info['revisions']
                # Truncate filename if too long
                if len(filename) > 30:
                    filename = filename[:27] + "..."
                print(f"   {i}. {filename:<30} ({revisions} revisions)")
        
        # Calculate some additional metrics
        if stats['unique_files'] > 0:
            avg_revisions = stats['total_revisions'] / stats['unique_files']
            print(f"\n📊 AVERAGE REVISIONS PER FILE: {avg_revisions:.1f}")
        
        if stats['unique_files'] > 0 and stats['total_links'] > 0:
            link_density = stats['total_links'] / stats['unique_files']
            print(f"🔗 AVERAGE LINKS PER FILE: {link_density:.1f}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error retrieving statistics: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add stats command arguments to the parser."""
    # No arguments needed for stats command
    pass 