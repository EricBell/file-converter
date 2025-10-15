# Lock File Cleanup

## What was fixed

The file converter now automatically cleans up lock files (`.ppwritelock`, `~$*`, etc.) that may be created during document conversion operations.

### Changes made:

1. **New module**: `src/core/lockfile.py` - Handles lock file detection and cleanup
2. **Updated writers**: All writers (PDF, DOCX, Markdown) now clean up lock files after write operations
3. **Updated CLI**: Exception handler now cleans up lock files on errors
4. **Automatic cleanup**: Lock files are removed whether conversion succeeds or fails

## Current lock file issue

The existing `~$out.pdf.ppwritelock` file cannot be removed because it's currently held open by another process (probably a PDF viewer or editor).

### To resolve:

**Option 1: Close the PDF viewer/editor**
- Close any applications that may have `out.pdf` open
- Then run: `rm "~\$out.pdf.ppwritelock"` or simply delete it in Windows Explorer

**Option 2: Force remove (Windows)**
```bash
# In PowerShell or Command Prompt
del "~$out.pdf.ppwritelock"
```

**Option 3: Use the cleanup script**
After closing any PDF viewers, run:
```bash
python cleanup_locks.py
```

## Future conversions

All new conversions will automatically clean up lock files:
```bash
python convert.py document.md -f pdf -o output.pdf
# Lock files are automatically cleaned up after conversion
```

## Testing

All 128 unit tests pass with the new lock file cleanup functionality.
