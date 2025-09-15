"""
Unit tests for the Document model.
"""

import pytest
from src.core.document import (
    Document, ElementType, Heading, Paragraph, List, ListItem,
    CodeBlock, InlineCode, Bold, Italic, Link, Image
)


class TestDocumentElements:
    """Test individual document elements."""

    def test_heading_creation(self):
        """Test heading element creation."""
        heading = Heading(content="Test Heading", level=2)
        assert heading.element_type == ElementType.HEADING
        assert heading.content == "Test Heading"
        assert heading.level == 2
        assert heading.attributes["level"] == 2

    def test_paragraph_creation(self):
        """Test paragraph element creation."""
        paragraph = Paragraph(content="Test paragraph content.")
        assert paragraph.element_type == ElementType.PARAGRAPH
        assert paragraph.content == "Test paragraph content."

    def test_list_creation(self):
        """Test list element creation."""
        list_element = List(ordered=True)
        assert list_element.element_type == ElementType.LIST
        assert list_element.ordered is True
        assert list_element.attributes["ordered"] is True
        assert len(list_element.items) == 0

    def test_list_item_creation(self):
        """Test list item element creation."""
        list_item = ListItem(content="Test item")
        assert list_item.element_type == ElementType.LIST_ITEM
        assert list_item.content == "Test item"

    def test_code_block_creation(self):
        """Test code block element creation."""
        code_block = CodeBlock(content="print('hello')", language="python")
        assert code_block.element_type == ElementType.CODE_BLOCK
        assert code_block.content == "print('hello')"
        assert code_block.language == "python"
        assert code_block.attributes["language"] == "python"

    def test_code_block_without_language(self):
        """Test code block without language specification."""
        code_block = CodeBlock(content="some code")
        assert code_block.element_type == ElementType.CODE_BLOCK
        assert code_block.content == "some code"
        assert code_block.language is None
        assert "language" not in code_block.attributes

    def test_inline_code_creation(self):
        """Test inline code element creation."""
        inline_code = InlineCode(content="code")
        assert inline_code.element_type == ElementType.INLINE_CODE
        assert inline_code.content == "code"

    def test_bold_creation(self):
        """Test bold text element creation."""
        bold = Bold(content="bold text")
        assert bold.element_type == ElementType.BOLD
        assert bold.content == "bold text"

    def test_italic_creation(self):
        """Test italic text element creation."""
        italic = Italic(content="italic text")
        assert italic.element_type == ElementType.ITALIC
        assert italic.content == "italic text"

    def test_link_creation(self):
        """Test link element creation."""
        link = Link(content="Link Text", url="https://example.com", title="Example")
        assert link.element_type == ElementType.LINK
        assert link.content == "Link Text"
        assert link.url == "https://example.com"
        assert link.title == "Example"
        assert link.attributes["url"] == "https://example.com"
        assert link.attributes["title"] == "Example"

    def test_image_creation(self):
        """Test image element creation."""
        image = Image(
            content="Alt text",
            url="https://example.com/image.jpg",
            alt_text="Alternative text",
            title="Image title"
        )
        assert image.element_type == ElementType.IMAGE
        assert image.content == "Alt text"
        assert image.url == "https://example.com/image.jpg"
        assert image.alt_text == "Alternative text"
        assert image.title == "Image title"
        assert image.attributes["url"] == "https://example.com/image.jpg"
        assert image.attributes["alt_text"] == "Alternative text"
        assert image.attributes["title"] == "Image title"


class TestDocument:
    """Test Document class functionality."""

    def test_document_creation(self):
        """Test document creation."""
        doc = Document(title="Test Document")
        assert doc.title == "Test Document"
        assert len(doc.elements) == 0
        assert len(doc.metadata) == 0

    def test_document_creation_without_title(self):
        """Test document creation without title."""
        doc = Document()
        assert doc.title is None
        assert len(doc.elements) == 0

    def test_add_element(self):
        """Test adding elements to document."""
        doc = Document()
        heading = Heading(content="Test", level=1)
        doc.add_element(heading)
        assert len(doc.elements) == 1
        assert doc.elements[0] == heading

    def test_add_heading(self):
        """Test add_heading convenience method."""
        doc = Document()
        heading = doc.add_heading("Test Heading", level=2)
        assert len(doc.elements) == 1
        assert isinstance(heading, Heading)
        assert heading.content == "Test Heading"
        assert heading.level == 2
        assert doc.elements[0] == heading

    def test_add_paragraph(self):
        """Test add_paragraph convenience method."""
        doc = Document()
        paragraph = doc.add_paragraph("Test paragraph")
        assert len(doc.elements) == 1
        assert isinstance(paragraph, Paragraph)
        assert paragraph.content == "Test paragraph"
        assert doc.elements[0] == paragraph

    def test_add_list(self):
        """Test add_list convenience method."""
        doc = Document()
        list_element = doc.add_list(["Item 1", "Item 2"], ordered=True)
        assert len(doc.elements) == 1
        assert isinstance(list_element, List)
        assert list_element.ordered is True
        assert len(list_element.items) == 2
        assert list_element.items[0].content == "Item 1"
        assert list_element.items[1].content == "Item 2"

    def test_add_code_block(self):
        """Test add_code_block convenience method."""
        doc = Document()
        code_block = doc.add_code_block("print('hello')", language="python")
        assert len(doc.elements) == 1
        assert isinstance(code_block, CodeBlock)
        assert code_block.content == "print('hello')"
        assert code_block.language == "python"

    def test_get_elements_by_type(self):
        """Test getting elements by type."""
        doc = Document()
        doc.add_heading("Heading 1", level=1)
        doc.add_paragraph("Paragraph 1")
        doc.add_heading("Heading 2", level=2)
        doc.add_paragraph("Paragraph 2")

        headings = doc.get_elements_by_type(ElementType.HEADING)
        paragraphs = doc.get_elements_by_type(ElementType.PARAGRAPH)

        assert len(headings) == 2
        assert len(paragraphs) == 2
        assert all(h.element_type == ElementType.HEADING for h in headings)
        assert all(p.element_type == ElementType.PARAGRAPH for p in paragraphs)

    def test_get_headings(self):
        """Test get_headings convenience method."""
        doc = Document()
        doc.add_heading("Heading 1", level=1)
        doc.add_paragraph("Paragraph")
        doc.add_heading("Heading 2", level=2)

        headings = doc.get_headings()
        assert len(headings) == 2
        assert headings[0].content == "Heading 1"
        assert headings[1].content == "Heading 2"

    def test_get_text_content(self):
        """Test getting all text content."""
        doc = Document()
        doc.add_heading("Heading")
        doc.add_paragraph("Paragraph")
        doc.add_code_block("code")

        text = doc.get_text_content()
        assert "Heading" in text
        assert "Paragraph" in text
        assert "code" in text

    def test_document_len(self):
        """Test document length."""
        doc = Document()
        assert len(doc) == 0

        doc.add_heading("Heading")
        assert len(doc) == 1

        doc.add_paragraph("Paragraph")
        assert len(doc) == 2

    def test_document_iteration(self):
        """Test document iteration."""
        doc = Document()
        doc.add_heading("Heading")
        doc.add_paragraph("Paragraph")

        elements = list(doc)
        assert len(elements) == 2
        assert elements[0].content == "Heading"
        assert elements[1].content == "Paragraph"

    def test_document_with_sample_data(self, sample_document):
        """Test document with sample fixture data."""
        assert sample_document.title == "Test Document"
        assert len(sample_document) > 0

        headings = sample_document.get_headings()
        assert len(headings) >= 2

        text_content = sample_document.get_text_content()
        assert "Chapter 1" in text_content
        assert "This is a paragraph" in text_content