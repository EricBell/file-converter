# PDF to Markdown Converter

A simple Python CLI tool to convert PDF files to Markdown format using PyMuPDF.

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python pdf2md.py input.pdf
```

### Options

- `-o, --output PATH`: Specify output file path (default: same name as input with .md extension)
- `--overwrite`: Overwrite output file if it exists without prompting
- `--version`: Show version information
- `--help`: Show help message

### Examples

```bash
# Convert PDF to markdown with default output name
python pdf2md.py document.pdf

# Convert with custom output file
python pdf2md.py document.pdf -o converted_document.md

# Overwrite existing output without prompt
python pdf2md.py document.pdf --overwrite
```

## Features

- Converts PDF text to clean Markdown format
- Automatic heading detection and formatting
- Text cleaning and normalization
- Error handling for invalid files
- Interactive confirmation for file overwrites

## Requirements

- Python 3.7+
- PyMuPDF (fitz) for PDF processing
- Click for CLI interface