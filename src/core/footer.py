"""
Footer configuration for document conversion.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FooterConfig:
    """Configuration for document footers."""

    enabled: bool = True
    layout: str = "single"  # "single" or "double"
    left_template: str = "Last updated: {date}"
    right_template: str = "Page {page}"
    date_format: str = "%Y-%m-%d"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.layout not in ["single", "double"]:
            raise ValueError(f"Invalid layout: {self.layout}. Must be 'single' or 'double'")

    def get_date_string(self) -> str:
        """
        Get the formatted date string.

        Returns:
            str: Formatted current date
        """
        return datetime.now().strftime(self.date_format)

    def format_footer_text(self, template: str, page_number: int) -> str:
        """
        Format a footer template with current values.

        Args:
            template: Template string with {date} and {page} placeholders
            page_number: Current page number

        Returns:
            str: Formatted footer text
        """
        return template.format(
            date=self.get_date_string(),
            page=page_number
        )

    def get_footer_for_page(self, page_number: int) -> tuple[str, str]:
        """
        Get left and right footer text for a given page number.

        For single-sided layout, left and right are consistent across pages.
        For double-sided layout, they are swapped on even pages.

        Args:
            page_number: Current page number (1-indexed)

        Returns:
            tuple[str, str]: (left_text, right_text) for the page
        """
        if not self.enabled:
            return ("", "")

        left_text = self.format_footer_text(self.left_template, page_number)
        right_text = self.format_footer_text(self.right_template, page_number)

        # For double-sided layout, swap on even pages
        if self.layout == "double" and page_number % 2 == 0:
            return (right_text, left_text)

        return (left_text, right_text)
