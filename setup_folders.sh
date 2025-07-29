#!/bin/bash
# A simple script to create the directory structure for the Sovereign File Tracker.

echo "Creating SFT directory structure..."

# Create the main workflow folders
mkdir -p _INGEST
mkdir -p _UPDATE
mkdir -p SovereignArchive
mkdir -p SFT_Symlink

# Create the category sub-folders inside _INGEST
mkdir -p _INGEST/AUDIO
mkdir -p _INGEST/IMAGES
mkdir -p _INGEST/TEXT
mkdir -p _INGEST/BLOBS

echo "Directory structure created successfully."
