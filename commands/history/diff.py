import argparse
import difflib
from pathlib import Path
from typing import Optional

from commands.core import command, handle_command_error
from logic import get_records_by_identifier, get_file_paths_for_revisions


def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary by reading the first few bytes.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        bool: True if the file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' in chunk
    except Exception:
        return True


def read_file_content(file_path: str) -> Optional[str]:
    """
    Read the content of a text file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        str: File content or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return None
    except Exception:
        return None


@command(name='diff', description='Compare two revisions of a file')
@handle_command_error
def diff_command(args: argparse.Namespace):
    """
    Handle the diff command.
    
    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier
    rev1 = args.rev1
    rev2 = args.rev2
    
    if not identifier:
        raise ValueError("Identifier is required")
    
    print(f"🔍 Comparing revisions for: '{identifier}'")
    
    # If revisions not provided, get the two most recent
    if rev1 is None or rev2 is None:
        print("   No revisions specified, using two most recent revisions")
        records = get_records_by_identifier(identifier, limit=10)
        if not records:
            print(f"❌ File not found: '{identifier}'")
            print("   Try searching with a different identifier or check the spelling.")
            raise Exception(f"File not found: {identifier}")
        
        if len(records) < 2:
            print(f"❌ Only {len(records)} revision(s) found for '{identifier}'")
            print("   At least 2 revisions are required for comparison.")
            raise Exception(f"Insufficient revisions for comparison: {identifier}")
        
        rev1 = records[1]['revision']  # Second most recent
        rev2 = records[0]['revision']  # Most recent
        print(f"   Comparing revision {rev1} → {rev2}")
    
    # Get file paths for the two revisions
    try:
        file_info = get_file_paths_for_revisions(identifier, rev1, rev2)
    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    
    if not file_info:
        print(f"❌ File not found: '{identifier}'")
        print("   Try searching with a different identifier or check the spelling.")
        raise Exception(f"File not found: {identifier}")
    
    # Check if files exist
    rev1_path = Path(file_info['rev1']['path'])
    rev2_path = Path(file_info['rev2']['path'])
    
    if not rev1_path.exists():
        print(f"❌ Revision {rev1} file not found: {rev1_path}")
        raise Exception(f"Revision {rev1} file not found")
    
    if not rev2_path.exists():
        print(f"❌ Revision {rev2} file not found: {rev2_path}")
        raise Exception(f"Revision {rev2} file not found")
    
    # Check if files are binary
    if is_binary_file(str(rev1_path)) or is_binary_file(str(rev2_path)):
        print(f"❌ Binary file comparison not supported yet")
        print(f"   File: {file_info['original_filename']}")
        print(f"   Revisions: {rev1} and {rev2}")
        print("   Binary diff functionality will be added in a future version.")
        return
    
    # Read file contents
    rev1_content = read_file_content(str(rev1_path))
    rev2_content = read_file_content(str(rev2_path))
    
    if rev1_content is None:
        print(f"❌ Could not read revision {rev1} file: {rev1_path}")
        raise Exception(f"Could not read revision {rev1} file")
    
    if rev2_content is None:
        print(f"❌ Could not read revision {rev2} file: {rev2_path}")
        raise Exception(f"Could not read revision {rev2} file")
    
    # Generate diff
    print(f"✅ Generating diff for: {file_info['original_filename']}")
    print(f"   UUID: {file_info['file_uuid']}")
    print(f"   Revision {rev1} ({file_info['rev1']['timestamp']}) → Revision {rev2} ({file_info['rev2']['timestamp']})")
    print("=" * 80)
    
    # Split content into lines for diff
    rev1_lines = rev1_content.splitlines(keepends=True)
    rev2_lines = rev2_content.splitlines(keepends=True)
    
    # Generate unified diff
    diff_lines = difflib.unified_diff(
        rev1_lines,
        rev2_lines,
        fromfile=f"{file_info['original_filename']} (revision {rev1})",
        tofile=f"{file_info['original_filename']} (revision {rev2})",
        lineterm=''
    )
    
    # Print the diff
    diff_output = list(diff_lines)
    if diff_output:
        for line in diff_output:
            print(line)
    else:
        print("📄 No differences found between the two revisions.")
    
    print("=" * 80)
    
    # Show revision notes if they differ
    rev1_notes = file_info['rev1']['notes']
    rev2_notes = file_info['rev2']['notes']
    
    if rev1_notes != rev2_notes:
        print("📝 Revision Notes Comparison:")
        print(f"   Revision {rev1} notes: {rev1_notes or 'None'}")
        print(f"   Revision {rev2} notes: {rev2_notes or 'None'}")


def add_arguments(parser: argparse.ArgumentParser):
    """Add diff command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename to compare revisions for'
    )
    parser.add_argument(
        '--rev1',
        type=int,
        help='First revision number (defaults to second most recent)'
    )
    parser.add_argument(
        '--rev2',
        type=int,
        help='Second revision number (defaults to most recent)'
    ) 