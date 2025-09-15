"""
Base interface for document readers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from ..core.document import Document


class BaseReader(ABC):
    """Abstract base class for document readers."""

    @abstractmethod
    def read(self, source: Union[str, Path]) -> Document:
        """
        Read and parse a document from the given source.

        Args:
            source: File path or content to read

        Returns:
            Document: Parsed document object

        Raises:
            ValueError: If the source format is not supported
            FileNotFoundError: If the file doesn't exist
            Exception: If parsing fails
        """
        pass

    @abstractmethod
    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this reader supports the given file format.

        Args:
            file_path: Path to the file to check

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
            list[str]: List of supported extensions (e.g., ['.pdf', '.txt'])
        """
        pass