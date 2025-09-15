"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.core.document import Document


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    doc = Document(title="Test Document")
    doc.add_heading("Chapter 1", level=1)
    doc.add_paragraph("This is a paragraph with some text.")
    doc.add_heading("Section 1.1", level=2)
    doc.add_paragraph("Another paragraph with more content.")
    doc.add_list(["Item 1", "Item 2", "Item 3"], ordered=False)
    doc.add_heading("Section 1.2", level=2)
    doc.add_code_block("print('Hello, World!')", language="python")
    doc.add_paragraph("Final paragraph.")
    return doc


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Test Document

## Chapter 1

This is a paragraph with some text.

### Section 1.1

Another paragraph with more content.

- Item 1
- Item 2
- Item 3

### Section 1.2

```python
print('Hello, World!')
```

Final paragraph.
"""


@pytest.fixture
def sample_markdown_file(temp_dir, sample_markdown_content):
    """Create a sample markdown file for testing."""
    markdown_file = temp_dir / "sample.md"
    markdown_file.write_text(sample_markdown_content, encoding='utf-8')
    return markdown_file


@pytest.fixture
def sample_pdf_content():
    """Sample text content that would come from a PDF."""
    return """TEST DOCUMENT

CHAPTER 1

This is a paragraph with some text.

1. Section 1.1

Another paragraph with more content.

2. Section 1.2

Some code content here.

Final paragraph.
"""