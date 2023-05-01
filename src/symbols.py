"""Shared types."""

from datetime import datetime
from typing import TypedDict, Any


class FileMetadata(TypedDict):
    name: str
    name_without_ext: str
    path: str
    extension: str
    date_created: datetime
    date_modified: datetime
    original_file: Any

class PDFDocument():
    pass