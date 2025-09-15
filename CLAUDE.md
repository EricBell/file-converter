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

## Dependencies

- PyMuPDF (fitz): PDF text extraction
- Click: CLI framework
- python-docx: DOCX file generation
- pytest: Testing framework
- pytest-cov: Coverage reporting

## Testing

Run tests with:
```bash
pytest                    # Run all tests
pytest tests/unit/        # Run unit tests only
pytest tests/integration/ # Run integration tests only
pytest --cov=src          # Run with coverage report
```

Test structure:
- **tests/unit/**: Unit tests for individual components
- **tests/integration/**: Integration tests for CLI and end-to-end workflows
- **tests/conftest.py**: Shared fixtures and test configuration
- **pytest.ini**: Pytest configuration with coverage settings

The test suite includes:
- Document model tests
- Reader/writer tests with mocking
- Converter factory tests
- CLI integration tests
- Coverage reporting (minimum 80%)

## Supported Conversions

- PDF → Markdown
- PDF → DOCX
- Markdown → DOCX
- Markdown → Markdown (reformatting)