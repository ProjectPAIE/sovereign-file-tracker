"""
Repair command module for the SFT CLI.
"""

import argparse
from commands.core import command, handle_command_error
from logic import audit_archive


@command(name='repair', description='Audit and repair symbolic links in the SFT archive')
@handle_command_error
def repair_command(args: argparse.Namespace):
    """
    Handle the repair command.

    Args:
        args: Parsed command line arguments
    """
    fix_issues = args.fix

    print("🔧 SFT Archive Repair Tool")
    print("=" * 60)

    if fix_issues:
        print("🔧 Mode: Audit and Auto-Fix")
        print("   Will attempt to automatically fix broken or incorrect symbolic links")
    else:
        print("🔍 Mode: Audit Only")
        print("   Will report issues but not attempt to fix them")

    print("=" * 60)

    try:
        # Perform the audit
        audit_results = audit_archive(fix_issues=fix_issues)

        # Print summary report
        print("\n📊 AUDIT SUMMARY")
        print("-" * 30)
        print(f"📁 Total Files Checked: {audit_results['total_files']}")
        print(f"✅ Valid Links: {audit_results['valid_links']}")
        print(f"❌ Broken Links: {audit_results['broken_links']}")
        print(f"🔗 Missing Links: {audit_results['missing_links']}")
        print(f"⚠️  Incorrect Links: {audit_results['incorrect_links']}")

        if fix_issues:
            print(f"🔧 Links Fixed: {audit_results['fixed_links']}")
            print(f"💥 Fixes Failed: {audit_results['failed_fixes']}")

        # Calculate health percentage
        total_issues = audit_results['broken_links'] + audit_results['missing_links'] + audit_results['incorrect_links']
        if audit_results['total_files'] > 0:
            health_percentage = ((audit_results['total_files'] - total_issues) / audit_results['total_files']) * 100
            print(f"🏥 Archive Health: {health_percentage:.1f}%")
        else:
            print("🏥 Archive Health: No files to check")

        # Print detailed issues if any
        if total_issues > 0:
            print("\n🔍 DETAILED ISSUES")
            print("-" * 30)

            if audit_results['broken_links'] > 0:
                print(f"\n❌ BROKEN LINKS ({audit_results['broken_links']}):")
                for issue in audit_results['broken_details'][:5]:  # Show first 5
                    print(f"   • {issue['filename']} (UUID: {issue['uuid']})")
                    print(f"     Error: {issue['error']}")
                if len(audit_results['broken_details']) > 5:
                    print(f"     ... and {len(audit_results['broken_details']) - 5} more")

            if audit_results['missing_links'] > 0:
                print(f"\n🔗 MISSING LINKS ({audit_results['missing_links']}):")
                for issue in audit_results['missing_details'][:5]:  # Show first 5
                    if isinstance(issue, dict):
                        print(f"   • {issue['filename']} (UUID: {issue['uuid']})")
                        print(f"     Expected: {issue['expected_path']}")
                    else:
                        print(f"   • {issue}")
                if len(audit_results['missing_details']) > 5:
                    print(f"     ... and {len(audit_results['missing_details']) - 5} more")

            if audit_results['incorrect_links'] > 0:
                print(f"\n⚠️  INCORRECT LINKS ({audit_results['incorrect_links']}):")
                for issue in audit_results['incorrect_details'][:5]:  # Show first 5
                    print(f"   • {issue['filename']} (UUID: {issue['uuid']})")
                    if 'current_target' in issue:
                        print(f"     Current: {issue['current_target']}")
                        print(f"     Expected: {issue['expected_target']}")
                    else:
                        print(f"     Error: {issue['error']}")
                if len(audit_results['incorrect_details']) > 5:
                    print(f"     ... and {len(audit_results['incorrect_details']) - 5} more")

        # Print fix results if in fix mode
        if fix_issues and (audit_results['fixed_links'] > 0 or audit_results['failed_fixes'] > 0):
            print("\n🔧 FIX RESULTS")
            print("-" * 30)

            if audit_results['fixed_links'] > 0:
                print(f"✅ Successfully Fixed: {audit_results['fixed_links']} links")
                for fix in audit_results['fixed_details'][:3]:  # Show first 3
                    print(f"   • {fix['filename']} -> {fix['target_path']}")
                if len(audit_results['fixed_details']) > 3:
                    print(f"     ... and {len(audit_results['fixed_details']) - 3} more")

            if audit_results['failed_fixes'] > 0:
                print(f"💥 Failed Fixes: {audit_results['failed_fixes']} links")
                for fix in audit_results['failed_details'][:3]:  # Show first 3
                    print(f"   • {fix['filename']} -> {fix['target_path']}")
                if len(audit_results['failed_details']) > 3:
                    print(f"     ... and {len(audit_results['failed_details']) - 3} more")

        # Print recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 30)

        if total_issues == 0:
            print("🎉 Your SFT archive is in perfect health!")
            print("   All symbolic links are valid and pointing to the correct files.")
        elif fix_issues:
            if audit_results['failed_fixes'] > 0:
                print("⚠️  Some issues could not be automatically fixed.")
                print("   Check the failed fixes above and resolve them manually.")
            else:
                print("✅ All issues have been automatically resolved!")
                print("   Your SFT archive should now be healthy.")
        else:
            print("🔧 Issues found in your SFT archive.")
            print("   Run 'sft repair --fix' to automatically fix these issues.")
            print("   Or manually check and fix the symbolic links listed above.")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ Repair operation failed: {e}")
        raise


def add_arguments(parser: argparse.ArgumentParser):
    """Add repair command arguments to the parser."""
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix broken or incorrect symbolic links'
    ) 