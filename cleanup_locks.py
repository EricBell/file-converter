#!/usr/bin/env python3
"""
Utility script to clean up lock files in the project directory.
Run this to clean up any orphaned lock files.
"""

import os
from pathlib import Path
from src.core.lockfile import cleanup_lock_files, get_lock_file_patterns

def main():
    """Find and clean up all lock files in the current directory."""
    current_dir = Path(".")
    removed_count = 0
    
    # Find all files in current directory
    for file_path in current_dir.glob("*"):
        if file_path.is_file() and not file_path.name.startswith("~$"):
            # Try to clean up lock files for this file
            count = cleanup_lock_files(file_path)
            removed_count += count
    
    # Also try to remove any lock files directly
    for lock_file in current_dir.glob("~$*"):
        if lock_file.is_file():
            try:
                lock_file.unlink()
                print(f"Removed lock file: {lock_file}")
                removed_count += 1
            except Exception as e:
                print(f"Could not remove {lock_file}: {e}")
    
    if removed_count > 0:
        print(f"\nTotal: Cleaned up {removed_count} lock file(s)")
    else:
        print("No lock files found or all lock files are in use")

if __name__ == "__main__":
    main()
