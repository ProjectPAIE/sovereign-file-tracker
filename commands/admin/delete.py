"""
Delete command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import soft_delete_record


@command(name='delete', description='Soft delete a file (archive with status:deleted tag)')
@handle_command_error
def delete_command(args: argparse.Namespace):
    """
    Handle the delete command.

    Args:
        args: Parsed command line arguments
    """
    identifier = args.identifier

    if not identifier:
        raise ValueError("Identifier is required")

    print(f"🗑️  Soft deleting file: '{identifier}'")
    print("=" * 60)

    try:
        # Perform soft delete
        success = soft_delete_record(identifier)

        if success:
            print("✅ Successfully soft deleted the file!")
            print(f"   File: {identifier}")
            print("   Status: Added 'status:deleted' tag")
            print("   Physical files: Moved to _TRASH folder")
            print()
            print("💡 The file is now archived but can be restored if needed.")
            print("   Use 'sft view' to see the updated record status.")

    except ValueError as e:
        print(f"❌ {e}")
        raise Exception(str(e))
    except Exception as e:
        print(f"❌ Error soft deleting file: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add delete command arguments to the parser."""
    parser.add_argument(
        'identifier',
        type=str,
        help='UUID or filename of the file to soft delete'
    ) 