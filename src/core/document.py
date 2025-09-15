"""
Document model for representing structured content in a format-agnostic way.
"""

from abc import ABC
from typing import List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ElementType(Enum):
    """Types of document elements."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    BOLD = "bold"
    ITALIC = "italic"
    LINK = "link"
    IMAGE = "image"


@dataclass
class DocumentElement(ABC):
    """Base class for all document elements."""
    content: str = ""
    attributes: dict = None
    element_type: ElementType = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class Heading(DocumentElement):
    """Represents a heading element."""
    level: int = 1

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.HEADING
        self.attributes["level"] = self.level


@dataclass
class Paragraph(DocumentElement):
    """Represents a paragraph element."""

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.PARAGRAPH


@dataclass
class DocumentList(DocumentElement):
    """Represents a list element."""
    ordered: bool = False
    items: List["ListItem"] = None

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.LIST
        self.attributes["ordered"] = self.ordered
        if self.items is None:
            self.items = []


@dataclass
class ListItem(DocumentElement):
    """Represents a list item element."""

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.LIST_ITEM


@dataclass
class CodeBlock(DocumentElement):
    """Represents a code block element."""
    language: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.CODE_BLOCK
        if self.language:
            self.attributes["language"] = self.language


@dataclass
class InlineCode(DocumentElement):
    """Represents inline code element."""

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.INLINE_CODE


@dataclass
class Bold(DocumentElement):
    """Represents bold text element."""

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.BOLD


@dataclass
class Italic(DocumentElement):
    """Represents italic text element."""

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.ITALIC


@dataclass
class Link(DocumentElement):
    """Represents a hyperlink element."""
    url: str = ""
    title: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.LINK
        self.attributes["url"] = self.url
        if self.title:
            self.attributes["title"] = self.title


@dataclass
class Image(DocumentElement):
    """Represents an image element."""
    url: str = ""
    alt_text: Optional[str] = None
    title: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.element_type = ElementType.IMAGE
        self.attributes["url"] = self.url
        if self.alt_text:
            self.attributes["alt_text"] = self.alt_text
        if self.title:
            self.attributes["title"] = self.title


class Document:
    """
    Represents a structured document with various elements.
    """

    def __init__(self, title: Optional[str] = None):
        self.title = title
        self.elements: List[DocumentElement] = []
        self.metadata: dict = {}

    def add_element(self, element: DocumentElement) -> None:
        """Add an element to the document."""
        self.elements.append(element)

    def add_heading(self, text: str, level: int = 1) -> Heading:
        """Add a heading element."""
        heading = Heading(content=text, level=level)
        self.add_element(heading)
        return heading

    def add_paragraph(self, text: str) -> Paragraph:
        """Add a paragraph element."""
        paragraph = Paragraph(content=text)
        self.add_element(paragraph)
        return paragraph

    def add_list(self, items: List[str], ordered: bool = False) -> DocumentList:
        """Add a list element with items."""
        list_element = DocumentList(ordered=ordered)
        for item_text in items:
            list_item = ListItem(content=item_text)
            list_element.items.append(list_item)
        self.add_element(list_element)
        return list_element

    def add_code_block(self, code: str, language: Optional[str] = None) -> CodeBlock:
        """Add a code block element."""
        code_block = CodeBlock(content=code, language=language)
        self.add_element(code_block)
        return code_block

    def get_elements_by_type(self, element_type: ElementType) -> List[DocumentElement]:
        """Get all elements of a specific type."""
        return [elem for elem in self.elements if elem.element_type == element_type]

    def get_headings(self) -> List[Heading]:
        """Get all heading elements."""
        return [elem for elem in self.elements if elem.element_type == ElementType.HEADING]

    def get_text_content(self) -> str:
        """Get all text content as a single string."""
        text_parts = []
        for element in self.elements:
            if element.content:
                text_parts.append(element.content)
        return "\n".join(text_parts)

    def __len__(self) -> int:
        """Return the number of elements in the document."""
        return len(self.elements)

    def __iter__(self):
        """Iterate over document elements."""
        return iter(self.elements)