"""
Unit tests for converter factory and document converter.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.core.converter import ConverterFactory, DocumentConverter
from src.readers.base import BaseReader
from src.writers.base import BaseWriter
from src.core.document import Document


class MockReader(BaseReader):
    """Mock reader for testing."""

    def read(self, source):
        doc = Document(title="Mock Document")
        doc.add_paragraph("Mock content")
        return doc

    def supports_format(self, file_path):
        return Path(file_path).suffix.lower() == '.mock'

    @classmethod
    def get_supported_extensions(cls):
        return ['.mock']


class MockWriter(BaseWriter):
    """Mock writer for testing."""

    def write(self, document, output_path):
        Path(output_path).write_text("Mock output content")

    def to_string(self, document):
        return "Mock string representation"

    def supports_format(self, file_path):
        return Path(file_path).suffix.lower() == '.mock'

    @classmethod
    def get_supported_extensions(cls):
        return ['.mock']


class TestConverterFactory:
    """Test ConverterFactory functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any existing registrations
        ConverterFactory._readers.clear()
        ConverterFactory._writers.clear()

    def test_register_reader(self):
        """Test registering a reader."""
        ConverterFactory.register_reader(MockReader)

        assert '.mock' in ConverterFactory._readers
        assert ConverterFactory._readers['.mock'] == MockReader

    def test_register_writer(self):
        """Test registering a writer."""
        ConverterFactory.register_writer(MockWriter)

        assert '.mock' in ConverterFactory._writers
        assert ConverterFactory._writers['.mock'] == MockWriter

    def test_get_reader_success(self):
        """Test getting a registered reader."""
        ConverterFactory.register_reader(MockReader)

        reader = ConverterFactory.get_reader("test.mock")
        assert isinstance(reader, MockReader)

    def test_get_reader_not_registered(self):
        """Test getting a reader that's not registered."""
        with pytest.raises(ValueError, match="No reader registered for extension"):
            ConverterFactory.get_reader("test.unknown")

    def test_get_writer_success(self):
        """Test getting a registered writer."""
        ConverterFactory.register_writer(MockWriter)

        writer = ConverterFactory.get_writer("test.mock")
        assert isinstance(writer, MockWriter)

    def test_get_writer_not_registered(self):
        """Test getting a writer that's not registered."""
        with pytest.raises(ValueError, match="No writer registered for extension"):
            ConverterFactory.get_writer("test.unknown")

    def test_create_converter_success(self):
        """Test creating a converter successfully."""
        ConverterFactory.register_reader(MockReader)
        ConverterFactory.register_writer(MockWriter)

        converter = ConverterFactory.create_converter("input.mock", "output.mock")
        assert isinstance(converter, DocumentConverter)
        assert isinstance(converter.reader, MockReader)
        assert isinstance(converter.writer, MockWriter)

    def test_create_converter_no_reader(self):
        """Test creating converter when reader is not available."""
        ConverterFactory.register_writer(MockWriter)

        with pytest.raises(ValueError, match="No reader registered for extension"):
            ConverterFactory.create_converter("input.unknown", "output.mock")

    def test_create_converter_no_writer(self):
        """Test creating converter when writer is not available."""
        ConverterFactory.register_reader(MockReader)

        with pytest.raises(ValueError, match="No writer registered for extension"):
            ConverterFactory.create_converter("input.mock", "output.unknown")

    def test_get_supported_input_formats(self):
        """Test getting supported input formats."""
        ConverterFactory.register_reader(MockReader)

        formats = ConverterFactory.get_supported_input_formats()
        assert '.mock' in formats

    def test_get_supported_output_formats(self):
        """Test getting supported output formats."""
        ConverterFactory.register_writer(MockWriter)

        formats = ConverterFactory.get_supported_output_formats()
        assert '.mock' in formats

    def test_is_conversion_supported(self):
        """Test checking if conversion is supported."""
        ConverterFactory.register_reader(MockReader)
        ConverterFactory.register_writer(MockWriter)

        assert ConverterFactory.is_conversion_supported('.mock', '.mock') is True
        assert ConverterFactory.is_conversion_supported('.mock', '.unknown') is False
        assert ConverterFactory.is_conversion_supported('.unknown', '.mock') is False

    def test_case_insensitive_extensions(self):
        """Test that extensions are handled case-insensitively."""
        ConverterFactory.register_reader(MockReader)
        ConverterFactory.register_writer(MockWriter)

        # Test uppercase extensions
        reader = ConverterFactory.get_reader("test.MOCK")
        writer = ConverterFactory.get_writer("test.MOCK")

        assert isinstance(reader, MockReader)
        assert isinstance(writer, MockWriter)

        assert ConverterFactory.is_conversion_supported('.MOCK', '.mock') is True
        assert ConverterFactory.is_conversion_supported('.mock', '.MOCK') is True


class TestDocumentConverter:
    """Test DocumentConverter functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.mock_reader = Mock(spec=BaseReader)
        self.mock_writer = Mock(spec=BaseWriter)
        self.converter = DocumentConverter(self.mock_reader, self.mock_writer)

    def test_converter_initialization(self):
        """Test converter initialization."""
        assert self.converter.reader == self.mock_reader
        assert self.converter.writer == self.mock_writer

    def test_convert_success(self, temp_dir):
        """Test successful conversion."""
        # Create input file
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")
        output_file = temp_dir / "output.txt"

        # Set up mocks
        mock_document = Mock(spec=Document)
        self.mock_reader.supports_format.return_value = True
        self.mock_reader.read.return_value = mock_document
        self.mock_writer.supports_format.return_value = True

        # Perform conversion
        self.converter.convert(input_file, output_file)

        # Verify calls
        self.mock_reader.supports_format.assert_called_once_with(input_file)
        self.mock_reader.read.assert_called_once_with(input_file)
        self.mock_writer.supports_format.assert_called_once_with(output_file)
        self.mock_writer.write.assert_called_once_with(mock_document, output_file)

    def test_convert_input_file_not_found(self, temp_dir):
        """Test conversion with non-existent input file."""
        input_file = temp_dir / "nonexistent.txt"
        output_file = temp_dir / "output.txt"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            self.converter.convert(input_file, output_file)

    def test_convert_reader_format_not_supported(self, temp_dir):
        """Test conversion when reader doesn't support input format."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")
        output_file = temp_dir / "output.txt"

        self.mock_reader.supports_format.return_value = False

        with pytest.raises(ValueError, match="Reader does not support format"):
            self.converter.convert(input_file, output_file)

    def test_convert_writer_format_not_supported(self, temp_dir):
        """Test conversion when writer doesn't support output format."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")
        output_file = temp_dir / "output.txt"

        self.mock_reader.supports_format.return_value = True
        self.mock_writer.supports_format.return_value = False

        with pytest.raises(ValueError, match="Writer does not support format"):
            self.converter.convert(input_file, output_file)

    def test_convert_to_string_success(self, temp_dir):
        """Test successful conversion to string."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")

        mock_document = Mock(spec=Document)
        self.mock_reader.supports_format.return_value = True
        self.mock_reader.read.return_value = mock_document
        self.mock_writer.to_string.return_value = "converted content"

        result = self.converter.convert_to_string(input_file)

        assert result == "converted content"
        self.mock_reader.read.assert_called_once_with(input_file)
        self.mock_writer.to_string.assert_called_once_with(mock_document)

    def test_convert_to_string_input_file_not_found(self, temp_dir):
        """Test convert_to_string with non-existent input file."""
        input_file = temp_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            self.converter.convert_to_string(input_file)

    def test_convert_to_string_format_not_supported(self, temp_dir):
        """Test convert_to_string when format is not supported."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")

        self.mock_reader.supports_format.return_value = False

        with pytest.raises(ValueError, match="Reader does not support format"):
            self.converter.convert_to_string(input_file)

    def test_convert_with_string_paths(self, temp_dir):
        """Test conversion with string paths instead of Path objects."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")
        output_file = temp_dir / "output.txt"

        mock_document = Mock(spec=Document)
        self.mock_reader.supports_format.return_value = True
        self.mock_reader.read.return_value = mock_document
        self.mock_writer.supports_format.return_value = True

        # Use string paths
        self.converter.convert(str(input_file), str(output_file))

        # Should still work correctly
        self.mock_reader.read.assert_called_once()
        self.mock_writer.write.assert_called_once()


class TestIntegratedConverter:
    """Test converter with real components integration."""

    def setup_method(self):
        """Set up with real reader and writer instances."""
        ConverterFactory._readers.clear()
        ConverterFactory._writers.clear()
        ConverterFactory.register_reader(MockReader)
        ConverterFactory.register_writer(MockWriter)

    def test_end_to_end_conversion(self, temp_dir):
        """Test end-to-end conversion with factory."""
        input_file = temp_dir / "input.mock"
        output_file = temp_dir / "output.mock"
        input_file.write_text("input content")

        converter = ConverterFactory.create_converter(input_file, output_file)
        converter.convert(input_file, output_file)

        assert output_file.exists()
        assert output_file.read_text() == "Mock output content"

    def test_convert_to_string_integration(self, temp_dir):
        """Test convert_to_string with factory."""
        input_file = temp_dir / "input.mock"
        input_file.write_text("input content")

        converter = ConverterFactory.create_converter(input_file, "output.mock")
        result = converter.convert_to_string(input_file)

        assert result == "Mock string representation"