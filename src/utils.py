"""
Utility Helper Functions
Author: Akash Das
Project: Automated Resume Screening Tool

Contains shared file system helpers, logging setup, and data validators.
"""

from pathlib import Path
from typing import List


def get_supported_files(directory: Path, extensions: List[str] = None) -> List[Path]:
    """Retrieve all supported files matching the given extensions within a directory."""
    if extensions is None:
        extensions = [".pdf", ".docx", ".txt"]
    if not directory.exists() or not directory.is_dir():
        return []
    return [p for p in directory.iterdir() if p.suffix.lower() in extensions]


def ensure_directory(path: Path) -> Path:
    """Ensure that a directory exists, creating parent directories if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path
