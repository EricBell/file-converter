"""
Command-line interface for the file converter.
"""

import sys
from pathlib import Path
from typing import Optional
import click

from ..core.converter import ConverterFactory
from ..core.footer import FooterConfig
from ..core.lockfile import cleanup_lock_files


def detect_format_from_extension(file_path: Path) -> str:
    """Detect file format from extension."""
    return file_path.suffix.lower()


def generate_output_path(input_path: Path, output_format: str) -> Path:
    """Generate output path based on input path and desired format."""
    if not output_format.startswith('.'):
        output_format = f'.{output_format}'
    return input_path.with_suffix(output_format)


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path), required=False)
@click.option('-o', '--output', type=click.Path(path_type=Path),
              help='Output file path. If not provided, auto-generates '
                   'based on input filename and target format')
@click.option('-f', '--format', 'output_format',
              type=click.Choice(['md', 'markdown', 'docx', 'pdf'], case_sensitive=False),
              help='Output format. If not specified, tries to detect '
                   'from output file extension')
@click.option('--overwrite', is_flag=True,
              help='Overwrite output file if it exists')
@click.option('--list-formats', is_flag=True,
              help='List supported input and output formats')
@click.option('--no-footer', is_flag=True,
              help='Disable footer (footer is enabled by default)')
@click.option('--footer-layout',
              type=click.Choice(['single', 'double'], case_sensitive=False),
              default='single',
              help='Footer layout: single-sided or double-sided (default: single)')
@click.option('--footer-left',
              default='Last updated: {date}',
              help='Left footer template (default: "Last updated: {date}")')
@click.option('--footer-right',
              default='Page {page}',
              help='Right footer template (default: "Page {page}")')
@click.option('--date-format',
              default='%Y-%m-%d',
              help='Date format string (default: "%%Y-%%m-%%d" for YYYY-MM-DD)')
@click.version_option(version='2.1.0')
def main(input_file: Optional[Path], output: Optional[Path], output_format: Optional[str],
         overwrite: bool, list_formats: bool, no_footer: bool, footer_layout: str,
         footer_left: str, footer_right: str, date_format: str):
    """
    Convert files between different document formats.

    INPUT_FILE: Path to the file to convert

    Supported conversions:
    - PDF to Markdown (.md)
    - PDF to DOCX (.docx)
    - PDF to PDF (reformatting)
    - Markdown to PDF (.pdf)
    - Markdown to DOCX (.docx)
    - Markdown to Markdown (reformatting)

    Use --list-formats to see all supported file extensions.
    """

    if list_formats:
        click.echo("Supported input formats:")
        for fmt in sorted(ConverterFactory.get_supported_input_formats()):
            click.echo(f"  {fmt}")
        click.echo("\nSupported output formats:")
        for fmt in sorted(ConverterFactory.get_supported_output_formats()):
            click.echo(f"  {fmt}")
        return

    # Check if input file is provided when not listing formats
    if input_file is None:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    # Validate input file
    input_ext = detect_format_from_extension(input_file)
    if input_ext not in ConverterFactory.get_supported_input_formats():
        click.echo(f"Error: Unsupported input format '{input_ext}'. "
                  f"Use --list-formats to see supported formats.", err=True)
        sys.exit(1)

    # Determine output format and path
    if output is None:
        if output_format is None:
            click.echo("Error: Either --output or --format must be specified "
                      "when output path is not provided.", err=True)
            sys.exit(1)

        # Normalize format
        if output_format in ['md', 'markdown']:
            output_ext = '.md'
        elif output_format == 'docx':
            output_ext = '.docx'
        elif output_format == 'pdf':
            output_ext = '.pdf'
        else:
            output_ext = f'.{output_format}'

        output = generate_output_path(input_file, output_ext)
    else:
        output_ext = detect_format_from_extension(output)
        if output_format and output_format != output_ext.lstrip('.'):
            click.echo("Warning: Specified format doesn't match output "
                      f"file extension. Using extension: {output_ext}")

    # Validate output format
    if output_ext not in ConverterFactory.get_supported_output_formats():
        click.echo(f"Error: Unsupported output format '{output_ext}'. "
                  f"Use --list-formats to see supported formats.", err=True)
        sys.exit(1)

    # Check if conversion is supported
    if not ConverterFactory.is_conversion_supported(input_ext, output_ext):
        click.echo(f"Error: Conversion from {input_ext} to {output_ext} "
                  f"is not supported.", err=True)
        sys.exit(1)

    # Check if output file exists
    if output.exists() and not overwrite:
        if not click.confirm(f"Output file '{output}' already exists. "
                           f"Overwrite?"):
            click.echo("Operation cancelled.")
            sys.exit(1)

    try:
        # Create footer configuration
        footer_config = FooterConfig(
            enabled=not no_footer,
            layout=footer_layout,
            left_template=footer_left,
            right_template=footer_right,
            date_format=date_format
        )

        click.echo(f"Converting '{input_file}' ({input_ext}) to "
                  f"'{output}' ({output_ext})...")

        # Create converter and perform conversion
        converter = ConverterFactory.create_converter(input_file, output)
        converter.convert(input_file, output, footer_config)

        click.echo(f"✓ Successfully converted to '{output}'")
        click.echo(f"  Input:  {input_file} ({input_ext})")
        click.echo(f"  Output: {output} ({output_ext})")

        # Show file size info
        if output.exists():
            size = output.stat().st_size
            click.echo(f"  Size:   {size:,} bytes")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        # Clean up any lock files that may have been created
        if output:
            cleanup_lock_files(output)
        sys.exit(1)


if __name__ == '__main__':
    main()