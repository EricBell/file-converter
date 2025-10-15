"""
Markdown writer implementation.
"""

from pathlib import Path
from typing import Union, Optional

from .base import BaseWriter
from ..core.document import Document, ElementType
from ..core.footer import FooterConfig
from ..core.lockfile import cleanup_lock_files


class MarkdownWriter(BaseWriter):
    """Writer for Markdown files."""

    def write(self, document: Document, output_path: Union[str, Path],
              footer_config: Optional[FooterConfig] = None) -> None:
        """
        Write a document to a Markdown file.

        Note: Footer configuration is ignored for Markdown since it doesn't
        have the concept of pages.
        """
        output_path = Path(output_path)

        if not self.supports_format(output_path):
            raise ValueError(f"Unsupported output format: "
                           f"{output_path.suffix}")

        try:
            markdown_content = self.to_string(document)
            output_path.write_text(markdown_content, encoding='utf-8')
        except Exception as e:
            raise IOError(f"Error writing to file {output_path}: {str(e)}")
        finally:
            # Always clean up lock files, even if an error occurred
            cleanup_lock_files(output_path)

    def to_string(self, document: Document) -> str:
        """Convert a document to Markdown string."""
        if not isinstance(document, Document):
            raise ValueError("Input must be a Document object")

        markdown_parts = []

        # Add title if present
        if document.title:
            markdown_parts.append(f"# {document.title}\n")

        # Process each element
        for element in document.elements:
            markdown_text = self._convert_element(element)
            if markdown_text:
                markdown_parts.append(markdown_text)

        return "\n\n".join(markdown_parts)

    def _convert_element(self, element) -> str:
        """Convert a document element to Markdown."""
        if element.element_type == ElementType.HEADING:
            return self._convert_heading(element)
        elif element.element_type == ElementType.PARAGRAPH:
            return self._convert_paragraph(element)
        elif element.element_type == ElementType.LIST:
            return self._convert_list(element)
        elif element.element_type == ElementType.CODE_BLOCK:
            return self._convert_code_block(element)
        else:
            # Fallback for unknown element types
            return element.content if element.content else ""

    def _convert_heading(self, heading) -> str:
        """Convert a heading element to Markdown."""
        level = heading.attributes.get('level', 1)
        prefix = '#' * level
        return f"{prefix} {heading.content}"

    def _convert_paragraph(self, paragraph) -> str:
        """Convert a paragraph element to Markdown."""
        return paragraph.content

    def _convert_list(self, list_element, indent_level=0) -> str:
        """
        Convert a list element to Markdown with support for nested lists.

        Args:
            list_element: The DocumentList to convert
            indent_level: Current indentation level (2 spaces per level)

        Returns:
            String representation of the list in Markdown format
        """
        if not hasattr(list_element, 'items') or not list_element.items:
            return ""

        is_ordered = list_element.attributes.get('ordered', False)
        markdown_lines = []

        indent = "  " * indent_level  # 2 spaces per indent level

        for i, item in enumerate(list_element.items, 1):
            if is_ordered:
                prefix = f"{i}."
            else:
                prefix = "-"
            markdown_lines.append(f"{indent}{prefix} {item.content}")

            # Process nested children if any
            if hasattr(item, 'children') and item.children:
                for child_list in item.children:
                    nested_markdown = self._convert_list(child_list, indent_level + 1)
                    if nested_markdown:
                        markdown_lines.append(nested_markdown)

        return "\n".join(markdown_lines)

    def _convert_code_block(self, code_block) -> str:
        """Convert a code block element to Markdown."""
        language = code_block.attributes.get('language', '')
        if language:
            return f"```{language}\n{code_block.content}\n```"
        else:
            return f"```\n{code_block.content}\n```"

    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Check if this writer supports the given file format."""
        return Path(file_path).suffix.lower() in ['.md', '.markdown']

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return ['.md', '.markdown']