"""
Unit tests for PDF reader.
"""

import pytest
from unittest.mock import Mock, patch

from src.readers.pdf_reader import PDFReader
from src.core.document import Document, ElementType


class TestPDFReader:
    """Test PDFReader functionality."""

    def test_supports_format_pdf(self):
        """Test that PDF reader supports .pdf files."""
        reader = PDFReader()
        assert reader.supports_format("test.pdf") is True
        assert reader.supports_format("test.PDF") is True

    def test_supports_format_non_pdf(self):
        """Test that PDF reader doesn't support non-PDF files."""
        reader = PDFReader()
        assert reader.supports_format("test.md") is False
        assert reader.supports_format("test.docx") is False
        assert reader.supports_format("test.txt") is False

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = PDFReader.get_supported_extensions()
        assert extensions == ['.pdf']

    @patch('src.readers.pdf_reader.fitz')
    def test_read_nonexistent_file(self, mock_fitz):
        """Test reading a file that doesn't exist."""
        reader = PDFReader()

        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            reader.read("/nonexistent/file.pdf")

    def test_read_unsupported_format(self, temp_dir):
        """Test reading a file with unsupported format."""
        reader = PDFReader()
        unsupported_file = temp_dir / "test.txt"
        unsupported_file.write_text("test content")

        with pytest.raises(ValueError, match="Unsupported file format"):
            reader.read(unsupported_file)

    @patch('src.readers.pdf_reader.fitz')
    def test_read_pdf_success(self, mock_fitz, temp_dir, sample_pdf_content):
        """Test successfully reading a PDF file."""
        # Create a test PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("fake pdf content")  # Just for file existence

        # Mock PyMuPDF
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = sample_pdf_content
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc

        reader = PDFReader()
        document = reader.read(pdf_file)

        assert isinstance(document, Document)
        assert document.title == "test"
        assert len(document.elements) > 0

        # Verify mock was called correctly
        mock_fitz.open.assert_called_once_with(pdf_file)
        mock_doc.close.assert_called_once()

    @patch('src.readers.pdf_reader.fitz')
    def test_read_pdf_exception(self, mock_fitz, temp_dir):
        """Test handling exceptions during PDF processing."""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("fake pdf content")

        mock_fitz.open.side_effect = Exception("PDF processing error")

        reader = PDFReader()
        with pytest.raises(Exception, match="Error processing PDF"):
            reader.read(pdf_file)

    def test_is_heading_detection(self):
        """Test heading detection logic."""
        reader = PDFReader()

        # Test uppercase headings
        assert reader._is_heading("CHAPTER ONE") is True

        # Test numbered headings
        assert reader._is_heading("1. Introduction") is True
        assert reader._is_heading("2.1 Overview") is True

        # Test capitalized headings
        assert reader._is_heading("Introduction") is True

        # Test non-headings
        assert reader._is_heading("This is a regular paragraph.") is False
        long_text = ("This is a very long line that should not be "
                     "considered a heading because it exceeds the length limit.")
        assert reader._is_heading(long_text) is False

    def test_determine_heading_level(self):
        """Test heading level determination."""
        reader = PDFReader()

        # Numbered headings should be level 2
        assert reader._determine_heading_level("1. Introduction") == 2
        assert reader._determine_heading_level("2.1 Overview") == 2

        # All caps should be level 1
        assert reader._determine_heading_level("CHAPTER ONE") == 1

        # Other headings should be level 2
        assert reader._determine_heading_level("Introduction") == 2

    def test_format_heading_text(self):
        """Test heading text formatting."""
        reader = PDFReader()

        # All caps should be title-cased
        assert reader._format_heading_text("CHAPTER ONE") == "Chapter One"

        # Other text should remain unchanged
        assert reader._format_heading_text("Introduction") == "Introduction"
        assert reader._format_heading_text("1. Overview") == "1. Overview"

    def test_clean_text(self):
        """Test text cleaning functionality."""
        reader = PDFReader()

        # Test whitespace normalization
        assert reader._clean_text("  multiple   spaces  ") == "multiple spaces"

        # Test punctuation spacing
        assert reader._clean_text("Hello.World") == "Hello. World"
        assert reader._clean_text("End!Next") == "End! Next"
        assert reader._clean_text("Question?Answer") == "Question? Answer"

    @patch('src.readers.pdf_reader.fitz')
    def test_process_page_text(self, mock_fitz, temp_dir):
        """Test processing of page text."""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("fake pdf content")

        # Test text with headings and paragraphs
        test_text = """MAIN HEADING

1. Section One

This is a paragraph.

ANOTHER HEADING

Another paragraph here."""

        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = test_text
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc

        reader = PDFReader()
        document = reader.read(pdf_file)

        # Check that we have both headings and paragraphs
        headings = document.get_elements_by_type(ElementType.HEADING)
        paragraphs = document.get_elements_by_type(ElementType.PARAGRAPH)

        assert len(headings) >= 2
        assert len(paragraphs) >= 2

        # Check heading levels
        heading_contents = [h.content for h in headings]
        assert "Main Heading" in heading_contents  # Should be title-cased
        assert "1. Section One" in heading_contents

    @patch('src.readers.pdf_reader.fitz')
    def test_empty_pdf_pages(self, mock_fitz, temp_dir):
        """Test handling of empty PDF pages."""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("fake pdf content")

        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = ""  # Empty page
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc

        reader = PDFReader()
        document = reader.read(pdf_file)

        assert isinstance(document, Document)
        assert len(document.elements) == 0  # No content should be added

    @patch('src.readers.pdf_reader.fitz')
    def test_multiple_pages(self, mock_fitz, temp_dir):
        """Test processing multiple PDF pages."""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("fake pdf content")

        # Create mock pages
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Page 1 content\nFirst paragraph."

        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Page 2 content\nSecond paragraph."

        mock_doc = Mock()
        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_fitz.open.return_value = mock_doc

        reader = PDFReader()
        document = reader.read(pdf_file)

        assert len(document.elements) == 4  # 2 paragraphs per page

        # Verify content from both pages is present
        text_content = document.get_text_content()
        assert "Page 1 content" in text_content
        assert "Page 2 content" in text_content