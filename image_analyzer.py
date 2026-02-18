#!/usr/bin/env python3
"""
Image File Analyzer
Analyzes image files to extract text, identify account numbers, routing numbers,
and other financial data using OCR.
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: PIL/Pillow and/or pytesseract not available. Install with:")
    print("  pip install pillow pytesseract")
    print("  sudo apt-get install tesseract-ocr  # on Linux")


class ImageAnalyzer:
    """Analyzes image files for text extraction and financial data identification."""
    
    # Patterns for identifying financial data
    ACCOUNT_PATTERNS = [
        r'account\s*[#:]?\s*([0-9]{8,12})',
        r'deposit\s+account\s*[#:]?\s*([0-9]{8,12})',
        r'acct\.?\s*[#:]?\s*([0-9]{8,12})',
        r'account\s+number\s*[#:]?\s*([0-9]{8,12})',
    ]
    
    ROUTING_PATTERNS = [
        r'routing\s*[#:]?\s*([0-9]{9})',
        r'bank\s+routing\s*[#:]?\s*([0-9]{9})',
        r'aba\s+number\s*[#:]?\s*([0-9]{9})',
        r'routing\s+number\s*[#:]?\s*([0-9]{9})',
    ]
    
    def __init__(self):
        self.extracted_text = ""
        self.account_numbers = []
        self.routing_numbers = []
        self.raw_data = []
        
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR."""
        if not OCR_AVAILABLE:
            return ""
        
        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using Tesseract OCR
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def parse_financial_data(self, text: str) -> Dict:
        """Parse financial data from text."""
        results = {
            'accounts': [],
            'routing_numbers': [],
            'pairs': [],
            'statistics': {}
        }
        
        # Find all account numbers
        for pattern in self.ACCOUNT_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                account = match.group(1)
                if account not in results['accounts']:
                    results['accounts'].append(account)
        
        # Find all routing numbers
        for pattern in self.ROUTING_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                routing = match.group(1)
                if routing not in results['routing_numbers']:
                    results['routing_numbers'].append(routing)
        
        # Try to find account-routing pairs (lines with both)
        lines = text.split('\n')
        for line in lines:
            account_match = None
            routing_match = None
            
            for pattern in self.ACCOUNT_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    account_match = match.group(1)
                    break
            
            for pattern in self.ROUTING_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    routing_match = match.group(1)
                    break
            
            if account_match and routing_match:
                results['pairs'].append({
                    'account': account_match,
                    'routing': routing_match,
                    'line': line.strip()
                })
        
        # Statistics
        results['statistics'] = {
            'total_accounts': len(results['accounts']),
            'total_routing_numbers': len(results['routing_numbers']),
            'total_pairs': len(results['pairs']),
            'text_length': len(text),
            'lines_processed': len(lines)
        }
        
        return results
    
    def analyze_structured_data(self, text: str) -> Dict:
        """Analyze structured data (like tab-separated account/routing numbers)."""
        results = {
            'structured_records': [],
            'columns_detected': []
        }
        
        lines = text.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Look for tab-separated or space-separated numbers
            # Pattern: number, account, routing, etc.
            parts = re.split(r'[\t\s]{2,}', line.strip())
            
            if len(parts) >= 3:
                record = {
                    'line_number': line_num,
                    'raw_line': line,
                    'parts': parts
                }
                
                # Try to identify account and routing numbers in parts
                for part in parts:
                    # Account numbers are typically 8-12 digits
                    if re.match(r'^[0-9]{8,12}$', part):
                        if 'account' not in record:
                            record['account'] = part
                    # Routing numbers are exactly 9 digits
                    elif re.match(r'^[0-9]{9}$', part):
                        if 'routing' not in record:
                            record['routing'] = part
                
                if 'account' in record or 'routing' in record:
                    results['structured_records'].append(record)
        
        return results
    
    def analyze(self, image_path: str) -> Dict:
        """Main analysis function."""
        print(f"Analyzing image: {image_path}")
        print("=" * 60)
        
        if not Path(image_path).exists():
            return {
                'error': f'Image file not found: {image_path}',
                'suggestion': 'Please provide the path to an image file in the workspace'
            }
        
        # Extract text
        print("Extracting text from image...")
        text = self.extract_text_from_image(image_path)
        
        if not text:
            return {
                'error': 'Could not extract text from image',
                'suggestion': 'Ensure OCR libraries are installed or the image contains readable text'
            }
        
        self.extracted_text = text
        
        # Parse financial data
        print("Parsing financial data...")
        financial_data = self.parse_financial_data(text)
        
        # Analyze structured data
        print("Analyzing structured data...")
        structured_data = self.analyze_structured_data(text)
        
        # Combine results
        results = {
            'image_path': image_path,
            'extracted_text_preview': text[:500] + '...' if len(text) > 500 else text,
            'financial_data': financial_data,
            'structured_data': structured_data,
            'full_text': text
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a summary of the analysis."""
        if 'error' in results:
            print(f"\nError: {results['error']}")
            if 'suggestion' in results:
                print(f"Suggestion: {results['suggestion']}")
            return
        
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        
        stats = results.get('financial_data', {}).get('statistics', {})
        print(f"\nText Extraction:")
        print(f"  - Text length: {stats.get('text_length', 0)} characters")
        print(f"  - Lines processed: {stats.get('lines_processed', 0)}")
        
        print(f"\nFinancial Data Found:")
        print(f"  - Account numbers: {stats.get('total_accounts', 0)}")
        print(f"  - Routing numbers: {stats.get('total_routing_numbers', 0)}")
        print(f"  - Account-Routing pairs: {stats.get('total_pairs', 0)}")
        
        financial = results.get('financial_data', {})
        if financial.get('pairs'):
            print(f"\nAccount-Routing Pairs:")
            for i, pair in enumerate(financial['pairs'][:10], 1):  # Show first 10
                print(f"  {i}. Account: {pair['account']}, Routing: {pair['routing']}")
            if len(financial['pairs']) > 10:
                print(f"  ... and {len(financial['pairs']) - 10} more")
        
        structured = results.get('structured_data', {})
        if structured.get('structured_records'):
            print(f"\nStructured Records Found: {len(structured['structured_records'])}")
            print(f"  (Records with identified account/routing numbers)")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python image_analyzer.py <image_path>")
        print("\nExample:")
        print("  python image_analyzer.py image.png")
        print("\nNote: Requires PIL/Pillow and pytesseract for OCR")
        sys.exit(1)
    
    image_path = sys.argv[1]
    analyzer = ImageAnalyzer()
    
    results = analyzer.analyze(image_path)
    analyzer.print_summary(results)
    
    # Save results to JSON
    output_file = Path(image_path).stem + '_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == '__main__':
    main()
