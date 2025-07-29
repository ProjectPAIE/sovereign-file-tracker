# Sovereign File Tracker (SFT)

SFT is a local-first system for creating a permanent, versioned, and annotated history for any file on your computer. The project is built on the core philosophy of **data sovereignty**, ensuring that you own and control the history and context of your digital life, free from any single application's ecosystem. It functions as a universal **"Local Wayback Machine"** or **"Git for anything,"** not just code.

## Core Features

  * **Automated Versioning:** Automatically tracks a complete, auditable history of your files using a `UUID` + `Revision` system.
  * **Centralized Metadata:** Uses a PostgreSQL database to store a rich, queryable **Contextual Annotation Layer (CAL)** with notes and tags for any file type.
  * **Application Independence:** Frees your data's history from any single proprietary application.
  * **Simple, Robust CLI:** Provides a powerful command-line interface to interact with your tracked files.

-----

## Setup & Installation

#### Prerequisites

  * Python 3.10+
  * PostgreSQL 15+
      * This project requires a running PostgreSQL server. For local development on macOS, we recommend the free [Postgres.app](https://postgresapp.com/).

#### Installation Steps

1.  Clone the repository: `git clone https://github.com/ProjectPAIE/sovereign-file-tracker.git`
2.  Navigate into the project directory: `cd SovereignFileTracker`
3.  Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  Install the required libraries: `pip install -r requirements.txt`
5.  Create a `.env` file for your database credentials (you can copy `.env.example`).
6.  Create the database in PostgreSQL: `CREATE DATABASE sft_db;`

-----

## Usage

The SFT is composed of two main parts that run from your terminal: a background watcher and a CLI.

**1. Run the Watcher (in one terminal):**

```bash
python watcher.py
```

**2. Use the CLI (in a second terminal):**

```bash
# Ingest a new file
python sft.py ingest /path/to/your/file.txt

# Find a file
python sft.py find "your_file"

# View a file's details
python sft.py view <uuid_or_filename>

# Edit a file's notes
python sft.py note <uuid_or_filename>
```
## License

Sovereign File Tracker is licensed under the **AGPL-3.0** with an additional
[Attribution & Transparency Clause](./LICENSE). This ensures that anyone who
redistributes this software must clearly credit the original project and
inform users that it is available for free.
