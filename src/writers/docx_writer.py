"""
DOCX writer implementation using python-docx.
"""

from pathlib import Path
from typing import Union
from docx import Document as DocxDocument
from docx.shared import Inches

from .base import BaseWriter
from ..core.document import Document, ElementType


class DocxWriter(BaseWriter):
    """Writer for DOCX files using python-docx."""

    def write(self, document: Document, output_path: Union[str, Path]) -> None:
        """Write a document to a DOCX file."""
        output_path = Path(output_path)

        if not self.supports_format(output_path):
            raise ValueError(f"Unsupported output format: "
                           f"{output_path.suffix}")

        try:
            docx_doc = self._create_docx_document(document)
            docx_doc.save(output_path)
        except Exception as e:
            raise IOError(f"Error writing to file {output_path}: {str(e)}")

    def to_string(self, document: Document) -> str:
        """
        Convert a document to string representation.

        Note: DOCX format doesn't have a meaningful string representation.
        This returns a summary of the document structure.
        """
        if not isinstance(document, Document):
            raise ValueError("Input must be a Document object")

        parts = []
        if document.title:
            parts.append(f"Title: {document.title}")

        parts.append(f"Elements: {len(document.elements)}")

        element_counts = {}
        for element in document.elements:
            element_type = element.element_type.value
            element_counts[element_type] = element_counts.get(element_type, 0) + 1

        for element_type, count in element_counts.items():
            parts.append(f"  {element_type}: {count}")

        return "\n".join(parts)

    def _create_docx_document(self, document: Document) -> DocxDocument:
        """Create a python-docx Document from our Document object."""
        docx_doc = DocxDocument()

        # Add title if present
        if document.title:
            title = docx_doc.add_heading(document.title, level=0)

        # Process each element
        for element in document.elements:
            self._add_element_to_docx(element, docx_doc)

        return docx_doc

    def _add_element_to_docx(self, element, docx_doc: DocxDocument) -> None:
        """Add a document element to the DOCX document."""
        if element.element_type == ElementType.HEADING:
            self._add_heading_to_docx(element, docx_doc)
        elif element.element_type == ElementType.PARAGRAPH:
            self._add_paragraph_to_docx(element, docx_doc)
        elif element.element_type == ElementType.LIST:
            self._add_list_to_docx(element, docx_doc)
        elif element.element_type == ElementType.CODE_BLOCK:
            self._add_code_block_to_docx(element, docx_doc)
        else:
            # Fallback: treat as paragraph
            if element.content:
                docx_doc.add_paragraph(element.content)

    def _add_heading_to_docx(self, heading, docx_doc: DocxDocument) -> None:
        """Add a heading element to DOCX."""
        level = heading.attributes.get('level', 1)
        # Word headings are limited to levels 1-9
        level = min(max(level, 1), 9)
        docx_doc.add_heading(heading.content, level=level)

    def _add_paragraph_to_docx(self, paragraph, docx_doc: DocxDocument) -> None:
        """Add a paragraph element to DOCX."""
        docx_doc.add_paragraph(paragraph.content)

    def _add_list_to_docx(self, list_element, docx_doc: DocxDocument, indent_level=0) -> None:
        """
        Add a list element to DOCX with support for nested lists.

        Args:
            list_element: The DocumentList to convert
            docx_doc: The python-docx Document object
            indent_level: Current nesting level (0 = top level)
        """
        if not hasattr(list_element, 'items') or not list_element.items:
            return

        # python-docx doesn't have built-in list support, so we'll simulate it
        # with indented paragraphs
        is_ordered = list_element.attributes.get('ordered', False)

        # Calculate indentation based on nesting level
        base_indent = 0.25 + (indent_level * 0.5)  # Increase indent for each level

        for i, item in enumerate(list_element.items, 1):
            if is_ordered:
                bullet = f"{i}."
            else:
                bullet = "•"

            para = docx_doc.add_paragraph()
            para.paragraph_format.left_indent = Inches(base_indent)
            para.paragraph_format.first_line_indent = Inches(-0.25)
            run = para.add_run(f"{bullet} {item.content}")

            # Process nested children if any
            if hasattr(item, 'children') and item.children:
                for child_list in item.children:
                    self._add_list_to_docx(child_list, docx_doc, indent_level + 1)

    def _add_code_block_to_docx(self, code_block,
                               docx_doc: DocxDocument) -> None:
        """Add a code block element to DOCX."""
        # Add code as a paragraph with monospace font
        para = docx_doc.add_paragraph()
        run = para.add_run(code_block.content)
        run.font.name = 'Courier New'
        # Use a safe default size instead of accessing styles
        try:
            run.font.size = docx_doc.styles['Normal'].font.size
        except (KeyError, TypeError):
            # Fallback if styles access fails (e.g., in tests)
            pass

        # Add some styling to make it look like a code block
        para.paragraph_format.left_indent = Inches(0.5)
        para.paragraph_format.space_before = Inches(0.1)
        para.paragraph_format.space_after = Inches(0.1)

    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Check if this writer supports the given file format."""
        return Path(file_path).suffix.lower() == '.docx'

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return ['.docx']