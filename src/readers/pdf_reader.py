"""
PDF reader implementation using PyMuPDF.
"""

import re
from pathlib import Path
from typing import Union
import fitz  # PyMuPDF

from .base import BaseReader
from ..core.document import Document


class PDFReader(BaseReader):
    """Reader for PDF files using PyMuPDF."""

    def read(self, source: Union[str, Path]) -> Document:
        """Read and parse a PDF file."""
        source = Path(source)

        if not source.exists():
            raise FileNotFoundError(f"PDF file not found: {source}")

        if not self.supports_format(source):
            raise ValueError(f"Unsupported file format: {source.suffix}")

        try:
            doc = fitz.open(source)
            document = Document(title=source.stem)

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                if text.strip():
                    self._process_page_text(text, document)

            doc.close()
            return document

        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    def _process_page_text(self, text: str, document: Document) -> None:
        """Process text from a PDF page and add elements to document."""
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Clean the text
            cleaned_line = self._clean_text(line)

            # Check if it's a heading
            if self._is_heading(cleaned_line):
                level = self._determine_heading_level(cleaned_line)
                formatted_heading = self._format_heading_text(cleaned_line)
                document.add_heading(formatted_heading, level)
            else:
                # Add as paragraph
                document.add_paragraph(cleaned_line)

    def _is_heading(self, line: str) -> bool:
        """Determine if a line should be treated as a heading."""
        return (
            len(line) < 100 and
            (line.isupper() or
             re.match(r'^[A-Z][^.]*[^.]$', line) or
             re.match(r'^\d+\.?\s+[A-Z]', line))
        )

    def _determine_heading_level(self, line: str) -> int:
        """Determine the heading level based on line characteristics."""
        if re.match(r'^\d+\.?\s+', line):
            return 2  # Numbered headings are level 2
        elif line.isupper():
            return 1  # All caps are level 1
        else:
            return 2  # Default to level 2

    def _format_heading_text(self, line: str) -> str:
        """Format heading text for better readability."""
        if line.isupper():
            return line.title()
        return line

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix spacing around punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        return text.strip()

    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Check if this reader supports the given file format."""
        return Path(file_path).suffix.lower() == '.pdf'

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return ['.pdf']