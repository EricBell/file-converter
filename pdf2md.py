#!/usr/bin/env python3
"""
PDF to Markdown Converter CLI

A simple command-line tool to convert PDF files to Markdown format.
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import click
import re


class PDFToMarkdownConverter:
    def __init__(self):
        self.doc = None
    
    def convert_pdf_to_markdown(self, pdf_path):
        try:
            self.doc = fitz.open(pdf_path)
            markdown_content = []
            
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    processed_text = self._process_text(text)
                    if processed_text:
                        markdown_content.append(processed_text)
            
            return "\n\n".join(markdown_content)
        
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        
        finally:
            if self.doc:
                self.doc.close()
    
    def _process_text(self, text):
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if self._is_heading(line):
                line = self._format_heading(line)
            
            line = self._clean_text(line)
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _is_heading(self, line):
        return (
            len(line) < 100 and
            (line.isupper() or 
             re.match(r'^[A-Z][^.]*[^.]$', line) or
             re.match(r'^\d+\.?\s+[A-Z]', line))
        )
    
    def _format_heading(self, line):
        if re.match(r'^\d+\.?\s+', line):
            return f"## {line}"
        elif line.isupper():
            return f"# {line.title()}"
        else:
            return f"## {line}"
    
    def _clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        return text.strip()


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', type=click.Path(path_type=Path), 
              help='Output markdown file path. If not provided, uses input filename with .md extension')
@click.option('--overwrite', is_flag=True, help='Overwrite output file if it exists')
@click.version_option(version='1.0.0')
def main(input_file, output, overwrite):
    """Convert PDF files to Markdown format.
    
    INPUT_FILE: Path to the PDF file to convert
    """
    
    if input_file.suffix.lower() != '.pdf':
        click.echo(f"Error: Input file must be a PDF file, got: {input_file.suffix}", err=True)
        sys.exit(1)
    
    if output is None:
        output = input_file.with_suffix('.md')
    
    if output.exists() and not overwrite:
        if not click.confirm(f"Output file '{output}' already exists. Overwrite?"):
            click.echo("Operation cancelled.")
            sys.exit(1)
    
    try:
        click.echo(f"Converting '{input_file}' to markdown...")
        
        converter = PDFToMarkdownConverter()
        markdown_content = converter.convert_pdf_to_markdown(input_file)
        
        output.write_text(markdown_content, encoding='utf-8')
        
        click.echo(f"✓ Successfully converted to '{output}'")
        click.echo(f"  Input file: {input_file}")
        click.echo(f"  Output file: {output}")
        click.echo(f"  File size: {len(markdown_content)} characters")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()