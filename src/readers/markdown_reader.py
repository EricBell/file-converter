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

        i = 0
        while i < len(lines):
            line = lines[i]
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
                i += 1
                continue

            if in_code_block:
                code_block_lines.append(line)
                i += 1
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
                i += 1
                continue

            # Handle lists - check if line is a list item
            indent = len(line) - len(line.lstrip())
            list_match = re.match(r'^(\*|-|\+|\d+\.)\s+(.+)$', stripped_line)
            if list_match:
                if current_paragraph_lines:
                    self._add_paragraph(current_paragraph_lines, document)
                    current_paragraph_lines = []

                # Parse the entire list structure starting from this line
                list_element, lines_consumed = self._parse_list(lines[i:])
                document.add_element(list_element)
                i += lines_consumed
                continue

            # Handle empty lines
            if not stripped_line:
                if current_paragraph_lines:
                    self._add_paragraph(current_paragraph_lines, document)
                    current_paragraph_lines = []
                i += 1
                continue

            # Regular content line
            current_paragraph_lines.append(stripped_line)
            i += 1

        # Add any remaining paragraph
        if current_paragraph_lines:
            self._add_paragraph(current_paragraph_lines, document)

        # Handle any unclosed code block
        if in_code_block and code_block_lines:
            code_content = '\n'.join(code_block_lines)
            document.add_code_block(code_content, code_language)

    def _parse_list(self, lines: list[str]) -> tuple:
        """
        Parse a list structure with nested items.

        Returns:
            tuple: (DocumentList element, number of lines consumed)
        """
        from ..core.document import DocumentList, ListItem

        if not lines:
            return None, 0

        # Determine base indentation from first line
        first_line = lines[0]
        base_indent = len(first_line) - len(first_line.lstrip())

        # Determine if ordered or unordered
        stripped_first = first_line.strip()
        list_match = re.match(r'^(\*|-|\+|\d+\.)\s+(.+)$', stripped_first)
        if not list_match:
            return None, 0

        first_marker = list_match.group(1)
        is_ordered = first_marker.endswith('.')

        # Create the list
        list_element = DocumentList(ordered=is_ordered)

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            # Empty line ends the list
            if not stripped_line:
                break

            # Calculate indentation
            indent = len(line) - len(line.lstrip())

            # If indentation less than base, we're done with this list
            if indent < base_indent:
                break

            # If indentation equals base, it's an item at this level
            if indent == base_indent:
                list_match = re.match(r'^(\*|-|\+|\d+\.)\s+(.+)$', stripped_line)
                if not list_match:
                    # Not a list item, end of list
                    break

                list_content = list_match.group(2).strip()
                list_item = ListItem(content=list_content)
                list_element.items.append(list_item)
                i += 1

                # Check if next lines are nested (indented more)
                if i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    if next_stripped:
                        next_indent = len(next_line) - len(next_line.lstrip())
                        # If next line is indented more and is a list item, parse nested list
                        if next_indent > base_indent:
                            next_list_match = re.match(r'^(\*|-|\+|\d+\.)\s+(.+)$', next_stripped)
                            if next_list_match:
                                nested_list, nested_consumed = self._parse_list(lines[i:])
                                if nested_list:
                                    list_item.children.append(nested_list)
                                    i += nested_consumed
            else:
                # Indentation is greater than base but we shouldn't be here
                # This means it's a continuation or nested item that should have been handled
                break

        return list_element, i

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