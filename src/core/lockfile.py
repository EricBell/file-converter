"""
Utility module for managing lock files.

Handles cleanup of lock files that may be created by various libraries
or external processes during file operations.
"""

import os
import logging
from pathlib import Path
from typing import Union, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def get_lock_file_patterns(file_path: Union[str, Path]) -> List[Path]:
    """
    Get all possible lock file patterns for a given file path.

    Args:
        file_path: Path to the main file

    Returns:
        List of potential lock file paths
    """
    file_path = Path(file_path)
    parent = file_path.parent
    name = file_path.name
    stem = file_path.stem

    # Common lock file patterns
    patterns = [
        parent / f"~${name}",                    # Microsoft Office style
        parent / f"~${name}.tmp",                # Temporary lock
        parent / f".~lock.{name}#",              # LibreOffice style
        parent / f"{name}.lock",                 # Simple .lock suffix
        parent / f"~${stem}.ppwritelock",        # Custom python-pdf write lock (stem)
        parent / f"~${name}.ppwritelock",        # Custom python-pdf write lock (full name)
    ]

    return patterns


def remove_lock_file(lock_path: Union[str, Path]) -> bool:
    """
    Safely remove a lock file.

    Args:
        lock_path: Path to the lock file to remove

    Returns:
        bool: True if file was removed, False otherwise
    """
    lock_path = Path(lock_path)

    if not lock_path.exists():
        return False

    try:
        lock_path.unlink()
        logger.debug(f"Removed lock file: {lock_path}")
        return True
    except PermissionError:
        logger.warning(f"Permission denied when removing lock file: {lock_path}")
        return False
    except Exception as e:
        logger.warning(f"Failed to remove lock file {lock_path}: {e}")
        return False


def cleanup_lock_files(file_path: Union[str, Path]) -> int:
    """
    Clean up all lock files associated with a given file path.

    Args:
        file_path: Path to the main file

    Returns:
        int: Number of lock files removed
    """
    patterns = get_lock_file_patterns(file_path)
    removed_count = 0

    for lock_path in patterns:
        if remove_lock_file(lock_path):
            removed_count += 1

    if removed_count > 0:
        logger.info(f"Cleaned up {removed_count} lock file(s) for {file_path}")

    return removed_count


@contextmanager
def lock_file_cleanup(file_path: Union[str, Path]):
    """
    Context manager that ensures lock file cleanup after file operations.

    Usage:
        with lock_file_cleanup(output_path):
            # Perform file operations
            write_file(output_path)
        # Lock files are automatically cleaned up here

    Args:
        file_path: Path to the file being operated on
    """
    file_path = Path(file_path)

    try:
        yield file_path
    finally:
        # Always attempt cleanup, even if an exception occurred
        cleanup_lock_files(file_path)
