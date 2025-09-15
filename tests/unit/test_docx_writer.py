"""
Unit tests for DOCX writer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.writers.docx_writer import DocxWriter
from src.core.document import Document, ElementType


class TestDocxWriter:
    """Test DocxWriter functionality."""

    def test_supports_format_docx(self):
        """Test that DOCX writer supports .docx files."""
        writer = DocxWriter()
        assert writer.supports_format("test.docx") is True
        assert writer.supports_format("test.DOCX") is True

    def test_supports_format_non_docx(self):
        """Test that DOCX writer doesn't support non-DOCX files."""
        writer = DocxWriter()
        assert writer.supports_format("test.md") is False
        assert writer.supports_format("test.pdf") is False
        assert writer.supports_format("test.txt") is False

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = DocxWriter.get_supported_extensions()
        assert extensions == ['.docx']

    def test_to_string_document_summary(self, sample_document):
        """Test to_string returns document summary."""
        writer = DocxWriter()
        summary = writer.to_string(sample_document)

        assert "Title: Test Document" in summary
        assert "Elements:" in summary
        assert "heading:" in summary.lower()
        assert "paragraph:" in summary.lower()

    def test_to_string_invalid_input(self):
        """Test to_string with invalid input."""
        writer = DocxWriter()

        with pytest.raises(ValueError, match="Input must be a Document object"):
            writer.to_string("not a document")

    @patch('src.writers.docx_writer.DocxDocument')
    def test_create_docx_document_with_title(self, mock_docx_class, sample_document):
        """Test creating DOCX document with title."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        writer = DocxWriter()
        result = writer._create_docx_document(sample_document)

        assert result == mock_docx_doc
        # Verify title was added
        mock_docx_doc.add_heading.assert_called()

    @patch('src.writers.docx_writer.DocxDocument')
    def test_create_docx_document_without_title(self, mock_docx_class):
        """Test creating DOCX document without title."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        document = Document()  # No title
        document.add_paragraph("Test paragraph")

        writer = DocxWriter()
        result = writer._create_docx_document(document)

        assert result == mock_docx_doc

    @patch('src.writers.docx_writer.DocxDocument')
    def test_add_heading_to_docx(self, mock_docx_class):
        """Test adding heading elements to DOCX."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        document = Document()
        document.add_heading("Test Heading", level=2)

        writer = DocxWriter()
        writer._create_docx_document(document)

        # Should call add_heading for both title and content heading
        mock_docx_doc.add_heading.assert_called()

    @patch('src.writers.docx_writer.DocxDocument')
    def test_add_paragraph_to_docx(self, mock_docx_class):
        """Test adding paragraph elements to DOCX."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        document = Document()
        document.add_paragraph("Test paragraph content")

        writer = DocxWriter()
        writer._create_docx_document(document)

        mock_docx_doc.add_paragraph.assert_called_with("Test paragraph content")

    @patch('src.writers.docx_writer.DocxDocument')
    @patch('src.writers.docx_writer.Inches')
    def test_add_list_to_docx(self, mock_inches, mock_docx_class):
        """Test adding list elements to DOCX."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        mock_para = Mock()
        mock_docx_doc.add_paragraph.return_value = mock_para

        document = Document()
        document.add_list(["Item 1", "Item 2"], ordered=False)

        writer = DocxWriter()
        writer._create_docx_document(document)

        # Should add paragraphs for list items
        assert mock_docx_doc.add_paragraph.call_count >= 2

    @patch('src.writers.docx_writer.DocxDocument')
    def test_add_code_block_to_docx(self, mock_docx_class):
        """Test adding code block elements to DOCX."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        mock_para = Mock()
        mock_run = Mock()
        mock_para.add_run.return_value = mock_run
        mock_docx_doc.add_paragraph.return_value = mock_para

        document = Document()
        document.add_code_block("print('hello')", language="python")

        writer = DocxWriter()
        writer._create_docx_document(document)

        mock_docx_doc.add_paragraph.assert_called()
        mock_para.add_run.assert_called_with("print('hello')")

    def test_heading_level_limits(self):
        """Test that heading levels are limited to valid Word range."""
        writer = DocxWriter()

        # Test with mock heading elements
        class MockHeading:
            def __init__(self, level):
                self.attributes = {"level": level}
                self.content = "Test"

        mock_docx_doc = Mock()

        # Test level too high
        heading = MockHeading(15)  # Beyond Word's limit
        writer._add_heading_to_docx(heading, mock_docx_doc)
        mock_docx_doc.add_heading.assert_called_with("Test", level=9)

        # Test level too low
        heading = MockHeading(0)
        writer._add_heading_to_docx(heading, mock_docx_doc)
        mock_docx_doc.add_heading.assert_called_with("Test", level=1)

        # Test normal level
        heading = MockHeading(3)
        writer._add_heading_to_docx(heading, mock_docx_doc)
        mock_docx_doc.add_heading.assert_called_with("Test", level=3)

    @patch('src.writers.docx_writer.DocxDocument')
    def test_write_to_file(self, mock_docx_class, sample_document, temp_dir):
        """Test writing document to file."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        writer = DocxWriter()
        output_file = temp_dir / "output.docx"

        writer.write(sample_document, output_file)

        mock_docx_doc.save.assert_called_once_with(output_file)

    def test_write_unsupported_format(self, sample_document, temp_dir):
        """Test writing to unsupported format."""
        writer = DocxWriter()
        output_file = temp_dir / "output.md"

        with pytest.raises(ValueError, match="Unsupported output format"):
            writer.write(sample_document, output_file)

    @patch('src.writers.docx_writer.DocxDocument')
    def test_write_io_error(self, mock_docx_class, sample_document, temp_dir):
        """Test handling IO errors during write."""
        mock_docx_doc = Mock()
        mock_docx_doc.save.side_effect = IOError("Write failed")
        mock_docx_class.return_value = mock_docx_doc

        writer = DocxWriter()
        output_file = temp_dir / "output.docx"

        with pytest.raises(IOError, match="Error writing to file"):
            writer.write(sample_document, output_file)

    @patch('src.writers.docx_writer.DocxDocument')
    def test_empty_document(self, mock_docx_class):
        """Test handling empty document."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        document = Document()  # Empty document

        writer = DocxWriter()
        result = writer._create_docx_document(document)

        assert result == mock_docx_doc
        # Should not crash with empty document

    @patch('src.writers.docx_writer.DocxDocument')
    def test_unknown_element_type(self, mock_docx_class):
        """Test handling unknown element types."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        # Create a custom element with unknown type
        from src.core.document import DocumentElement, ElementType

        class UnknownElement(DocumentElement):
            def __post_init__(self):
                self.element_type = "unknown_type"
                self.content = "Unknown content"

        document = Document()
        unknown_element = UnknownElement()
        document.add_element(unknown_element)

        writer = DocxWriter()
        writer._create_docx_document(document)

        # Should fall back to adding as paragraph
        mock_docx_doc.add_paragraph.assert_called_with("Unknown content")

    def test_list_without_items(self):
        """Test handling list elements without items."""
        writer = DocxWriter()

        # Create a mock list element without items
        class MockDocumentList:
            def __init__(self):
                self.element_type = ElementType.LIST
                self.attributes = {"ordered": False}

        mock_docx_doc = Mock()
        mock_list = MockDocumentList()

        # Should not crash when list has no items
        writer._add_list_to_docx(mock_list, mock_docx_doc)

        # Should not call add_paragraph for empty list
        mock_docx_doc.add_paragraph.assert_not_called()

    @patch('src.writers.docx_writer.DocxDocument')
    @patch('src.writers.docx_writer.Inches')
    def test_ordered_vs_unordered_lists(self, mock_inches, mock_docx_class):
        """Test different bullet styles for ordered vs unordered lists."""
        mock_docx_doc = Mock()
        mock_docx_class.return_value = mock_docx_doc

        mock_para = Mock()
        mock_run = Mock()
        mock_para.add_run.return_value = mock_run
        mock_docx_doc.add_paragraph.return_value = mock_para

        document = Document()

        # Add unordered list
        document.add_list(["Item 1"], ordered=False)

        # Add ordered list
        document.add_list(["Item 1"], ordered=True)

        writer = DocxWriter()
        writer._create_docx_document(document)

        # Should have called add_run with different bullet styles
        calls = mock_para.add_run.call_args_list
        assert len(calls) >= 2

        # Check that different bullet styles were used
        bullet_calls = [call[0][0] for call in calls]
        assert any("•" in call for call in bullet_calls)  # Unordered
        assert any("1." in call for call in bullet_calls)  # Ordered