# Sovereign File Tracker (SFT)

A local-first system for creating a permanent, versioned, and queryable knowledge graph for your entire digital life. Think "Git for any file," built for data sovereignty.

## The Philosophy

The Sovereign File Tracker (SFT) is a tool for builders, creators, and archivists who believe in data ownership. It solves three fundamental problems of modern digital life:

1.  **Data Fragmentation:** Your files and their context are scattered across dozens of apps and folders.
2.  **History & Lineage:** The evolution of your ideas and work is fragile and easily lost.
3.  **Application Lock-In:** Your data's history is trapped inside proprietary, walled-garden applications.

SFT extracts this power and gives it back to you, creating a single, robust, and permanent home for your data's history that you own and control.

## Core Features

  * **Universal File Tracking:** Tracks any file type, from text and images to audio and code.
  * **Automated Versioning:** Creates a complete, auditable history of every file using a `UUID + Revision` system.
  * **Rich Knowledge Graph:** Allows you to create explicit, directional links between any two files, with support for notes and tags on the links themselves.
  * **Powerful CLI:** A comprehensive command-line interface for interacting with your archive.
  * **Sovereign & Local-First:** All data and metadata are stored locally on your machine in a standard, open-source PostgreSQL database.

-----

## Setup & Installation

#### Prerequisites

  * Python 3.10+
  * PostgreSQL 15+
      * This project requires a running PostgreSQL server. For local development on macOS, we recommend the free [Postgres.app](https://postgresapp.com/).

#### Installation Steps

1.  Clone the repository: `git clone <your-repo-url>`
2.  Navigate into the project directory: `cd sovereign-file-tracker`
3.  Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  Install the required libraries: `pip install -r requirements.txt`
5.  Install the CLI in editable mode: `pip install -e .`
6.  Create a `.env` file for your database credentials (you can copy `.env.example`).
7.  Create the database in PostgreSQL: `CREATE DATABASE sft_db;`
8.  **Initialize the SFT folders and tables:**
    ```bash
    sft init
    ```

-----

## Usage

The SFT is composed of two main parts that run from your terminal: a background watcher and the CLI.

**1. Run the Watcher (in one terminal):**

```bash
python3 watcher.py
```

**2. Use the CLI (in a second terminal):**
The `sft` command is now available globally within your activated environment.

#### Core Commands

  * `sft ingest <filepath>`: Ingest a new file into the tracker.
  * `sft find <term>`: Search for files by filename or UUID.
  * `sft ls`: List the most recently tracked files.
  * `sft view <id>`: View the detailed metadata for a file.
  * `sft checkout <id>`: Get a working copy of a file.

#### History Commands

  * `sft history <id>`: See the complete revision history of a file.
  * `sft diff <id> --rev1 <n> --rev2 <m>`: Show the differences between two revisions of a text file.

#### Annotation Commands

  * `sft note <id>`: Add or edit a multi-line note for a file.
  * `sft tag <id> <tags...>`: Add one or more tags to a file.
  * `sft untag <id> <tags...>`: Remove tags from a file.

#### Knowledge Graph Commands

  * `sft link <source_id> <target_id> --note`: Create a link between two files, optionally with a note.
  * `sft unlink <source_id> <target_id>`: Remove a link.
  * `sft show-links <id>`: Show all outgoing links from a file.
  * `sft backlinks <id>`: Show all incoming links to a file.
  * `sft all-links <id>`: Get a 360-degree view of all connections.
  * `sft link-tag <source_id> <target_id> <tags...>`: Add tags to a specific link.
  * `sft link-untag <source_id> <target_id> <tags...>`: Remove tags from a specific link.

#### Admin Commands

  * `sft init`: Sets up the required folders and database tables.
  * `sft stats`: Shows high-level analytics about the SFT archive.
  * `sft delete <id>`: Safely moves a tracked file and its history to a trash folder.
  * `sft repair`: Audits the archive for inconsistencies and can fix broken symlinks.
  * `sft trace <start_id> <end_id>`: Traces a path through the knowledge graph.


```
## License

Sovereign File Tracker is licensed under the **AGPL-3.0** with an additional
[Attribution & Transparency Clause](./LICENSE). This ensures that anyone who
redistributes this software must clearly credit the original project and
inform users that it is available for free.
