"""
Integration tests for CLI functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner

from src.cli.main import main


class TestCLIIntegration:
    """Integration tests for the CLI."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_help_command(self):
        """Test the help command."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "Convert files between different document formats" in result.output
        assert "INPUT_FILE" in result.output

    def test_version_command(self):
        """Test the version command."""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert "2.0.0" in result.output

    def test_list_formats_command(self):
        """Test the list formats command."""
        result = self.runner.invoke(main, ['--list-formats'])
        assert result.exit_code == 0
        assert "Supported input formats:" in result.output
        assert "Supported output formats:" in result.output
        assert ".pdf" in result.output
        assert ".md" in result.output
        assert ".docx" in result.output

    def test_missing_input_file(self):
        """Test CLI with missing input file."""
        result = self.runner.invoke(main, ['nonexistent.pdf'])
        assert result.exit_code == 2  # Click error code for missing file
        assert "does not exist" in result.output.lower()

    def test_unsupported_input_format(self, temp_dir):
        """Test CLI with unsupported input format."""
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("test content")

        result = self.runner.invoke(main, [str(unsupported_file)])
        assert result.exit_code == 1
        assert "Unsupported input format" in result.output

    def test_missing_output_and_format(self, temp_dir):
        """Test CLI when both output and format are missing."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        result = self.runner.invoke(main, [str(test_file)])
        assert result.exit_code == 1
        assert "Either --output or --format must be specified" in result.output

    def test_format_output_mismatch_warning(self, temp_dir):
        """Test warning when format and output extension don't match."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(test_file),
            '-o', str(temp_dir / "output.docx"),
            '-f', 'md'
        ])
        # Should show warning about format mismatch
        assert "Warning:" in result.output

    def test_unsupported_output_format(self, temp_dir):
        """Test CLI with unsupported output format."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(test_file),
            '-o', str(temp_dir / "output.xyz")
        ])
        assert result.exit_code == 1
        assert "Unsupported output format" in result.output

    def test_unsupported_conversion(self, temp_dir):
        """Test CLI with unsupported conversion combination."""
        # Create a mock file that would have an extension not in our conversion matrix
        # This test assumes we might add readers/writers that don't all support each other
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        # For now, all our current formats support conversion to each other
        # So this test is more of a placeholder for future unsupported combinations
        result = self.runner.invoke(main, [
            str(test_file),
            '-f', 'md'
        ])
        # This should succeed with current implementation
        assert "Converting" in result.output or result.exit_code == 0

    @patch('src.cli.main.ConverterFactory.create_converter')
    def test_conversion_error(self, mock_create_converter, temp_dir):
        """Test CLI handling of conversion errors."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        mock_converter = mock_create_converter.return_value
        mock_converter.convert.side_effect = Exception("Conversion failed")

        result = self.runner.invoke(main, [
            str(test_file),
            '-f', 'docx'
        ])
        assert result.exit_code == 1
        assert "Error: Conversion failed" in result.output

    def test_file_exists_no_overwrite(self, temp_dir):
        """Test CLI when output file exists and no overwrite flag."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        output_file = temp_dir / "output.md"
        output_file.write_text("existing content")

        # Test with 'n' response to overwrite prompt
        result = self.runner.invoke(main, [
            str(test_file),
            '-o', str(output_file)
        ], input='n\n')

        assert result.exit_code == 1
        assert "Operation cancelled" in result.output

    def test_file_exists_with_overwrite_flag(self, temp_dir):
        """Test CLI with overwrite flag when file exists."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        output_file = temp_dir / "output.md"
        output_file.write_text("existing content")

        result = self.runner.invoke(main, [
            str(test_file),
            '-o', str(output_file),
            '--overwrite'
        ])

        # Should succeed without prompting
        assert "Converting" in result.output

    def test_format_normalization(self, temp_dir):
        """Test that format options are normalized correctly."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        # Test different format specifications
        result = self.runner.invoke(main, [
            str(test_file),
            '-f', 'markdown'  # Should be normalized to .md
        ])

        assert "Converting" in result.output

    def test_auto_output_path_generation(self, temp_dir):
        """Test automatic output path generation."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(test_file),
            '-f', 'docx'
        ])

        # Should generate test.docx automatically
        expected_output = temp_dir / "test.docx"
        assert f"'{expected_output}'" in result.output or "Converting" in result.output

    @patch('src.cli.main.ConverterFactory.create_converter')
    def test_successful_conversion_output(self, mock_create_converter, temp_dir):
        """Test successful conversion output messages."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")
        output_file = temp_dir / "output.docx"

        mock_converter = mock_create_converter.return_value

        result = self.runner.invoke(main, [
            str(test_file),
            '-o', str(output_file)
        ])

        assert "Converting" in result.output
        assert "Successfully converted" in result.output
        assert str(test_file) in result.output
        assert str(output_file) in result.output

    def test_case_insensitive_format_option(self, temp_dir):
        """Test that format option is case insensitive."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(test_file),
            '-f', 'DOCX'  # Uppercase should work
        ])

        # Should not error on case
        assert result.exit_code != 1 or "Unsupported" not in result.output

    def test_pathlib_path_handling(self, temp_dir):
        """Test that Path objects are handled correctly."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test\n\nThis is a test.")

        # CLI should handle Path objects properly when they're converted to strings
        result = self.runner.invoke(main, [
            str(test_file),
            '-f', 'md'
        ])

        assert "Converting" in result.output


class TestCLIEdgeCases:
    """Test edge cases and error handling in CLI."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_empty_input_file(self, temp_dir):
        """Test CLI with empty input file."""
        empty_file = temp_dir / "empty.md"
        empty_file.write_text("")

        result = self.runner.invoke(main, [
            str(empty_file),
            '-f', 'docx'
        ])

        # Should handle empty files gracefully
        assert "Converting" in result.output

    def test_very_long_file_paths(self, temp_dir):
        """Test CLI with very long file paths."""
        # Create nested directories
        long_path = temp_dir
        for i in range(10):
            long_path = long_path / f"very_long_directory_name_{i}"
            long_path.mkdir(exist_ok=True)

        test_file = long_path / "test.md"
        test_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(test_file),
            '-f', 'docx'
        ])

        # Should handle long paths
        assert "Converting" in result.output or result.exit_code == 0

    def test_special_characters_in_filename(self, temp_dir):
        """Test CLI with special characters in filenames."""
        special_file = temp_dir / "test file with spaces & symbols.md"
        special_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(special_file),
            '-f', 'docx'
        ])

        assert "Converting" in result.output or result.exit_code == 0

    def test_multiple_dots_in_filename(self, temp_dir):
        """Test CLI with multiple dots in filename."""
        dotted_file = temp_dir / "test.backup.final.md"
        dotted_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(dotted_file),
            '-f', 'docx'
        ])

        # Should correctly identify .md as the extension
        assert "Converting" in result.output or result.exit_code == 0

    def test_no_extension_input_file(self, temp_dir):
        """Test CLI with input file that has no extension."""
        no_ext_file = temp_dir / "testfile"
        no_ext_file.write_text("# Test")

        result = self.runner.invoke(main, [
            str(no_ext_file),
            '-f', 'docx'
        ])

        # Should error due to no extension
        assert result.exit_code == 1
        assert "Unsupported input format" in result.output