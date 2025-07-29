# schemas.py
# This file contains the Pydantic data models (the "blueprints") for our application.

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

# Note: Python's standard 'uuid' library may not have uuid7() yet.
# We would install a small library like 'uuid_extensions' to provide this.
from uuid_extensions import uuid7


class CalRecord(BaseModel):
    """
    The blueprint for a single, versioned record in the Contextual Annotation Layer (CAL).
    Each instance of this model represents one snapshot of a file's history.
    """

    # --- Core Identifying Fields ---
    # The permanent, unique ID for the file concept. Generated with the modern,
    # time-ordered UUIDv7 for better database performance.
    id: uuid.UUID = Field(default_factory=uuid7)

    # The version number for this specific snapshot of the file.
    revision: int = 1


    # --- File System Metadata ---
    # The original, human-readable name of the file when it was ingested.
    original_filename: str

    # The absolute path to where this specific revision of the file is stored.
    archive_path: str


    # --- Contextual Annotation Layer (CAL) ---
    # A list of user- or system-generated tags for easy searching.
    tags: List[str] = []

    # Free-form notes added by the user or by AI agents.
    notes: Optional[str] = None


    # --- Timestamp ---
    # The timestamp of when this specific revision was created.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
