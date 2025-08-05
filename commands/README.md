# SFT Commands

This directory contains the modular command structure for the Sovereign File Tracker CLI.

## Structure

```
commands/
├── __init__.py          # Main commands module
├── core/                # Core file operations
│   ├── __init__.py      # Core utilities and decorators
│   ├── ingest.py        # File ingestion command
│   ├── find.py          # File search command
│   ├── view.py          # File viewing command
│   ├── checkout.py      # File checkout command
│   └── ls.py            # List recent files command
├── history/             # Version history operations
│   └── __init__.py      # History command
├── annotation/          # File annotation operations
│   ├── __init__.py      # Annotation command module
│   ├── note.py          # Note editing command
│   ├── tag.py           # Tag management command
│   └── untag.py         # Tag removal command
└── graph/               # Graph and relationship operations
    ├── __init__.py      # Graph command module
    ├── link.py          # File linking command
    ├── show_links.py    # Show file links command
    └── unlink.py        # Remove file links command
```

## Adding New Commands

To add a new command:

1. Create a new Python file in the appropriate subdirectory
2. Use the `@command` decorator to mark your function as a command
3. Implement the command function that takes an `argparse.Namespace` argument
4. Add an `add_arguments` function to define command-specific arguments

### Example

```python
import argparse
from commands.core import command, handle_command_error

@command(name='mycommand', description='My custom command')
@handle_command_error
def my_command(args: argparse.Namespace):
    """Handle the mycommand command."""
    # Your command logic here
    print(f"Executing mycommand with: {args.parameter}")

def add_arguments(parser: argparse.ArgumentParser):
    """Add mycommand arguments to the parser."""
    parser.add_argument(
        'parameter',
        type=str,
        help='Parameter for mycommand'
    )
```

## Command Discovery

The main `sft.py` script automatically discovers commands by:

1. Scanning subdirectories for `__init__.py` files
2. Scanning individual Python files within subdirectories
3. Looking for functions decorated with `@command`
4. Automatically registering discovered commands with argparse

## Available Commands

### Core Operations
- `ingest` - Ingest a new file into the SFT system
- `find` - Search for files in the SFT system
- `view` - View details of a specific file
- `checkout` - Checkout a file from the archive to Desktop
- `ls` - List the most recently tracked files
- `history` - Show version history of a file

### Annotation Operations
- `note` - Add or edit notes for a file
- `tag` - Add tags to a file record
- `untag` - Remove tags from a file record

### Graph Operations
- `link` - Create a link between two files
- `show-links` - Show all links from a source file
- `backlinks` - Show all files that link to a specified target file
- `all-links` - Show all outgoing and incoming links for a specified file
- `link-tag` - Add tags to a link between two files
- `link-untag` - Remove tags from a link between two files
- `unlink` - Remove a link between two files
- `trace` - Trace a path between two files and show threaded notes

### History Operations
- `history` - Show revision history for a file
- `diff` - Compare two revisions of a file

### Admin Operations
- `init` - Initialize the SFT system with folder structure and database tables
- `delete` - Soft delete a file (archive with status:deleted tag)
- `repair` - Audit and repair symbolic links in the SFT archive
- `stats` - Show comprehensive statistics about the SFT archive

## Link Command Details

The `link` command creates relationships between files in the SFT system:

### Usage
```bash
sft link <source_identifier> <target_identifier> [--note]
```

### Arguments
- `source_identifier`: UUID or filename of the source file
- `target_identifier`: UUID or filename of the target file
- `--note`: Open editor to add notes to the link after creation

### Features
- **File Resolution**: Automatically resolves filenames to UUIDs using the latest revision
- **Ambiguity Detection**: Handles cases where multiple files match an identifier
- **Duplicate Prevention**: Prevents creating duplicate links between the same files
- **Self-Link Prevention**: Prevents linking a file to itself
- **Link Notes**: Optional notes can be added to links using the `--note` flag
- **Interactive Editing**: Opens user's default editor for adding link notes
- **Error Handling**: Provides clear error messages for various failure scenarios

### Examples
```bash
# Link by filename
sft link document.txt reference.pdf

# Link by UUID
sft link 0688f2c8-15ef-7188-8000-bd0904be6719 06888748-2038-7950-8000-7cda73c402e9

# Mixed identifiers
sft link document.txt 06888748-2038-7950-8000-7cda73c402e9

# Link with notes
sft link document.txt reference.pdf --note
```

### Output Format
```
🔗 Creating link from 'test_ingest.txt' to 'my_first_test.txt'
✅ Successfully created link!
📝 Opening editor to add notes to the link...
   Make your changes and save the file, then return here.
✅ Successfully added notes to the link!
```

### Error Scenarios
- **File not found**: When either source or target file doesn't exist
- **Multiple matches**: When an identifier matches multiple files (use UUID for specificity)
- **Duplicate link**: When the link already exists
- **Self-linking**: When trying to link a file to itself

## Show-Links Command Details

The `show-links` command displays all files that are linked from a source file:

### Usage
```bash
sft show-links <identifier>
```

### Arguments
- `identifier`: UUID or filename to show links for

### Features
- **File Resolution**: Automatically resolves filenames to UUIDs using the latest revision
- **Ambiguity Detection**: Handles cases where multiple files match an identifier
- **Link Display**: Shows detailed information about each linked target file
- **Notes Preview**: Displays truncated notes from target files
- **User-Friendly Output**: Clear, organized display of link information

### Examples
```bash
# Show links by filename
sft show-links document.txt

# Show links by UUID
sft show-links 0688f2c8-15ef-7188-8000-bd0904be6719
```

### Output Format
```
🔗 Showing links from: 'test_ingest.txt'
   Source: test_ingest.txt (0688f2c8-15ef-7188-8000-bd0904be6719)

✅ Found 1 link(s):
================================================================================
🔗 Link 1:
   Target: my_first_test.txt
   UUID: 06888748-2038-7950-8000-7cda73c402e9
   Revision: 1
   Timestamp: 2025-07-28 21:13:06.013843-10:00
   Link Notes: This is a reference to the main project file
   Target Notes: Walk in a room full of PURPOSE!
================================================================================
```

### Error Scenarios
- **File not found**: When the identifier doesn't match any files
- **Multiple matches**: When an identifier matches multiple files (use UUID for specificity)
- **No links**: When the file exists but has no outgoing links

## Tag Command Details

The `tag` command adds tags to file records for better organization and searchability:

### Usage
```bash
sft tag <identifier> <tag1> [tag2] [tag3] ...
```

### Arguments
- `identifier`: UUID or filename to add tags to
- `tags`: One or more tags to add (space-separated)

### Features
- **File Resolution**: Automatically resolves filenames to UUIDs using the latest revision
- **Ambiguity Detection**: Handles cases where multiple files match an identifier
- **Duplicate Prevention**: Automatically avoids adding duplicate tags
- **Batch Tagging**: Add multiple tags in a single command
- **User-Friendly Output**: Clear success/failure messages with detailed information

### Examples
```bash
# Add single tag
sft tag document.txt important

# Add multiple tags
sft tag my_file.pdf urgent review draft

# Add tags using UUID
sft tag 0688f2c8-15ef-7188-8000-bd0904be6719 project-a milestone
```

### Output Format
```
🏷️  Adding tags to: 'my_first_test.txt'
   Tags to add: important, urgent
✅ Successfully added tags!
   File: my_first_test.txt
   Tags added: important, urgent
```

### Error Scenarios
- **File not found**: When the identifier doesn't match any files
- **Multiple matches**: When an identifier matches multiple files (use UUID for specificity)
- **No tags provided**: When no tags are specified
- **Database errors**: Connection issues or permission problems

## Untag Command Details

The `untag` command removes tags from file records:

### Usage
```bash
sft untag <identifier> <tag1> [tag2] [tag3] ...
```

### Arguments
- `identifier`: UUID or filename to remove tags from
- `tags`: One or more tags to remove (space-separated)

### Features
- **File Resolution**: Automatically resolves filenames to UUIDs using the latest revision
- **Ambiguity Detection**: Handles cases where multiple files match an identifier
- **Safe Removal**: Only removes tags that actually exist on the file
- **Batch Removal**: Remove multiple tags in a single command
- **User-Friendly Output**: Clear success/failure messages with detailed information

### Examples
```bash
# Remove single tag
sft untag document.txt important

# Remove multiple tags
sft untag my_file.pdf urgent review draft

# Remove tags using UUID
sft untag 0688f2c8-15ef-7188-8000-bd0904be6719 project-a milestone
```

### Output Format
```
🏷️  Removing tags from: 'my_first_test.txt'
   Tags to remove: important, urgent
✅ Successfully removed tags!
   File: my_first_test.txt
   Tags removed: important, urgent
```

### Error Scenarios
- **File not found**: When the identifier doesn't match any files
- **Multiple matches**: When an identifier matches multiple files (use UUID for specificity)
- **No tags provided**: When no tags are specified
- **Tags don't exist**: When trying to remove tags that aren't on the file
- **Database errors**: Connection issues or permission problems

## Find Command Details

The `find` command searches for files in the SFT system with pagination support:

### Usage
```bash
sft find <search_term> [--limit LIMIT] [--offset OFFSET]
```

### Arguments
- `search_term`: Search term to find files
- `--limit LIMIT`: Maximum number of files to display (default: 25)
- `--offset OFFSET`: Number of files to skip (default: 0)

### Features
- **File Resolution**: Automatically resolves filenames to UUIDs using the latest revision
- **Ambiguity Detection**: Handles cases where multiple files match an identifier
- **Notes Preview**: Displays truncated notes from files
- **User-Friendly Output**: Clear, organized display of search results
- **Pagination Support**: Handle large numbers of search results with limit and offset

### Examples
```bash
# Search for files (default: 25 results)
sft find document

# Search with custom limit
sft find test --limit 10

# Search with pagination
sft find file --limit 5 --offset 10
```

### Output Format
```
🔍 Searching for: 'test'
   Showing first 3 results
✅ Found 3 record(s):
================================================================================
📄 Record 1:
   UUID: 06888628-8936-706b-8000-64bb9dcb6447
   Filename: test_document.txt
   Revision: 2
   Notes: None
----------------------------------------
📄 Record 2:
   UUID: 0688f2c8-15ef-7188-8000-bd0904be6719
   Filename: test_ingest.txt
   Revision: 1
   Notes: Quick note for Cursor
================================================================================
💡 Use --offset 3 to see more results
```

### Error Scenarios
- **File not found**: When the search term doesn't match any files
- **No more results**: When pagination reaches the end of results
- **Database errors**: Connection issues or permission problems

## LS Command Details

The `ls` command lists the most recently tracked files in a clean, tabular format:

### Usage
```bash
sft ls [--limit LIMIT] [--offset OFFSET]
```

### Arguments
- `--limit LIMIT`: Maximum number of files to display (default: 25)
- `--offset OFFSET`: Number of files to skip (default: 0)

### Features
- **Recent Files**: Shows the most recently tracked files with pagination
- **Clean Table Format**: Displays UUID, Filename, and Revision in organized columns
- **Timestamp Ordering**: Files are ordered by timestamp (most recent first)
- **Filename Truncation**: Long filenames are automatically truncated for readability
- **User-Friendly Output**: Clear headers and separators for easy reading
- **Pagination Support**: Handle large numbers of files with limit and offset

### Examples
```bash
# List recent files (default: 25)
sft ls

# List first 10 files
sft ls --limit 10

# List next 10 files (skip first 10)
sft ls --limit 10 --offset 10

# List files 21-30
sft ls --limit 10 --offset 20
```

### Output Format
```
📋 Listing most recently tracked files...
   Showing first 5 results
✅ Found 5 recent file(s):
====================================================================================================
UUID                                 Filename                       Revision
----------------------------------------------------------------------------------------------------
0688f45b-bf3e-7596-8000-bbecfa3198e9 todo_test.txt                  1
0688f44e-7d19-745b-8000-7ab752e491c8 todo.txt                       1
0688f338-7b33-7205-8000-aafcf00b0638 test_no_extension              1
...
====================================================================================================
💡 Use --offset 5 to see more results
```

### Use Cases
- **Quick Overview**: Get a quick overview of recently added files
- **File Discovery**: Discover files you may have forgotten about
- **System Status**: Check the current state of your file tracking system
- **Revision Tracking**: See which files have multiple revisions

### Error Scenarios
- **No files**: When no files are found in the system
- **Database errors**: Connection issues or permission problems

## Unlink Command Details

The `unlink` command removes relationships between files in the `sft_links` table:

### Usage
```bash
sft unlink <source_identifier> <target_identifier>
```

### Arguments
- `source_identifier`: UUID or filename of the source file
- `target_identifier`: UUID or filename of the target file

### Features
- **File Resolution**: Automatically resolves filenames to UUIDs using the latest revision
- **Ambiguity Detection**: Handles cases where multiple files match an identifier
- **Link Validation**: Checks if the link exists before attempting removal
- **Database Safety**: Uses transactions to ensure data integrity
- **User-Friendly Output**: Clear success/failure messages with detailed information

### Examples
```bash
# Remove link by filename
sft unlink document.txt related_file.txt

# Remove link by UUID
sft unlink 0688f2c8-15ef-7188-8000-bd0904be6719 06888748-2038-7950-8000-7cda73c402e9

# Mixed identifiers
sft unlink document.txt 06888748-2038-7950-8000-7cda73c402e9
```

### Output Format
```
🔗 Removing link from 'test_ingest.txt' to 'my_first_test.txt'
   Source: test_ingest.txt (0688f2c8-15ef-7188-8000-bd0904be6719)
   Target: my_first_test.txt (06888748-2038-7950-8000-7cda73c402e9)
✅ Successfully removed link!
   From: test_ingest.txt (0688f2c8-15ef-7188-8000-bd0904be6719)
   To: my_first_test.txt (06888748-2038-7950-8000-7cda73c402e9)
```

### Error Scenarios
- **File not found**: When either source or target file doesn't exist
- **Multiple matches**: When an identifier matches multiple files (use UUID for specificity)
- **Link does not exist**: When trying to remove a non-existent link
- **Database errors**: Connection issues or permission problems

## Diff Command Details

The `diff` command compares two revisions of a file using Python's built-in difflib:

### Usage
```bash
sft diff <identifier> [--rev1 REV1] [--rev2 REV2]
```

### Arguments
- `identifier`: UUID or filename to compare revisions for
- `--rev1 REV1`: First revision number (defaults to second most recent)
- `--rev2 REV2`: Second revision number (defaults to most recent)

### Features
- **Automatic Revision Selection**: If no revisions specified, compares the two most recent
- **Unified Diff Format**: Uses Python's difflib for clear, readable diff output
- **Binary File Detection**: Detects and handles binary files gracefully
- **File Encoding Support**: Handles UTF-8 and fallback to latin-1 encoding
- **Revision Validation**: Ensures both revisions belong to the same file
- **Notes Comparison**: Shows differences in revision notes if they exist
- **User-Friendly Output**: Clear error messages and helpful feedback

### Examples
```bash
# Compare two most recent revisions
sft diff document.txt

# Compare specific revisions
sft diff my_file.txt --rev1 1 --rev2 3

# Compare using UUID
sft diff 06888628-8936-706b-8000-64bb9dcb6447 --rev1 1 --rev2 2
```

### Output Format
```
🔍 Comparing revisions for: 'test_document.txt'
   No revisions specified, using two most recent revisions
   Comparing revision 1 → 2
✅ Generating diff for: test_document.txt
   UUID: 06888628-8936-706b-8000-64bb9dcb6447
   Revision 1 (2025-07-28 19:56:24) → Revision 2 (2025-07-28 19:56:24)
================================================================================
--- test_document.txt (revision 1)
+++ test_document.txt (revision 2)
@@ -1,3 +1,4 @@
 Original content
+New line added
 Another line
================================================================================
```

### Error Scenarios
- **File not found**: When the identifier doesn't match any files
- **Insufficient revisions**: When less than 2 revisions exist
- **Revision not found**: When specified revision doesn't exist
- **File not found**: When archive files are missing
- **Binary files**: When attempting to diff binary files
- **Read errors**: When files cannot be read due to permissions or encoding

## Stats Command Details

The `stats` command provides comprehensive statistics about the SFT archive:

### Usage
```bash
sft stats
```

### Arguments
- No arguments required

### Features
- **Basic Statistics**: Shows total files, revisions, links, and recent activity
- **Category Breakdown**: Displays files organized by category (TEXT, IMAGES, AUDIO, BLOBS)
- **Tag Analysis**: Shows the most commonly used tags
- **Revision Tracking**: Lists files with the most revisions
- **Activity Metrics**: Shows recent activity and engagement statistics
- **Note Statistics**: Tracks files and links with notes
- **Calculated Metrics**: Provides averages and density metrics

### Examples
```bash
# Show archive statistics
sft stats
```

### Output Format
```
📊 SFT Archive Statistics
============================================================
📈 BASIC STATISTICS
------------------------------
📁 Unique Files:     27
📄 Total Revisions:  32
🔗 Total Links:      5
📝 Files with Notes: 13
🔗 Links with Notes: 1
🆕 Recent Files (7d): 27

📂 FILES BY CATEGORY
------------------------------
   TEXT      : 21
   UNKNOWN   : 5
   BLOBS     : 1

🏷️  TOP TAGS
------------------------------
   important      : 1 files

📋 FILES WITH MOST REVISIONS
------------------------------
   1. document.pdf                   (2 revisions)
   2. test_document.txt              (2 revisions)

📊 AVERAGE REVISIONS PER FILE: 1.2
🔗 AVERAGE LINKS PER FILE: 0.2
============================================================
```

### Use Cases
- **System Overview**: Get a quick overview of archive size and activity
- **Category Analysis**: Understand file type distribution
- **Tag Usage**: See which tags are most popular
- **Revision Tracking**: Identify frequently updated files
- **Activity Monitoring**: Track recent system usage
- **Performance Analysis**: Understand link density and engagement

### Error Scenarios
- **Database errors**: Connection issues or permission problems
- **Query errors**: Issues with complex SQL queries
- **Data corruption**: Problems with archive data integrity

## Trace Command Details

The `trace` command finds paths between files using recursive SQL queries and displays a threaded view of all notes:

### Usage
```bash
sft trace <start_identifier> <end_identifier>
```

### Arguments
- `start_identifier`: UUID or filename of the starting file
- `end_identifier`: UUID or filename of the ending file

### Features
- **Recursive Path Finding**: Uses PostgreSQL recursive CTEs to find paths through the link graph
- **Threaded View**: Displays all file notes and link notes in chronological order
- **Multi-step Paths**: Can trace paths with multiple intermediate files
- **Cycle Prevention**: Automatically prevents infinite loops in the graph
- **Depth Limiting**: Limits search depth to prevent performance issues
- **Comprehensive Display**: Shows file metadata, notes, tags, and link notes
- **Error Handling**: Graceful handling of missing files, ambiguous identifiers, and no-path scenarios

### Examples
```bash
# Trace a direct link between two files
sft trace test_ingest.txt test_no_extension

# Trace a multi-step path through the graph
sft trace test_ingest.txt todo_test.txt

# Use UUIDs for precise identification
sft trace 0688f2c8-15ef-7188-8000-bd0904be6719 0688f338-7b33-7205-8000-aafcf00b0638
```

### Output Format
```
🔍 Tracing path from 'test_ingest.txt' to 'todo_test.txt'
============================================================================
✅ Found path with 3 steps

🧵 THREADED VIEW - Notes and Links in Chronological Order
============================================================================
📄 STEP 1: test_ingest.txt
   UUID: 0688f2c8-15ef-7188-8000-bd0904be6719
   Revision: 1
   Timestamp: 2025-08-02 23:31:45
   📝 File Notes:
      Quick note for Cursor
      Another edit, im not too sure but here is more
   ────────────────────────────────────────────────────────────

📄 STEP 2: test_no_extension
   UUID: 0688f338-7b33-7205-8000-aafcf00b0638
   Revision: 1
   Timestamp: 2025-08-03 00:01:43
   📝 File Notes: None
   ────────────────────────────────────────────────────────────

📄 STEP 3: todo_test.txt
   UUID: 0688f45b-bf3e-7596-8000-bbecfa3198e9
   Revision: 1
   Timestamp: 2025-08-03 01:19:23
   📝 File Notes: None
   🔗 Link Notes:
      Notes
      #somenote
============================================================================
🎯 Path completed: test_ingest.txt → todo_test.txt
```

### Use Cases
- **Knowledge Discovery**: Find connections between related documents
- **Research Trails**: Trace the evolution of ideas through linked files
- **Documentation Analysis**: Understand relationships between project files
- **Content Threading**: Follow conversations or discussions across files
- **Graph Exploration**: Discover indirect connections in the file network
- **Audit Trails**: Track how information flows through the system

### Technical Details
- **Recursive SQL**: Uses PostgreSQL's `WITH RECURSIVE` CTE for path finding
- **Cycle Detection**: Prevents infinite loops by tracking visited nodes
- **Depth Limiting**: Maximum search depth of 10 steps for performance
- **Array Handling**: Properly parses PostgreSQL arrays for path reconstruction
- **UUID Resolution**: Converts filenames to UUIDs for precise identification
- **Latest Revisions**: Always shows the most recent revision of each file

### Error Scenarios
- **File not found**: When start or end identifier doesn't match any files
- **Ambiguous identifier**: When identifier matches multiple files
- **No path found**: When no link path exists between the files
- **Same file**: When start and end files are identical
- **Database errors**: Connection issues or query execution problems
- **Graph cycles**: Handled automatically by cycle detection

## Backlinks Command Details

The `backlinks` command shows all files that link to a specified target file:

### Usage
```bash
sft backlinks <identifier>
```

### Arguments
- `identifier`: UUID or filename of the target file

### Features
- **Inverse Link Discovery**: Finds all files that link TO the specified file
- **Comprehensive Information**: Shows source file metadata, notes, and link notes
- **Chronological Ordering**: Displays backlinks ordered by timestamp (newest first)
- **Latest Revisions**: Always shows the most recent revision of source files
- **Link Notes Integration**: Displays notes from the links themselves
- **User-Friendly Output**: Clean, formatted display with clear separators
- **Error Handling**: Graceful handling of missing files and ambiguous identifiers

### Examples
```bash
# Show backlinks to a file by filename
sft backlinks test_no_extension

# Show backlinks to a file by UUID
sft backlinks 0688f338-7b33-7205-8000-aafcf00b0638

# Show backlinks to a file with no incoming links
sft backlinks my_first_test.txt
```

### Output Format
```
🔗 Showing backlinks to: 'test_no_extension'
============================================================================
✅ Found 2 backlink(s):
============================================================================
🔗 Backlink 1:
   Source: todo_test.txt
   UUID: 0688f45b-bf3e-7596-8000-bbecfa3198e9
   Revision: 1
   Timestamp: 2025-08-03 01:19:23
   📝 Source Notes: None
   ────────────────────────────────────────────────────────────

🔗 Backlink 2:
   Source: test_ingest.txt
   UUID: 0688f2c8-15ef-7188-8000-bd0904be6719
   Revision: 1
   Timestamp: 2025-08-02 23:31:45
   📝 Source Notes: Quick note for Cursor

Another edit, im not too sure but here is more
============================================================================
```

### Use Cases
- **Reference Tracking**: See which files reference a specific document
- **Impact Analysis**: Understand which files depend on a target file
- **Content Discovery**: Find related content that links to a specific topic
- **Graph Exploration**: Discover incoming connections in the file network
- **Dependency Mapping**: Track which files are linked to a particular resource
- **Content Analysis**: Understand the influence and reach of specific files

### Technical Details
- **Inverse Query**: Uses `WHERE target_uuid = %s` to find incoming links
- **Latest Revisions**: Subquery ensures only the most recent revision is shown
- **Join Optimization**: Efficiently joins `sft_links` with `file_lineage` tables
- **Timestamp Ordering**: Results ordered by source file timestamp (DESC)
- **UUID Resolution**: Converts filenames to UUIDs for precise identification
- **Note Integration**: Shows both source file notes and link notes

### Error Scenarios
- **File not found**: When the identifier doesn't match any files
- **Ambiguous identifier**: When identifier matches multiple files
- **No backlinks**: When the file has no incoming links
- **Database errors**: Connection issues or query execution problems
- **Permission issues**: Problems accessing file metadata or link information

## All-Links Command Details

The `all-links` command provides a comprehensive view of all connections for a specified file:

### Usage
```bash
sft all-links <identifier>
```

### Arguments
- `identifier`: UUID or filename of the file to show all links for

### Features
- **Bidirectional View**: Shows both outgoing and incoming links in one command
- **Comprehensive Information**: Displays complete metadata for all connected files
- **Clear Sections**: Separate sections for outgoing and incoming links
- **Link Notes Integration**: Shows notes from both files and links
- **Summary Statistics**: Provides a quick overview of total connections
- **User-Friendly Output**: Clean, formatted display with clear separators
- **Error Handling**: Graceful handling of missing files and ambiguous identifiers

### Examples
```bash
# Show all links for a file with both outgoing and incoming links
sft all-links test_ingest.txt

# Show all links for a file with only outgoing links
sft all-links my_first_test.txt

# Show all links for a file with no connections
sft all-links some_unlinked_file.txt
```

### Output Format
```
🔗 Showing all links for: 'test_ingest.txt'
============================================================================
✅ Found 3 total link(s)

📤 OUTGOING LINKS (Linked To):
==================================================
🔗 Outgoing Link 1:
   Target: test_no_extension
   UUID: 0688f338-7b33-7205-8000-aafcf00b0638
   Revision: 1
   Timestamp: 2025-08-03 00:01:43
   📝 Target Notes: None
   ────────────────────────────────────────

🔗 Outgoing Link 2:
   Target: todo.txt
   UUID: 0688f44e-7d19-745b-8000-7ab752e491c8
   Revision: 1
   Timestamp: 2025-08-03 01:15:51
   📝 Target Notes: None

📥 INCOMING LINKS (Linked From):
==================================================
🔗 Incoming Link 1:
   Source: my_first_test.txt
   UUID: 06888748-2038-7950-8000-7cda73c402e9
   Revision: 1
   Timestamp: 2025-07-28 21:13:06
   📝 Source Notes: Walk in a room full of PURPOSE!
============================================================================
📊 Summary:
   Outgoing links: 2
   Incoming links: 1
   Total connections: 3
```

### Use Cases
- **Complete Network View**: Get a full picture of a file's connections
- **Relationship Analysis**: Understand both dependencies and dependents
- **Content Discovery**: Find all related files in both directions
- **Graph Exploration**: Discover the complete neighborhood of a file
- **Impact Assessment**: Understand the full scope of a file's influence
- **Connection Auditing**: Verify all links to and from a specific file

### Technical Details
- **Dual Function Calls**: Uses both `get_links_by_source` and `get_backlinks_by_target`
- **Efficient Queries**: Leverages existing optimized functions
- **Field Mapping**: Properly handles different field names from each function
- **Comprehensive Display**: Shows all available metadata for each connection
- **Summary Statistics**: Calculates and displays connection counts
- **Error Aggregation**: Handles errors from both outgoing and incoming queries

### Error Scenarios
- **File not found**: When the identifier doesn't match any files
- **Ambiguous identifier**: When identifier matches multiple files
- **No links found**: When the file has no outgoing or incoming links
- **Database errors**: Connection issues or query execution problems
- **Partial failures**: When one query succeeds but the other fails

## Link-Tag Command Details

The `link-tag` command adds tags to links between files:

### Usage
```bash
sft link-tag <source_identifier> <target_identifier> <tags...>
```

### Arguments
- `source_identifier`: UUID or filename of the source file
- `target_identifier`: UUID or filename of the target file
- `tags`: One or more tags to add to the link

### Features
- **Link Tagging**: Adds tags directly to links between files
- **Duplicate Prevention**: Automatically avoids adding duplicate tags
- **Multiple Tags**: Supports adding multiple tags in a single command
- **Link Validation**: Ensures the specified link exists before adding tags
- **File Resolution**: Converts filenames to UUIDs with ambiguity checking
- **Clear Feedback**: Shows exactly which tags were added to the link
- **Integration**: Tags are displayed in `all-links` and other link commands

### Examples
```bash
# Add a single tag to a link
sft link-tag test_ingest.txt test_no_extension important

# Add multiple tags to a link
sft link-tag test_ingest.txt test_no_extension important reference documentation

# Use UUIDs for precise identification
sft link-tag 0688f2c8-15ef-7188-8000-bd0904be6719 0688f338-7b33-7205-8000-aafcf00b0638 project core

# Add tags to a link that already has some tags (duplicates are ignored)
sft link-tag test_ingest.txt test_no_extension important new_tag
```

### Output Format
```
🏷️  Adding tags to link from 'test_ingest.txt' to 'test_no_extension'
   Tags to add: important, reference, documentation
============================================================================
✅ Successfully added tags to the link!
   Link: test_ingest.txt → test_no_extension
   Tags added: important, reference, documentation

💡 Use 'sft all-links' to see the updated link with tags.
```

### Use Cases
- **Link Categorization**: Organize links by type, purpose, or relationship
- **Relationship Tagging**: Mark links as dependencies, references, or related content
- **Project Organization**: Tag links by project, feature, or component
- **Content Discovery**: Use tags to find specific types of relationships
- **Workflow Management**: Tag links by status, priority, or workflow stage
- **Metadata Enhancement**: Add context and meaning to file relationships

### Technical Details
- **Database Integration**: Uses the new `tags` column in `sft_links` table
- **Array Handling**: Stores tags as PostgreSQL `TEXT[]` arrays
- **Duplicate Detection**: Checks existing tags before adding new ones
- **Transaction Safety**: Uses database transactions for data integrity
- **Link Validation**: Verifies link exists before attempting to modify tags
- **UUID Resolution**: Converts filenames to UUIDs for precise identification

### Error Scenarios
- **File not found**: When source or target identifier doesn't match any files
- **Ambiguous identifier**: When identifier matches multiple files
- **Link not found**: When no link exists between the specified files
- **Self-link attempt**: When trying to tag a link from a file to itself
- **Database errors**: Connection issues or query execution problems
- **Permission issues**: Problems with database write access

## Link-Untag Command Details

The `link-untag` command removes tags from links between files:

### Usage
```bash
sft link-untag <source_identifier> <target_identifier> <tags...>
```

### Arguments
- `source_identifier`: UUID or filename of the source file
- `target_identifier`: UUID or filename of the target file
- `tags`: One or more tags to remove from the link

### Features
- **Link Tag Removal**: Removes tags directly from links between files
- **Multiple Tags**: Supports removing multiple tags in a single command
- **Safe Removal**: Only removes tags that actually exist on the link
- **Link Validation**: Ensures the specified link exists before removing tags
- **File Resolution**: Converts filenames to UUIDs with ambiguity checking
- **Clear Feedback**: Shows exactly which tags were removed from the link
- **Integration**: Updated tags are displayed in `all-links` and other link commands

### Examples
```bash
# Remove a single tag from a link
sft link-untag test_ingest.txt test_no_extension reference

# Remove multiple tags from a link
sft link-untag test_ingest.txt test_no_extension important documentation

# Use UUIDs for precise identification
sft link-untag 0688f2c8-15ef-7188-8000-bd0904be6719 0688f338-7b33-7205-8000-aafcf00b0638 project core

# Remove tags that don't exist (handled gracefully)
sft link-untag test_ingest.txt test_no_extension nonexistent_tag
```

### Output Format
```
🏷️  Removing tags from link from 'test_ingest.txt' to 'test_no_extension'
   Tags to remove: reference
============================================================================
✅ Successfully removed tags from the link!
   Link: test_ingest.txt → test_no_extension
   Tags removed: reference

💡 Use 'sft all-links' to see the updated link with remaining tags.
```

### Use Cases
- **Tag Cleanup**: Remove outdated or incorrect tags from links
- **Tag Refinement**: Update link categorization by removing specific tags
- **Relationship Management**: Adjust how links are categorized and organized
- **Tag Maintenance**: Keep link tags current and relevant
- **Workflow Updates**: Remove tags when link status or purpose changes
- **Metadata Cleanup**: Maintain clean and accurate link metadata

### Technical Details
- **Database Integration**: Uses the `tags` column in `sft_links` table
- **Array Handling**: Updates PostgreSQL `TEXT[]` arrays by filtering out removed tags
- **Safe Removal**: Only removes tags that actually exist on the link
- **Transaction Safety**: Uses database transactions for data integrity
- **Link Validation**: Verifies link exists before attempting to modify tags
- **UUID Resolution**: Converts filenames to UUIDs for precise identification

### Error Scenarios
- **File not found**: When source or target identifier doesn't match any files
- **Ambiguous identifier**: When identifier matches multiple files
- **Link not found**: When no link exists between the specified files
- **Self-link attempt**: When trying to remove tags from a link from a file to itself
- **Database errors**: Connection issues or query execution problems
- **Permission issues**: Problems with database write access

## Init Command Details

The `init` command sets up the complete SFT system infrastructure:

### Usage
```bash
sft init
```

### Arguments
- No arguments required

### Features
- **Complete Setup**: Creates all necessary folders and database tables
- **Folder Structure**: Sets up the complete SFT directory hierarchy
- **Database Tables**: Creates `file_lineage` and `sft_links` tables
- **Safe Execution**: Handles existing folders and tables gracefully
- **Clear Feedback**: Provides detailed progress information
- **Next Steps Guidance**: Shows users what to do after initialization

### Folder Structure Created
```
_INGEST/
├── AUDIO/          # Audio files for ingestion
├── BLOBS/          # Binary/blob files for ingestion
├── IMAGES/         # Image files for ingestion
└── TEXT/           # Text files for ingestion

_UPDATE/            # Files to be updated

SovereignArchive/
├── AUDIO/          # Archived audio files
├── BLOBS/          # Archived binary/blob files
├── IMAGES/         # Archived image files
└── TEXT/           # Archived text files

SFT_Symlink/
├── AUDIO/          # Symlink directory for audio
├── BLOBS/          # Symlink directory for binary/blob
├── IMAGES/         # Symlink directory for images
└── TEXT/           # Symlink directory for text
```

### Database Tables Created
- **file_lineage**: Stores file metadata, revisions, and tracking information
- **sft_links**: Stores relationships between files with notes and tags

### Examples
```bash
# Initialize SFT system in current directory
sft init
```

### Output Format
```
🚀 Initializing SFT (Sovereign File Tracker) System
============================================================

📁 Creating SFT folder structure...
   ✅ Created: _INGEST/AUDIO
   ✅ Created: _INGEST/BLOBS
   ✅ Created: _INGEST/IMAGES
   ✅ Created: _INGEST/TEXT
   ✅ Created: _UPDATE
   ✅ Created: SovereignArchive/AUDIO
   ✅ Created: SovereignArchive/BLOBS
   ✅ Created: SovereignArchive/IMAGES
   ✅ Created: SovereignArchive/TEXT
   ✅ Created: SFT_Symlink/AUDIO
   ✅ Created: SFT_Symlink/BLOBS
   ✅ Created: SFT_Symlink/IMAGES
   ✅ Created: SFT_Symlink/TEXT

🗄️  Setting up database tables...
   📊 Creating file_lineage table...
   ✅ file_lineage table created successfully
   🔗 Creating sft_links table...
   ✅ sft_links table created successfully

============================================================
✅ SFT system initialization completed successfully!

📋 Next steps:
   1. Place files in the _INGEST folder to automatically track them
   2. Use 'sft ingest <filepath>' to manually ingest files
   3. Use 'sft --help' to see all available commands

🎉 Happy file tracking!
```

### Use Cases
- **New Installation**: Set up SFT system for the first time
- **Fresh Start**: Reinitialize system in a new directory
- **Development Setup**: Create test environment with proper structure
- **System Migration**: Set up SFT in a new location
- **Clean Installation**: Ensure all components are properly configured

### Technical Details
- **Directory Creation**: Uses `pathlib.Path.mkdir()` with `parents=True`
- **Database Integration**: Calls `create_file_lineage_table()` and `create_links_table()`
- **Error Handling**: Gracefully handles existing folders and database errors
- **Progress Tracking**: Shows detailed status for each step
- **Safe Execution**: Won't overwrite existing folders or tables

### Error Scenarios
- **Permission issues**: Insufficient permissions to create folders
- **Database connection**: PostgreSQL connection problems
- **Table creation**: Database schema creation failures
- **Disk space**: Insufficient disk space for folder creation
- **Existing tables**: Tables already exist (handled gracefully)

## Delete Command Details

The `delete` command performs a soft delete operation on files:

### Usage
```bash
sft delete <identifier>
```

### Arguments
- `identifier`: UUID or filename of the file to soft delete

### Features
- **Soft Delete**: Archives files instead of permanently removing them
- **Status Tagging**: Adds 'status:deleted' tag to the latest revision
- **Physical File Movement**: Moves files from SovereignArchive to _TRASH folder
- **Conflict Resolution**: Handles filename conflicts in _TRASH with numbered suffixes
- **Safety Checks**: Prevents deleting already-deleted files
- **Complete Cleanup**: Moves all revisions of a file to trash
- **Reversible**: Files can be restored by removing the status tag and moving files back

### Examples
```bash
# Delete by filename
sft delete document.txt

# Delete by UUID
sft delete 0688f2c8-15ef-7188-8000-bd0904be6719

# Delete a file with multiple revisions
sft delete project_document.pdf
```

### Output Format
```
🗑️  Soft deleting file: 'test_document.txt'
============================================================
✅ Successfully soft deleted the file!
   File: test_document.txt
   Status: Added 'status:deleted' tag
   Physical files: Moved to _TRASH folder

💡 The file is now archived but can be restored if needed.
   Use 'sft view' to see the updated record status.
```

### What Happens During Soft Delete

1. **Database Update**: Adds 'status:deleted' tag to the latest revision
2. **File Discovery**: Finds all physical files associated with the UUID
3. **Trash Creation**: Creates _TRASH directory if it doesn't exist
4. **File Movement**: Moves all physical files from SovereignArchive to _TRASH
5. **Conflict Handling**: Resolves filename conflicts with numbered suffixes
6. **Status Verification**: Ensures the file is properly marked as deleted

### Use Cases
- **Safe Deletion**: Remove files without permanent data loss
- **Temporary Removal**: Archive files that might be needed later
- **Bulk Cleanup**: Remove multiple files while maintaining recovery options
- **Testing**: Safely remove test files with easy restoration
- **Space Management**: Move files to trash for later permanent deletion
- **Audit Trail**: Maintain deletion history in the database

### Technical Details
- **Tag Management**: Uses PostgreSQL array operations for tag updates
- **File Operations**: Uses `shutil.move()` for safe file relocation
- **Path Handling**: Uses `pathlib.Path` for cross-platform compatibility
- **Database Transactions**: Ensures atomicity of tag updates
- **Error Recovery**: Rolls back database changes on file operation failures
- **UUID Resolution**: Converts filenames to UUIDs with ambiguity checking

### Error Scenarios
- **File not found**: When identifier doesn't match any files
- **Ambiguous identifier**: When identifier matches multiple files
- **Already deleted**: When file is already marked with 'status:deleted'
- **Permission issues**: Insufficient permissions to move files
- **Disk space**: Insufficient space in _TRASH directory
- **Database errors**: Connection issues or query execution problems
- **File system errors**: Problems with file operations or path resolution

### Restoration Process

To restore a soft-deleted file:

1. **Remove status tag**: Use `sft untag <identifier> status:deleted`
2. **Move files back**: Manually move files from _TRASH to appropriate SovereignArchive subdirectory
3. **Update archive paths**: Update the database records with new archive paths (if needed)

### Safety Features
- **Non-destructive**: Never permanently deletes files
- **Conflict resolution**: Handles filename conflicts automatically
- **Transaction safety**: Database changes are atomic
- **Error handling**: Graceful failure with rollback capabilities
- **Status tracking**: Clear indication of deletion status
- **Recovery options**: Multiple ways to restore deleted files

## Repair Command Details

The `repair` command audits and repairs symbolic links in the SFT archive:

### Usage
```bash
sft repair [--fix]
```

### Arguments
- `--fix`: Automatically fix broken or incorrect symbolic links (optional)

### Features
- **Archive Audit**: Comprehensive check of all symbolic links in SFT_Symlink directory
- **Issue Detection**: Identifies broken, missing, and incorrect symbolic links
- **Health Assessment**: Calculates overall archive health percentage
- **Auto-Repair**: Optional automatic fixing of detected issues
- **Detailed Reporting**: Shows specific issues and fix results
- **Safety First**: Audit-only mode by default, requires explicit --fix flag
- **Cross-Platform**: Works on Unix-like systems with symbolic link support

### Examples
```bash
# Audit only (safe, read-only operation)
sft repair

# Audit and automatically fix issues
sft repair --fix

# Check help
sft repair --help
```

### Output Format
```
🔧 SFT Archive Repair Tool
============================================================
🔍 Mode: Audit Only
   Will report issues but not attempt to fix them
============================================================

📊 AUDIT SUMMARY
------------------------------
📁 Total Files Checked: 15
✅ Valid Links: 12
❌ Broken Links: 2
🔗 Missing Links: 1
⚠️  Incorrect Links: 0
🏥 Archive Health: 80.0%

🔍 DETAILED ISSUES
------------------------------

❌ BROKEN LINKS (2):
   • document.txt (UUID: 0688f2c8-15ef-7188-8000-bd0904be6719)
     Error: No such file or directory
   • image.jpg (UUID: 0688f338-7b33-7205-8000-aafcf00b0638)
     Error: No such file or directory

🔗 MISSING LINKS (1):
   • report.pdf (UUID: 0688f3a8-1234-5678-9000-abcdef123456)
     Expected: SFT_Symlink/TEXT/0688f3a8-1234-5678-9000-abcdef123456

💡 RECOMMENDATIONS
------------------------------
🔧 Issues found in your SFT archive.
   Run 'sft repair --fix' to automatically fix these issues.
   Or manually check and fix the symbolic links listed above.

============================================================
```

### What the Repair Command Checks

1. **Symbolic Link Existence**: Verifies that symlinks exist for all tracked files
2. **Link Validity**: Checks that symlinks point to existing target files
3. **Target Accuracy**: Ensures symlinks point to the correct archive paths
4. **Directory Structure**: Validates SFT_Symlink directory structure
5. **File Categories**: Confirms symlinks are in the correct category subdirectories

### Types of Issues Detected

- **Broken Links**: Symlinks that point to non-existent files
- **Missing Links**: No symlink exists for a tracked file
- **Incorrect Links**: Symlinks that point to wrong targets or are not symlinks at all

### Auto-Repair Capabilities

When `--fix` flag is used, the command can:

- **Create Missing Symlinks**: Generate new symlinks for missing entries
- **Fix Broken Symlinks**: Recreate symlinks that point to non-existent files
- **Replace Incorrect Symlinks**: Remove and recreate symlinks pointing to wrong targets
- **Handle Conflicts**: Safely replace existing files/symlinks when needed

### Use Cases
- **System Maintenance**: Regular health checks of the SFT archive
- **Post-Migration**: Verify integrity after moving files or changing paths
- **Troubleshooting**: Diagnose issues with file access or symlink problems
- **Recovery**: Fix issues after file system changes or corruption
- **Validation**: Ensure archive integrity before backups or transfers
- **Development**: Test symlink functionality during development

### Technical Details
- **Database Integration**: Queries file_lineage table for all tracked files
- **File System Operations**: Uses pathlib for cross-platform path handling
- **Symbolic Link Management**: Creates and manages symlinks safely
- **Error Recovery**: Handles various file system error conditions
- **Performance**: Efficient batch processing of all archive files
- **Logging**: Comprehensive logging for debugging and audit trails

### Error Scenarios
- **Permission issues**: Insufficient permissions to create/modify symlinks
- **File system errors**: Problems with symbolic link operations
- **Database connection**: PostgreSQL connection issues
- **Missing directories**: SFT_Symlink directory structure problems
- **Target file issues**: Archive files that don't exist or are inaccessible
- **Cross-platform limitations**: Symbolic link support varies by OS

### Safety Features
- **Audit-Only Default**: Requires explicit --fix flag to make changes
- **Backup Awareness**: Preserves existing symlinks when possible
- **Error Handling**: Graceful failure with detailed error reporting
- **Validation**: Verifies target files exist before creating symlinks
- **Atomic Operations**: Safe symlink creation and replacement
- **Detailed Logging**: Comprehensive audit trail of all operations

### Best Practices
- **Regular Audits**: Run `sft repair` periodically to check archive health
- **Pre-Backup Checks**: Audit before creating backups or transferring archives
- **Post-Migration Verification**: Always run repair after moving files
- **Development Testing**: Use repair to validate symlink functionality
- **Troubleshooting**: Use audit results to diagnose file access issues 