# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular Python CLI tool for converting documents between different formats (PDF, Markdown, DOCX). It uses a clean reader/writer architecture with a central document abstraction layer.

## Development Setup

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python convert.py input_file [options]
```

Common usage patterns:
- `python convert.py document.pdf -f md` - Convert PDF to Markdown
- `python convert.py document.pdf -f docx` - Convert PDF to DOCX
- `python convert.py document.md -f docx` - Convert Markdown to DOCX
- `python convert.py document.pdf -o custom_name.md` - Specify output file
- `python convert.py document.pdf --overwrite` - Overwrite without prompting
- `python convert.py --list-formats` - Show supported formats

## Code Architecture

The codebase follows a modular reader/writer pattern:

### Core Components

- **src/core/document.py**: Document abstraction layer with structured elements (headings, paragraphs, lists, code blocks)
- **src/core/converter.py**: Base converter interface and factory for orchestrating conversions

### Readers (src/readers/)
- **base.py**: Abstract base class for all readers
- **pdf_reader.py**: PDF parsing using PyMuPDF with heading detection
- **markdown_reader.py**: Markdown parsing with support for headings, lists, code blocks

### Writers (src/writers/)
- **base.py**: Abstract base class for all writers
- **markdown_writer.py**: Markdown generation from document objects
- **docx_writer.py**: DOCX generation using python-docx library

### CLI Interface
- **src/cli/main.py**: Click-based CLI with format detection and validation
- **convert.py**: Main entry point

### Extension Points

To add new format support:
1. Create new reader/writer classes inheriting from base classes
2. Implement required methods (read/write, format detection, supported extensions)
3. Register with ConverterFactory in src/__init__.py

The architecture supports easy extension to new formats and is designed to work well with web frameworks (Flask/FastAPI) by separating core conversion logic from CLI interface.

### Key Design Patterns
- **Factory Pattern**: `ConverterFactory` automatically registers and creates appropriate readers/writers
- **Document Abstraction**: Central `Document` class with `DocumentElement` subclasses (Heading, Paragraph, DocumentList, etc.)
- **Separation of Concerns**: Readers parse format-specific input → Document objects → Writers generate format-specific output

## Dependencies

- PyMuPDF (fitz): PDF text extraction
- Click: CLI framework
- python-docx: DOCX file generation
- pytest: Testing framework
- pytest-cov: Coverage reporting

## Testing

Run tests with:
```bash
pytest                              # Run all tests
pytest tests/unit/                  # Run unit tests only
pytest tests/integration/           # Run integration tests only
pytest --cov=src                    # Run with coverage report
pytest --cov=src --cov-report=html  # Generate HTML coverage report
pytest -k "test_document"           # Run specific test pattern
pytest tests/unit/test_document.py::TestDocument::test_add_heading  # Run single test
```

**Important Testing Notes:**
- **Type annotation conflict**: The `DocumentList` class was renamed to avoid conflicts with `typing.List`
- **Mocking strategy**: External libraries (PyMuPDF, python-docx) are fully mocked in tests
- **CLI testing**: Uses Click's `CliRunner` for integration testing
- **Coverage target**: Minimum 80% (currently achieving 96%)

Test structure:
- **tests/unit/**: Unit tests for individual components (106 tests)
- **tests/integration/**: Integration tests for CLI and end-to-end workflows (22 tests)
- **tests/conftest.py**: Shared fixtures including sample documents and temp directories
- **pytest.ini**: Pytest configuration with coverage settings and markers

## Development Notes

### Common Issues
- **Import errors**: Ensure virtual environment is activated and dependencies installed
- **Type annotation conflicts**: The codebase uses `DocumentList` instead of `List` to avoid conflicts with `typing.List`
- **CLI testing**: When writing CLI tests, be aware of file overwrite prompts - use different output formats or `--overwrite` flag
- **Mock configuration**: External library mocks (PyMuPDF, python-docx) require proper `__len__` and `__getitem__` setup

### Debugging
- Use `python convert.py --list-formats` to verify registered readers/writers
- Run `pytest -v -s` for verbose test output with print statements
- Check `htmlcov/index.html` after running coverage tests for detailed coverage analysis

## Supported Conversions

- PDF → Markdown
- PDF → DOCX
- Markdown → DOCX
- Markdown → Markdown (reformatting)