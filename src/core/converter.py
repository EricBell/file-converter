"""
Base converter interface and factory for document conversions.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Dict, Type
from .document import Document
from ..readers.base import BaseReader
from ..writers.base import BaseWriter


class BaseConverter(ABC):
    """Abstract base class for document converters."""

    def __init__(self, reader: BaseReader, writer: BaseWriter):
        self.reader = reader
        self.writer = writer

    @abstractmethod
    def convert(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
        """
        Convert a document from input format to output format.

        Args:
            input_path: Path to input file
            output_path: Path to output file
        """
        pass

    @abstractmethod
    def convert_to_string(self, input_path: Union[str, Path]) -> str:
        """
        Convert a document and return as string.

        Args:
            input_path: Path to input file

        Returns:
            str: Converted document content
        """
        pass


class DocumentConverter(BaseConverter):
    """Standard implementation of document converter."""

    def convert(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
        """Convert document from input to output format."""
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.reader.supports_format(input_path):
            raise ValueError(f"Reader does not support format: {input_path.suffix}")

        if not self.writer.supports_format(output_path):
            raise ValueError(f"Writer does not support format: {output_path.suffix}")

        # Read document
        document = self.reader.read(input_path)

        # Write document
        self.writer.write(document, output_path)

    def convert_to_string(self, input_path: Union[str, Path]) -> str:
        """Convert document and return as string."""
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.reader.supports_format(input_path):
            raise ValueError(f"Reader does not support format: {input_path.suffix}")

        # Read document
        document = self.reader.read(input_path)

        # Convert to string
        return self.writer.to_string(document)


class ConverterFactory:
    """Factory for creating document converters."""

    _readers: Dict[str, Type[BaseReader]] = {}
    _writers: Dict[str, Type[BaseWriter]] = {}

    @classmethod
    def register_reader(cls, reader_class: Type[BaseReader]) -> None:
        """Register a reader class for its supported extensions."""
        for ext in reader_class.get_supported_extensions():
            cls._readers[ext.lower()] = reader_class

    @classmethod
    def register_writer(cls, writer_class: Type[BaseWriter]) -> None:
        """Register a writer class for its supported extensions."""
        for ext in writer_class.get_supported_extensions():
            cls._writers[ext.lower()] = writer_class

    @classmethod
    def get_reader(cls, file_path: Union[str, Path]) -> BaseReader:
        """Get appropriate reader for file format."""
        ext = Path(file_path).suffix.lower()
        if ext not in cls._readers:
            raise ValueError(f"No reader registered for extension: {ext}")
        return cls._readers[ext]()

    @classmethod
    def get_writer(cls, file_path: Union[str, Path]) -> BaseWriter:
        """Get appropriate writer for file format."""
        ext = Path(file_path).suffix.lower()
        if ext not in cls._writers:
            raise ValueError(f"No writer registered for extension: {ext}")
        return cls._writers[ext]()

    @classmethod
    def create_converter(cls, input_path: Union[str, Path], output_path: Union[str, Path]) -> DocumentConverter:
        """Create a converter for the given input and output formats."""
        reader = cls.get_reader(input_path)
        writer = cls.get_writer(output_path)
        return DocumentConverter(reader, writer)

    @classmethod
    def get_supported_input_formats(cls) -> list[str]:
        """Get list of supported input formats."""
        return list(cls._readers.keys())

    @classmethod
    def get_supported_output_formats(cls) -> list[str]:
        """Get list of supported output formats."""
        return list(cls._writers.keys())

    @classmethod
    def is_conversion_supported(cls, input_ext: str, output_ext: str) -> bool:
        """Check if conversion from input to output format is supported."""
        return (input_ext.lower() in cls._readers and
                output_ext.lower() in cls._writers)