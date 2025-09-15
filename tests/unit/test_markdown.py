"""
Unit tests for Markdown reader and writer.
"""

import pytest
from pathlib import Path

from src.readers.markdown_reader import MarkdownReader
from src.writers.markdown_writer import MarkdownWriter
from src.core.document import Document, ElementType


class TestMarkdownReader:
    """Test MarkdownReader functionality."""

    def test_supports_format_markdown(self):
        """Test that Markdown reader supports markdown files."""
        reader = MarkdownReader()
        assert reader.supports_format("test.md") is True
        assert reader.supports_format("test.markdown") is True
        assert reader.supports_format("test.MD") is True

    def test_supports_format_non_markdown(self):
        """Test that Markdown reader doesn't support non-markdown files."""
        reader = MarkdownReader()
        assert reader.supports_format("test.pdf") is False
        assert reader.supports_format("test.docx") is False
        assert reader.supports_format("test.txt") is False

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = MarkdownReader.get_supported_extensions()
        assert '.md' in extensions
        assert '.markdown' in extensions

    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        reader = MarkdownReader()

        with pytest.raises(FileNotFoundError, match="Markdown file not found"):
            reader.read("/nonexistent/file.md")

    def test_read_unsupported_format(self, temp_dir):
        """Test reading a file with unsupported format."""
        reader = MarkdownReader()
        unsupported_file = temp_dir / "test.txt"
        unsupported_file.write_text("test content")

        with pytest.raises(ValueError, match="Unsupported file format"):
            reader.read(unsupported_file)

    def test_read_markdown_file(self, sample_markdown_file):
        """Test reading a markdown file."""
        reader = MarkdownReader()
        document = reader.read(sample_markdown_file)

        assert isinstance(document, Document)
        assert document.title == "sample"
        assert len(document.elements) > 0

        # Check for headings
        headings = document.get_elements_by_type(ElementType.HEADING)
        assert len(headings) >= 3

        # Check for paragraphs
        paragraphs = document.get_elements_by_type(ElementType.PARAGRAPH)
        assert len(paragraphs) >= 3

        # Check for lists
        lists = document.get_elements_by_type(ElementType.LIST)
        assert len(lists) >= 1

        # Check for code blocks
        code_blocks = document.get_elements_by_type(ElementType.CODE_BLOCK)
        assert len(code_blocks) >= 1

    def test_parse_headings(self, temp_dir):
        """Test parsing different heading levels."""
        content = """# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
"""
        markdown_file = temp_dir / "headings.md"
        markdown_file.write_text(content)

        reader = MarkdownReader()
        document = reader.read(markdown_file)

        headings = document.get_elements_by_type(ElementType.HEADING)
        assert len(headings) == 6

        # Check heading levels
        assert headings[0].attributes["level"] == 1
        assert headings[1].attributes["level"] == 2
        assert headings[2].attributes["level"] == 3
        assert headings[3].attributes["level"] == 4
        assert headings[4].attributes["level"] == 5
        assert headings[5].attributes["level"] == 6

        # Check heading content
        assert headings[0].content == "Heading 1"
        assert headings[5].content == "Heading 6"

    def test_parse_code_blocks(self, temp_dir):
        """Test parsing code blocks with and without language."""
        content = """```python
print("Hello World")
```

```
plain code block
```

```javascript
console.log("Hello");
```
"""
        markdown_file = temp_dir / "code.md"
        markdown_file.write_text(content)

        reader = MarkdownReader()
        document = reader.read(markdown_file)

        code_blocks = document.get_elements_by_type(ElementType.CODE_BLOCK)
        assert len(code_blocks) == 3

        # Check languages
        assert code_blocks[0].attributes.get("language") == "python"
        assert code_blocks[1].attributes.get("language") is None
        assert code_blocks[2].attributes.get("language") == "javascript"

        # Check content
        assert 'print("Hello World")' in code_blocks[0].content
        assert "plain code block" in code_blocks[1].content
        assert 'console.log("Hello");' in code_blocks[2].content

    def test_parse_lists(self, temp_dir):
        """Test parsing ordered and unordered lists."""
        content = """- Item 1
- Item 2
- Item 3

1. Ordered item 1
2. Ordered item 2

* Alternative bullet
+ Another bullet
"""
        markdown_file = temp_dir / "lists.md"
        markdown_file.write_text(content)

        reader = MarkdownReader()
        document = reader.read(markdown_file)

        lists = document.get_elements_by_type(ElementType.LIST)
        assert len(lists) >= 5  # Each list item is treated separately in simple implementation

    def test_parse_paragraphs(self, temp_dir):
        """Test parsing paragraphs."""
        content = """First paragraph with some text.

Second paragraph after empty line.

Third paragraph
with wrapped text
on multiple lines.
"""
        markdown_file = temp_dir / "paragraphs.md"
        markdown_file.write_text(content)

        reader = MarkdownReader()
        document = reader.read(markdown_file)

        paragraphs = document.get_elements_by_type(ElementType.PARAGRAPH)
        assert len(paragraphs) == 3

        assert "First paragraph" in paragraphs[0].content
        assert "Second paragraph" in paragraphs[1].content
        assert "Third paragraph" in paragraphs[2].content

    def test_empty_markdown_file(self, temp_dir):
        """Test handling empty markdown file."""
        markdown_file = temp_dir / "empty.md"
        markdown_file.write_text("")

        reader = MarkdownReader()
        document = reader.read(markdown_file)

        assert isinstance(document, Document)
        assert len(document.elements) == 0


class TestMarkdownWriter:
    """Test MarkdownWriter functionality."""

    def test_supports_format_markdown(self):
        """Test that Markdown writer supports markdown files."""
        writer = MarkdownWriter()
        assert writer.supports_format("test.md") is True
        assert writer.supports_format("test.markdown") is True
        assert writer.supports_format("test.MD") is True

    def test_supports_format_non_markdown(self):
        """Test that Markdown writer doesn't support non-markdown files."""
        writer = MarkdownWriter()
        assert writer.supports_format("test.pdf") is False
        assert writer.supports_format("test.docx") is False
        assert writer.supports_format("test.txt") is False

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = MarkdownWriter.get_supported_extensions()
        assert '.md' in extensions
        assert '.markdown' in extensions

    def test_to_string_with_title(self, sample_document):
        """Test converting document to string with title."""
        writer = MarkdownWriter()
        markdown_text = writer.to_string(sample_document)

        assert "# Test Document" in markdown_text
        assert "## Chapter 1" in markdown_text
        assert "This is a paragraph" in markdown_text

    def test_to_string_without_title(self):
        """Test converting document to string without title."""
        document = Document()  # No title
        document.add_heading("Heading", level=1)
        document.add_paragraph("Paragraph")

        writer = MarkdownWriter()
        markdown_text = writer.to_string(document)

        assert "# Heading" in markdown_text
        assert "Paragraph" in markdown_text
        # Should not have a title line
        assert not markdown_text.startswith("# \n")

    def test_convert_headings(self):
        """Test converting heading elements."""
        writer = MarkdownWriter()
        document = Document()
        document.add_heading("Level 1", level=1)
        document.add_heading("Level 2", level=2)
        document.add_heading("Level 3", level=3)

        markdown_text = writer.to_string(document)

        assert "# Level 1" in markdown_text
        assert "## Level 2" in markdown_text
        assert "### Level 3" in markdown_text

    def test_convert_paragraphs(self):
        """Test converting paragraph elements."""
        writer = MarkdownWriter()
        document = Document()
        document.add_paragraph("First paragraph.")
        document.add_paragraph("Second paragraph.")

        markdown_text = writer.to_string(document)

        assert "First paragraph." in markdown_text
        assert "Second paragraph." in markdown_text

    def test_convert_lists(self):
        """Test converting list elements."""
        writer = MarkdownWriter()
        document = Document()

        # Unordered list
        document.add_list(["Item 1", "Item 2", "Item 3"], ordered=False)

        # Ordered list
        document.add_list(["First", "Second", "Third"], ordered=True)

        markdown_text = writer.to_string(document)

        # Check unordered list
        assert "- Item 1" in markdown_text
        assert "- Item 2" in markdown_text
        assert "- Item 3" in markdown_text

        # Check ordered list
        assert "1. First" in markdown_text
        assert "2. Second" in markdown_text
        assert "3. Third" in markdown_text

    def test_convert_code_blocks(self):
        """Test converting code block elements."""
        writer = MarkdownWriter()
        document = Document()

        # Code block with language
        document.add_code_block('print("Hello")', language="python")

        # Code block without language
        document.add_code_block("plain code")

        markdown_text = writer.to_string(document)

        assert "```python" in markdown_text
        assert 'print("Hello")' in markdown_text
        assert "```\nplain code\n```" in markdown_text

    def test_write_to_file(self, sample_document, temp_dir):
        """Test writing document to file."""
        writer = MarkdownWriter()
        output_file = temp_dir / "output.md"

        writer.write(sample_document, output_file)

        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "# Test Document" in content
        assert "Chapter 1" in content

    def test_write_unsupported_format(self, sample_document, temp_dir):
        """Test writing to unsupported format."""
        writer = MarkdownWriter()
        output_file = temp_dir / "output.pdf"

        with pytest.raises(ValueError, match="Unsupported output format"):
            writer.write(sample_document, output_file)

    def test_to_string_invalid_input(self):
        """Test to_string with invalid input."""
        writer = MarkdownWriter()

        with pytest.raises(ValueError, match="Input must be a Document object"):
            writer.to_string("not a document")

    def test_empty_document(self):
        """Test converting empty document."""
        writer = MarkdownWriter()
        document = Document()

        markdown_text = writer.to_string(document)
        assert markdown_text == ""

    def test_roundtrip_conversion(self, temp_dir, sample_markdown_content):
        """Test reading and writing markdown (roundtrip)."""
        # Write sample content to file
        input_file = temp_dir / "input.md"
        input_file.write_text(sample_markdown_content)

        # Read with reader
        reader = MarkdownReader()
        document = reader.read(input_file)

        # Write with writer
        writer = MarkdownWriter()
        output_file = temp_dir / "output.md"
        writer.write(document, output_file)

        # Verify output file exists and has content
        assert output_file.exists()
        output_content = output_file.read_text()

        # Should contain key elements (exact formatting may differ)
        assert "Test Document" in output_content
        assert "Chapter 1" in output_content
        assert "print('Hello, World!')" in output_content