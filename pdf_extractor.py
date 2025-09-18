#!/usr/bin/env python3
"""
PDF Text Extraction Service using PDF-plumber
Provides superior text extraction for real estate documents
"""

import pdfplumber
import sys
import json
import re
from typing import Dict, List, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import base64

app = Flask(__name__)
CORS(app)

class PDFExtractor:
    def __init__(self):
        self.line_number_pattern = re.compile(r'^\s*\d+\s*$')
        self.form_field_pattern = re.compile(r'_{3,}')  # 3+ underscores (form fields)
        
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF using pdfplumber with enhanced formatting
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = []
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = self._extract_page_text(page, page_num)
                    pages_text.append(page_text)
                
                # Combine all pages
                full_text = self._combine_pages(pages_text)
                
                return {
                    'success': True,
                    'text': full_text,
                    'page_count': total_pages,
                    'pages': pages_text,
                    'method': 'pdfplumber',
                    'confidence': 0.95
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'page_count': 0,
                'method': 'pdfplumber',
                'confidence': 0.0
            }
    
    def _extract_page_text(self, page, page_num: int) -> str:
        """
        Extract text from a single page with intelligent formatting
        """
        # Try table extraction first (for structured content)
        tables = page.extract_tables()
        table_text = ""
        
        if tables:
            table_text = self._extract_table_text(tables)
        
        # Extract regular text
        text = page.extract_text()
        
        if not text:
            return table_text
        
        # Clean and format the text
        cleaned_text = self._clean_text(text)
        
        # Combine table and regular text
        if table_text and cleaned_text:
            return f"{cleaned_text}\n\n{table_text}"
        elif table_text:
            return table_text
        else:
            return cleaned_text
    
    def _extract_table_text(self, tables: List[List[List[str]]]) -> str:
        """
        Convert extracted tables to readable text format
        """
        table_texts = []
        
        for table_idx, table in enumerate(tables):
            if not table:
                continue
                
            table_lines = []
            for row in table:
                if row and any(cell and cell.strip() for cell in row):
                    # Join non-empty cells with proper spacing
                    clean_row = [cell.strip() if cell else '' for cell in row]
                    # Only include rows that have meaningful content
                    if any(cell and not self.form_field_pattern.match(cell) for cell in clean_row):
                        table_lines.append(' | '.join(clean_row))
            
            if table_lines:
                table_texts.append('\n'.join(table_lines))
        
        return '\n\n'.join(table_texts)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and format extracted text
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are just numbers (line numbers)
            if self.line_number_pattern.match(line):
                continue
            
            # Skip lines that are just underscores (form fields)
            if self.form_field_pattern.match(line):
                continue
            
            # Skip very short lines that might be artifacts
            if len(line) < 2:
                continue
            
            # Clean up excessive whitespace
            line = re.sub(r'\s+', ' ', line)
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _combine_pages(self, pages_text: List[str]) -> str:
        """
        Combine text from all pages with proper page breaks
        """
        non_empty_pages = [page for page in pages_text if page.strip()]
        return '\n\n--- Page Break ---\n\n'.join(non_empty_pages)

# Initialize extractor
extractor = PDFExtractor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'pdf-extractor',
        'version': '1.0.0'
    })

@app.route('/extract', methods=['POST'])
def extract_pdf():
    """
    Extract text from PDF file
    Expects: multipart/form-data with 'file' field
    Returns: JSON with extracted text
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'File must be a PDF'
            }), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Extract text
            result = extractor.extract_text_from_pdf(temp_path)
            return jsonify(result)
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/extract-base64', methods=['POST'])
def extract_pdf_base64():
    """
    Extract text from base64 encoded PDF
    Expects: JSON with 'pdf_data' field containing base64 PDF
    Returns: JSON with extracted text
    """
    try:
        data = request.get_json()
        
        if not data or 'pdf_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No PDF data provided'
            }), 400
        
        # Decode base64 PDF data
        try:
            pdf_bytes = base64.b64decode(data['pdf_data'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid base64 data: {str(e)}'
            }), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name
        
        try:
            # Extract text
            result = extractor.extract_text_from_pdf(temp_path)
            return jsonify(result)
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"🐍 PDF Extractor Service starting on port {port}")
    print(f"📄 Using pdfplumber for superior PDF text extraction")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
