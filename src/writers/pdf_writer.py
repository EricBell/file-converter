"""
PDF writer implementation using ReportLab.
"""

from pathlib import Path
from typing import Union, Optional
import warnings
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    ListFlowable, ListItem, Preformatted
)
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .base import BaseWriter
from ..core.document import Document, ElementType
from ..core.footer import FooterConfig
from ..core.lockfile import cleanup_lock_files


class PDFWriter(BaseWriter):
    """Writer for PDF files using ReportLab."""

    # Class-level flag to track font registration
    _font_registered = False
    _unicode_font_name = None

    def __init__(self):
        """Initialize PDF writer and register Unicode-capable fonts."""
        super().__init__()
        if not PDFWriter._font_registered:
            PDFWriter._unicode_font_name = self._register_unicode_font()
            PDFWriter._font_registered = True

    def _register_unicode_font(self) -> str:
        """
        Register a Unicode-capable monospace font with ReportLab.

        Returns:
            str: The font name to use for code blocks, or 'Courier' as fallback
        """
        # Common font paths across different operating systems
        font_paths = [
            # Linux
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
            # macOS
            '/Library/Fonts/DejaVuSansMono.ttf',
            '/System/Library/Fonts/DejaVuSansMono.ttf',
            # Windows (if installed)
            'C:/Windows/Fonts/DejaVuSansMono.ttf',
            # Bundled with application
            Path(__file__).parent.parent / 'fonts' / 'DejaVuSansMono.ttf',
        ]

        for font_path in font_paths:
            font_path = Path(font_path)
            if font_path.exists():
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSansMono', str(font_path)))
                    return 'DejaVuSansMono'
                except Exception as e:
                    warnings.warn(f"Failed to register font {font_path}: {e}")

        # Fallback to Courier with warning
        warnings.warn(
            "DejaVu Sans Mono font not found. Unicode characters in code blocks "
            "may not render correctly. Using Courier as fallback."
        )
        return 'Courier'

    def write(self, document: Document, output_path: Union[str, Path],
              footer_config: Optional[FooterConfig] = None) -> None:
        """Write a document to a PDF file."""
        output_path = Path(output_path)

        if not self.supports_format(output_path):
            raise ValueError(f"Unsupported output format: "
                           f"{output_path.suffix}")

        try:
            self._create_pdf_document(document, output_path, footer_config)
        except Exception as e:
            raise IOError(f"Error writing to file {output_path}: {str(e)}")
        finally:
            # Always clean up lock files, even if an error occurred
            cleanup_lock_files(output_path)

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

    def _create_pdf_document(self, document: Document, output_path: Path,
                             footer_config: Optional[FooterConfig] = None) -> None:
        """Create a PDF document from our Document object with optional footers."""
        # Set up margins - increase bottom margin if footer is enabled
        bottom_margin = 48 if (footer_config and footer_config.enabled) else 18

        # Create the PDF document
        pdf_doc = BaseDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=bottom_margin
        )

        # Create frame for content
        frame = Frame(
            pdf_doc.leftMargin,
            pdf_doc.bottomMargin,
            pdf_doc.width,
            pdf_doc.height,
            id='normal'
        )

        # Create page template with footer callback
        def add_page_footer(canvas, doc):
            """Add footer to page if configured."""
            if footer_config and footer_config.enabled:
                canvas.saveState()
                page_num = canvas.getPageNumber()
                left_text, right_text = footer_config.get_footer_for_page(page_num)

                # Draw left footer text
                canvas.setFont('Helvetica', 9)
                canvas.drawString(doc.leftMargin, 24, left_text)

                # Draw right footer text
                canvas.drawRightString(
                    doc.width + doc.leftMargin,
                    24,
                    right_text
                )
                canvas.restoreState()

        template = PageTemplate(id='main', frames=[frame], onPage=add_page_footer)
        pdf_doc.addPageTemplates([template])

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

    def _convert_list(self, list_element, styles, base_indent=20):
        """
        Convert a list element to PDF, with support for nested lists.

        Args:
            list_element: The DocumentList to convert
            styles: ReportLab style sheet
            base_indent: Base indentation level in points

        Returns:
            List of flowables representing the list structure
        """
        if not hasattr(list_element, 'items') or not list_element.items:
            return None

        is_ordered = list_element.attributes.get('ordered', False)

        # Create flowables list to return
        flowables = []

        # Process each item
        for i, item in enumerate(list_element.items, 1):
            if is_ordered:
                bullet_text = f"{i}."
            else:
                bullet_text = "•"

            # Create paragraph for list item content
            item_para = Paragraph(item.content, styles['Normal'])

            # Create list item with proper indentation
            list_item_flowable = ListFlowable(
                [ListItem(item_para, bulletText=bullet_text, leftIndent=base_indent)],
                bulletType='bullet' if not is_ordered else '1',
                start=i if is_ordered else None,
                leftIndent=base_indent,
                bulletFontName='Helvetica',
                bulletFontSize=10
            )
            flowables.append(list_item_flowable)

            # Process nested children if any
            if hasattr(item, 'children') and item.children:
                for child_list in item.children:
                    nested_flowables = self._convert_list(child_list, styles, base_indent + 30)
                    if nested_flowables:
                        if isinstance(nested_flowables, list):
                            flowables.extend(nested_flowables)
                        else:
                            flowables.append(nested_flowables)

        return flowables

    def _convert_code_block(self, code_block, styles):
        """Convert a code block element to PDF."""
        # Create a custom style for code blocks with Unicode-capable monospace font
        code_style = ParagraphStyle(
            'CodeBlock',
            parent=styles['Code'],
            fontName=self._unicode_font_name or 'Courier',
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
