# config.py
# Central configuration file for the Sovereign File Tracker.

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the .env file
load_dotenv()

# --- Database Configuration ---
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# --- Directory Configuration ---
# Use the current file's location to define the base path
BASE_DIR = Path(__file__).resolve().parent

# Define all workflow folders relative to the base path
INGEST_DIR = BASE_DIR / "_INGEST"
UPDATE_DIR = BASE_DIR / "_UPDATE"
ARCHIVE_DIR = BASE_DIR / "SovereignArchive"
SYMLINK_DIR = BASE_DIR / "SFT_Symlink"

# Define the categories for ingestion
CATEGORIES = ["AUDIO", "IMAGES", "TEXT", "BLOBS"]
