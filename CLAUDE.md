# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple Python CLI tool that converts PDF files to Markdown format using PyMuPDF (fitz) and Click for the command-line interface.

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
python pdf2md.py input.pdf
```

Common usage patterns:
- `python pdf2md.py document.pdf` - Convert with default output name
- `python pdf2md.py document.pdf -o custom_name.md` - Specify output file
- `python pdf2md.py document.pdf --overwrite` - Overwrite without prompting

## Code Architecture

The codebase consists of a single main file `pdf2md.py` with the following structure:

- **PDFToMarkdownConverter class**: Core conversion logic
  - `convert_pdf_to_markdown()`: Main conversion method that processes each page
  - `_process_text()`: Text processing and line-by-line formatting
  - `_is_heading()` / `_format_heading()`: Automatic heading detection and Markdown formatting
  - `_clean_text()`: Text normalization and cleanup

- **CLI interface**: Click-based command-line interface with options for output file, overwrite behavior, and version display

The converter uses PyMuPDF to extract text from PDF pages and applies heuristic-based formatting to detect headings and structure the output as clean Markdown.

## Dependencies

- PyMuPDF (fitz): PDF text extraction
- Click: CLI framework

No build system, test framework, or linting tools are currently configured.