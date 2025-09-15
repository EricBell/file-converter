"""
Base interface for document writers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from ..core.document import Document


class BaseWriter(ABC):
    """Abstract base class for document writers."""

    @abstractmethod
    def write(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Write a document to the specified output path.

        Args:
            document: Document object to write
            output_path: Path where the document should be written

        Raises:
            ValueError: If the document format is not supported
            IOError: If writing to the file fails
            Exception: If conversion fails
        """
        pass

    @abstractmethod
    def to_string(self, document: Document) -> str:
        """
        Convert a document to its string representation.

        Args:
            document: Document object to convert

        Returns:
            str: String representation of the document

        Raises:
            ValueError: If the document format is not supported
            Exception: If conversion fails
        """
        pass

    @abstractmethod
    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this writer supports the given file format.

        Args:
            file_path: Path to check the format for

        Returns:
            bool: True if the format is supported
        """
        pass

    @classmethod
    @abstractmethod
    def get_supported_extensions(cls) -> list[str]:
        """
        Get list of supported file extensions.

        Returns:
            list[str]: List of supported extensions (e.g., ['.md', '.html'])
        """
        pass