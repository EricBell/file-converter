"""
PDF writer implementation using ReportLab.
"""

from pathlib import Path
from typing import Union
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Preformatted
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .base import BaseWriter
from ..core.document import Document, ElementType


class PDFWriter(BaseWriter):
    """Writer for PDF files using ReportLab."""

    def write(self, document: Document, output_path: Union[str, Path]) -> None:
        """Write a document to a PDF file."""
        output_path = Path(output_path)

        if not self.supports_format(output_path):
            raise ValueError(f"Unsupported output format: "
                           f"{output_path.suffix}")

        try:
            self._create_pdf_document(document, output_path)
        except Exception as e:
            raise IOError(f"Error writing to file {output_path}: {str(e)}")

    def to_string(self, document: Document) -> str:
        """
        Convert a document to string representation.

        Note: PDF format doesn't have a meaningful string representation.
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

    def _create_pdf_document(self, document: Document, output_path: Path) -> None:
        """Create a PDF document from our Document object."""
        # Create the PDF document
        pdf_doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Get styles
        styles = getSampleStyleSheet()
        story = []

        # Add title if present
        if document.title:
            title_style = styles['Title']
            story.append(Paragraph(document.title, title_style))
            story.append(Spacer(1, 0.2 * inch))

        # Process each element
        for element in document.elements:
            flowables = self._convert_element_to_flowable(element, styles)
            if flowables:
                if isinstance(flowables, list):
                    story.extend(flowables)
                else:
                    story.append(flowables)
                # Add spacing after each element
                story.append(Spacer(1, 0.1 * inch))

        # Build the PDF
        pdf_doc.build(story)

    def _convert_element_to_flowable(self, element, styles):
        """Convert a document element to ReportLab flowables."""
        if element.element_type == ElementType.HEADING:
            return self._convert_heading(element, styles)
        elif element.element_type == ElementType.PARAGRAPH:
            return self._convert_paragraph(element, styles)
        elif element.element_type == ElementType.LIST:
            return self._convert_list(element, styles)
        elif element.element_type == ElementType.CODE_BLOCK:
            return self._convert_code_block(element, styles)
        else:
            # Fallback for unknown element types
            if element.content:
                return Paragraph(element.content, styles['Normal'])
            return None

    def _convert_heading(self, heading, styles):
        """Convert a heading element to PDF."""
        level = heading.attributes.get('level', 1)

        # Map heading levels to ReportLab styles
        style_map = {
            1: 'Heading1',
            2: 'Heading2',
            3: 'Heading3',
            4: 'Heading4',
            5: 'Heading5',
            6: 'Heading6'
        }

        style_name = style_map.get(level, 'Heading6')
        style = styles[style_name]

        return Paragraph(heading.content, style)

    def _convert_paragraph(self, paragraph, styles):
        """Convert a paragraph element to PDF."""
        return Paragraph(paragraph.content, styles['Normal'])

    def _convert_list(self, list_element, styles):
        """Convert a list element to PDF."""
        if not hasattr(list_element, 'items') or not list_element.items:
            return None

        is_ordered = list_element.attributes.get('ordered', False)

        # Create list items
        list_items = []
        for i, item in enumerate(list_element.items, 1):
            if is_ordered:
                bullet_text = f"{i}."
            else:
                bullet_text = "•"

            # Create paragraph for list item content
            item_para = Paragraph(item.content, styles['Normal'])
            list_items.append(ListItem(item_para, bulletText=bullet_text, leftIndent=20))

        # Create the list flowable
        list_flowable = ListFlowable(
            list_items,
            bulletType='bullet' if not is_ordered else 'number',
            start=1 if is_ordered else None,
            leftIndent=20,
            bulletFontName='Helvetica',
            bulletFontSize=10
        )

        return list_flowable

    def _convert_code_block(self, code_block, styles):
        """Convert a code block element to PDF."""
        # Create a custom style for code blocks with monospace font
        code_style = ParagraphStyle(
            'CodeBlock',
            parent=styles['Code'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=6,
            spaceAfter=6,
            backColor='#f5f5f5'
        )

        # Use Preformatted to preserve whitespace and formatting
        return Preformatted(code_block.content, code_style)

    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Check if this writer supports the given file format."""
        return Path(file_path).suffix.lower() == '.pdf'

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return ['.pdf']
