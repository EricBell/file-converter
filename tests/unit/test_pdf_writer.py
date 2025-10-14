"""
Unit tests for PDF writer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from src.writers.pdf_writer import PDFWriter
from src.core.document import Document, ElementType


class TestPDFWriter:
    """Test PDFWriter functionality."""

    def test_supports_format_pdf(self):
        """Test that PDF writer supports .pdf files."""
        writer = PDFWriter()
        assert writer.supports_format("test.pdf") is True
        assert writer.supports_format("test.PDF") is True

    def test_supports_format_non_pdf(self):
        """Test that PDF writer doesn't support non-PDF files."""
        writer = PDFWriter()
        assert writer.supports_format("test.md") is False
        assert writer.supports_format("test.docx") is False
        assert writer.supports_format("test.txt") is False

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = PDFWriter.get_supported_extensions()
        assert extensions == ['.pdf']

    def test_to_string_document_summary(self, sample_document):
        """Test to_string returns document summary."""
        writer = PDFWriter()
        summary = writer.to_string(sample_document)

        assert "Title: Test Document" in summary
        assert "Elements:" in summary
        assert "heading:" in summary.lower()
        assert "paragraph:" in summary.lower()

    def test_to_string_invalid_input(self):
        """Test to_string with invalid input."""
        writer = PDFWriter()

        with pytest.raises(ValueError, match="Input must be a Document object"):
            writer.to_string("not a document")

    @patch('src.writers.pdf_writer.ParagraphStyle')
    @patch('src.writers.pdf_writer.SimpleDocTemplate')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    @patch('src.writers.pdf_writer.Paragraph')
    def test_create_pdf_document_with_title(self, mock_paragraph, mock_styles,
                                           mock_doc_template, mock_paragraph_style, sample_document):
        """Test creating PDF document with title."""
        mock_pdf_doc = Mock()
        mock_doc_template.return_value = mock_pdf_doc

        # Mock ParagraphStyle to return a mock style
        mock_paragraph_style.return_value = Mock()

        # Create properly configured style mocks with all required styles
        mock_title_style = Mock()
        mock_title_style.fontName = 'Helvetica-Bold'
        mock_normal_style = Mock()
        mock_normal_style.fontName = 'Helvetica'
        mock_code_style = Mock()
        mock_code_style.fontName = 'Courier'

        # Create all heading styles
        mock_styles_dict = {
            'Title': mock_title_style,
            'Normal': mock_normal_style,
            'Code': mock_code_style,
        }
        for level in range(1, 7):
            style = Mock()
            style.fontName = 'Helvetica-Bold'
            mock_styles_dict[f'Heading{level}'] = style

        mock_styles.return_value = mock_styles_dict

        writer = PDFWriter()
        output_path = Path("test.pdf")
        writer._create_pdf_document(sample_document, output_path)

        # Verify PDF document was built
        mock_pdf_doc.build.assert_called_once()

    @patch('src.writers.pdf_writer.SimpleDocTemplate')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    @patch('src.writers.pdf_writer.Paragraph')
    def test_create_pdf_document_without_title(self, mock_paragraph, mock_styles, mock_doc_template):
        """Test creating PDF document without title."""
        mock_pdf_doc = Mock()
        mock_doc_template.return_value = mock_pdf_doc

        # Create properly configured style mocks
        mock_normal_style = Mock()
        mock_normal_style.fontName = 'Helvetica'
        mock_styles_dict = {'Normal': mock_normal_style}
        mock_styles.return_value = mock_styles_dict

        document = Document()  # No title
        document.add_paragraph("Test paragraph")

        writer = PDFWriter()
        output_path = Path("test.pdf")
        writer._create_pdf_document(document, output_path)

        # Verify PDF document was built
        mock_pdf_doc.build.assert_called_once()

    @patch('src.writers.pdf_writer.Paragraph')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_convert_heading(self, mock_styles, mock_paragraph):
        """Test converting heading elements to PDF."""
        mock_styles_dict = {
            'Heading1': Mock(),
            'Heading2': Mock(),
            'Heading3': Mock(),
            'Heading4': Mock(),
            'Heading5': Mock(),
            'Heading6': Mock()
        }
        mock_styles.return_value = mock_styles_dict

        document = Document()
        heading = document.add_heading("Test Heading", level=2)

        writer = PDFWriter()
        result = writer._convert_heading(heading, mock_styles_dict)

        # Verify Paragraph was created with correct style
        mock_paragraph.assert_called_once_with("Test Heading", mock_styles_dict['Heading2'])

    @patch('src.writers.pdf_writer.Paragraph')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_convert_paragraph(self, mock_styles, mock_paragraph):
        """Test converting paragraph elements to PDF."""
        mock_styles_dict = {'Normal': Mock()}
        mock_styles.return_value = mock_styles_dict

        document = Document()
        para = document.add_paragraph("Test paragraph content")

        writer = PDFWriter()
        result = writer._convert_paragraph(para, mock_styles_dict)

        # Verify Paragraph was created
        mock_paragraph.assert_called_once_with("Test paragraph content", mock_styles_dict['Normal'])

    @patch('src.writers.pdf_writer.ListFlowable')
    @patch('src.writers.pdf_writer.ListItem')
    @patch('src.writers.pdf_writer.Paragraph')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_convert_unordered_list(self, mock_styles, mock_paragraph,
                                    mock_list_item, mock_list_flowable):
        """Test converting unordered list to PDF."""
        mock_styles_dict = {'Normal': Mock()}
        mock_styles.return_value = mock_styles_dict

        document = Document()
        list_elem = document.add_list(["Item 1", "Item 2"], ordered=False)

        writer = PDFWriter()
        result = writer._convert_list(list_elem, mock_styles_dict)

        # Verify ListFlowable was created
        mock_list_flowable.assert_called_once()
        call_args = mock_list_flowable.call_args
        assert call_args[1]['bulletType'] == 'bullet'

    @patch('src.writers.pdf_writer.ListFlowable')
    @patch('src.writers.pdf_writer.ListItem')
    @patch('src.writers.pdf_writer.Paragraph')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_convert_ordered_list(self, mock_styles, mock_paragraph,
                                  mock_list_item, mock_list_flowable):
        """Test converting ordered list to PDF."""
        mock_styles_dict = {'Normal': Mock()}
        mock_styles.return_value = mock_styles_dict

        document = Document()
        list_elem = document.add_list(["Item 1", "Item 2"], ordered=True)

        writer = PDFWriter()
        result = writer._convert_list(list_elem, mock_styles_dict)

        # Verify ListFlowable was created with number type
        mock_list_flowable.assert_called_once()
        call_args = mock_list_flowable.call_args
        assert call_args[1]['bulletType'] == 'number'

    @patch('src.writers.pdf_writer.Preformatted')
    @patch('src.writers.pdf_writer.ParagraphStyle')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_convert_code_block(self, mock_styles, mock_para_style, mock_preformatted):
        """Test converting code block to PDF."""
        mock_styles_dict = {'Code': Mock()}
        mock_styles.return_value = mock_styles_dict

        document = Document()
        code = document.add_code_block("print('hello')", language="python")

        writer = PDFWriter()
        result = writer._convert_code_block(code, mock_styles_dict)

        # Verify Preformatted was created
        mock_preformatted.assert_called_once()
        assert "print('hello')" in str(mock_preformatted.call_args)

    @patch('src.writers.pdf_writer.ParagraphStyle')
    @patch('src.writers.pdf_writer.SimpleDocTemplate')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    @patch('src.writers.pdf_writer.Paragraph')
    def test_write_to_file(self, mock_paragraph, mock_styles, mock_doc_template, mock_paragraph_style, sample_document, temp_dir):
        """Test writing document to file."""
        mock_pdf_doc = Mock()
        mock_doc_template.return_value = mock_pdf_doc

        # Mock ParagraphStyle to return a mock style
        mock_paragraph_style.return_value = Mock()

        # Create properly configured style mocks with all required styles
        mock_title_style = Mock()
        mock_title_style.fontName = 'Helvetica-Bold'
        mock_normal_style = Mock()
        mock_normal_style.fontName = 'Helvetica'
        mock_code_style = Mock()
        mock_code_style.fontName = 'Courier'

        # Create all heading styles
        mock_styles_dict = {
            'Title': mock_title_style,
            'Normal': mock_normal_style,
            'Code': mock_code_style,
        }
        for level in range(1, 7):
            style = Mock()
            style.fontName = 'Helvetica-Bold'
            mock_styles_dict[f'Heading{level}'] = style

        mock_styles.return_value = mock_styles_dict

        writer = PDFWriter()
        output_file = temp_dir / "output.pdf"

        writer.write(sample_document, output_file)

        # Verify SimpleDocTemplate was created with output path
        mock_doc_template.assert_called_once()
        assert str(output_file) in str(mock_doc_template.call_args)

        # Verify PDF was built
        mock_pdf_doc.build.assert_called_once()

    def test_write_unsupported_format(self, sample_document, temp_dir):
        """Test writing to unsupported format."""
        writer = PDFWriter()
        output_file = temp_dir / "output.md"

        with pytest.raises(ValueError, match="Unsupported output format"):
            writer.write(sample_document, output_file)

    @patch('src.writers.pdf_writer.SimpleDocTemplate')
    def test_write_io_error(self, mock_doc_template, sample_document, temp_dir):
        """Test handling IO errors during write."""
        mock_pdf_doc = Mock()
        mock_pdf_doc.build.side_effect = Exception("Build failed")
        mock_doc_template.return_value = mock_pdf_doc

        writer = PDFWriter()
        output_file = temp_dir / "output.pdf"

        with pytest.raises(IOError, match="Error writing to file"):
            writer.write(sample_document, output_file)

    @patch('src.writers.pdf_writer.SimpleDocTemplate')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_empty_document(self, mock_styles, mock_doc_template):
        """Test handling empty document."""
        mock_pdf_doc = Mock()
        mock_doc_template.return_value = mock_pdf_doc
        mock_styles.return_value = {}

        document = Document()  # Empty document

        writer = PDFWriter()
        output_path = Path("test.pdf")
        writer._create_pdf_document(document, output_path)

        # Should not crash with empty document
        mock_pdf_doc.build.assert_called_once()

    @patch('src.writers.pdf_writer.Paragraph')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_unknown_element_type(self, mock_styles, mock_paragraph):
        """Test handling unknown element types."""
        mock_styles_dict = {'Normal': Mock()}
        mock_styles.return_value = mock_styles_dict

        # Create a custom element with unknown type
        from src.core.document import DocumentElement

        class UnknownElement(DocumentElement):
            def __post_init__(self):
                self.element_type = "unknown_type"
                self.content = "Unknown content"

        unknown_element = UnknownElement()

        writer = PDFWriter()
        result = writer._convert_element_to_flowable(unknown_element, mock_styles_dict)

        # Should fall back to creating a Paragraph
        mock_paragraph.assert_called_once_with("Unknown content", mock_styles_dict['Normal'])

    def test_list_without_items(self):
        """Test handling list elements without items."""
        writer = PDFWriter()

        # Create a mock list element without items
        class MockDocumentList:
            def __init__(self):
                self.element_type = ElementType.LIST
                self.attributes = {"ordered": False}

        mock_styles_dict = {'Normal': Mock()}
        mock_list = MockDocumentList()

        # Should return None when list has no items
        result = writer._convert_list(mock_list, mock_styles_dict)
        assert result is None

    @patch('src.writers.pdf_writer.SimpleDocTemplate')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    @patch('src.writers.pdf_writer.Paragraph')
    def test_element_with_no_content(self, mock_paragraph, mock_styles, mock_doc_template):
        """Test handling elements with no content."""
        mock_pdf_doc = Mock()
        mock_doc_template.return_value = mock_pdf_doc
        mock_styles_dict = {'Normal': Mock()}
        mock_styles.return_value = mock_styles_dict

        # Create element with empty content
        from src.core.document import Paragraph as DocParagraph

        element = DocParagraph(content="")

        writer = PDFWriter()
        result = writer._convert_element_to_flowable(element, mock_styles_dict)

        # Should still create a Paragraph even with empty content
        assert result is not None

    @patch('src.writers.pdf_writer.Paragraph')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_heading_level_mapping(self, mock_styles, mock_paragraph):
        """Test that heading levels map correctly to PDF styles."""
        mock_styles_dict = {
            'Heading1': Mock(),
            'Heading2': Mock(),
            'Heading3': Mock(),
            'Heading4': Mock(),
            'Heading5': Mock(),
            'Heading6': Mock()
        }
        mock_styles.return_value = mock_styles_dict

        writer = PDFWriter()

        # Test each heading level
        for level in range(1, 7):
            document = Document()
            heading = document.add_heading(f"Heading {level}", level=level)

            result = writer._convert_heading(heading, mock_styles_dict)

            # Verify correct style was used
            expected_style = mock_styles_dict[f'Heading{level}']
            mock_paragraph.assert_called_with(f"Heading {level}", expected_style)

    @patch('src.writers.pdf_writer.Paragraph')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    def test_heading_level_fallback(self, mock_styles, mock_paragraph):
        """Test heading level fallback for levels beyond 6."""
        mock_styles_dict = {
            'Heading1': Mock(),
            'Heading2': Mock(),
            'Heading3': Mock(),
            'Heading4': Mock(),
            'Heading5': Mock(),
            'Heading6': Mock()
        }
        mock_styles.return_value = mock_styles_dict

        writer = PDFWriter()

        # Create a mock heading with level 10 (beyond standard)
        class MockHeading:
            def __init__(self):
                self.attributes = {"level": 10}
                self.content = "Deep Heading"
                self.element_type = ElementType.HEADING

        heading = MockHeading()
        result = writer._convert_heading(heading, mock_styles_dict)

        # Should fall back to Heading6
        mock_paragraph.assert_called_with("Deep Heading", mock_styles_dict['Heading6'])

    @patch('src.writers.pdf_writer.SimpleDocTemplate')
    @patch('src.writers.pdf_writer.getSampleStyleSheet')
    @patch('src.writers.pdf_writer.Spacer')
    @patch('src.writers.pdf_writer.Paragraph')
    def test_spacing_between_elements(self, mock_paragraph, mock_spacer, mock_styles, mock_doc_template):
        """Test that spacing is added between elements."""
        mock_pdf_doc = Mock()
        mock_doc_template.return_value = mock_pdf_doc

        # Create properly configured style mocks
        mock_normal_style = Mock()
        mock_normal_style.fontName = 'Helvetica'
        mock_styles.return_value = {'Normal': mock_normal_style}

        document = Document()
        document.add_paragraph("Paragraph 1")
        document.add_paragraph("Paragraph 2")

        writer = PDFWriter()
        output_path = Path("test.pdf")
        writer._create_pdf_document(document, output_path)

        # Verify Spacer was called (at least once for spacing between elements)
        assert mock_spacer.call_count >= 1
