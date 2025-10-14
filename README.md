# File Converter

A modular Python CLI tool for converting documents between different formats (PDF, Markdown, DOCX) using a clean reader/writer architecture.

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
python convert.py input_file [options]
```

### Options

- `-o, --output PATH`: Specify output file path (auto-generated if not provided)
- `-f, --format FORMAT`: Output format (md, markdown, docx, pdf)
- `--overwrite`: Overwrite output file if it exists without prompting
- `--list-formats`: Show all supported input and output formats
- `--version`: Show version information
- `--help`: Show help message

### Examples

```bash
# Convert PDF to Markdown
python convert.py document.pdf -f md

# Convert PDF to DOCX
python convert.py document.pdf -f docx

# Convert Markdown to PDF
python convert.py document.md -f pdf

# Convert Markdown to DOCX
python convert.py document.md -f docx

# Convert with custom output file
python convert.py document.pdf -o converted_document.md

# Overwrite existing output without prompt
python convert.py document.pdf -f md --overwrite

# List all supported formats
python convert.py --list-formats
```

## Features

- **Multiple Format Support**: Convert between PDF, Markdown, and DOCX formats
- **PDF Generation**: Create professionally formatted PDFs from Markdown
- **Modular Architecture**: Clean reader/writer pattern with document abstraction
- **Smart Formatting**: Automatic heading detection, list handling, and code block formatting
- **CLI Interface**: User-friendly command-line tool with interactive prompts
- **Extensible Design**: Easy to add new format support

## Supported Conversions

- PDF → Markdown (.md)
- PDF → DOCX (.docx)
- PDF → PDF (reformatting)
- Markdown → PDF (.pdf)
- Markdown → DOCX (.docx)
- Markdown → Markdown (reformatting)

## Requirements

- Python 3.7+
- PyMuPDF (fitz): PDF text extraction
- ReportLab: PDF generation
- python-docx: DOCX file handling
- Click: CLI framework