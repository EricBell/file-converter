"""
Markdown reader implementation.
"""

import re
from pathlib import Path
from typing import Union

from .base import BaseReader
from ..core.document import Document


class MarkdownReader(BaseReader):
    """Reader for Markdown files."""

    def read(self, source: Union[str, Path]) -> Document:
        """Read and parse a Markdown file."""
        source = Path(source)

        if not source.exists():
            raise FileNotFoundError(f"Markdown file not found: {source}")

        if not self.supports_format(source):
            raise ValueError(f"Unsupported file format: {source.suffix}")

        try:
            content = source.read_text(encoding='utf-8')
            document = Document(title=source.stem)
            self._parse_markdown_content(content, document)
            return document

        except Exception as e:
            raise Exception(f"Error processing Markdown: {str(e)}")

    def _parse_markdown_content(self, content: str, document: Document) -> None:
        """Parse markdown content and add elements to document."""
        lines = content.split('\n')
        current_paragraph_lines = []
        in_code_block = False
        code_block_lines = []
        code_language = None

        for line in lines:
            stripped_line = line.strip()

            # Handle code blocks
            if stripped_line.startswith('```'):
                if not in_code_block:
                    # Start of code block
                    if current_paragraph_lines:
                        self._add_paragraph(current_paragraph_lines, document)
                        current_paragraph_lines = []

                    in_code_block = True
                    # Extract language if specified
                    code_language = stripped_line[3:].strip() or None
                else:
                    # End of code block
                    if code_block_lines:
                        code_content = '\n'.join(code_block_lines)
                        document.add_code_block(code_content, code_language)
                    in_code_block = False
                    code_block_lines = []
                    code_language = None
                continue

            if in_code_block:
                code_block_lines.append(line)
                continue

            # Handle headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped_line)
            if heading_match:
                if current_paragraph_lines:
                    self._add_paragraph(current_paragraph_lines, document)
                    current_paragraph_lines = []

                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                document.add_heading(heading_text, level)
                continue

            # Handle lists
            list_match = re.match(r'^(\*|-|\+|\d+\.)\s+(.+)$', stripped_line)
            if list_match:
                if current_paragraph_lines:
                    self._add_paragraph(current_paragraph_lines, document)
                    current_paragraph_lines = []

                list_marker = list_match.group(1)
                list_content = list_match.group(2).strip()
                is_ordered = list_marker.endswith('.')

                # For simplicity, treat each list item as separate
                # In a more complex implementation, you'd group consecutive
                # list items together
                document.add_list([list_content], ordered=is_ordered)
                continue

            # Handle empty lines
            if not stripped_line:
                if current_paragraph_lines:
                    self._add_paragraph(current_paragraph_lines, document)
                    current_paragraph_lines = []
                continue

            # Regular content line
            current_paragraph_lines.append(stripped_line)

        # Add any remaining paragraph
        if current_paragraph_lines:
            self._add_paragraph(current_paragraph_lines, document)

        # Handle any unclosed code block
        if in_code_block and code_block_lines:
            code_content = '\n'.join(code_block_lines)
            document.add_code_block(code_content, code_language)

    def _add_paragraph(self, lines: list[str], document: Document) -> None:
        """Add a paragraph from collected lines."""
        if lines:
            paragraph_text = ' '.join(lines)
            # Basic cleanup - could be more sophisticated
            paragraph_text = re.sub(r'\s+', ' ', paragraph_text).strip()
            if paragraph_text:
                document.add_paragraph(paragraph_text)

    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Check if this reader supports the given file format."""
        return Path(file_path).suffix.lower() in ['.md', '.markdown']

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return ['.md', '.markdown']