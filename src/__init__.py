"""
File converter package - modular document conversion system.
"""

from .core.converter import ConverterFactory, DocumentConverter
from .readers.pdf_reader import PDFReader
from .readers.markdown_reader import MarkdownReader
from .writers.markdown_writer import MarkdownWriter
from .writers.docx_writer import DocxWriter
from .writers.pdf_writer import PDFWriter

# Register readers and writers with the factory
ConverterFactory.register_reader(PDFReader)
ConverterFactory.register_reader(MarkdownReader)
ConverterFactory.register_writer(MarkdownWriter)
ConverterFactory.register_writer(DocxWriter)
ConverterFactory.register_writer(PDFWriter)

__all__ = [
    'ConverterFactory',
    'DocumentConverter',
    'PDFReader',
    'MarkdownReader',
    'MarkdownWriter',
    'DocxWriter',
    'PDFWriter'
]