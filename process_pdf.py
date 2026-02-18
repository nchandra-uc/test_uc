#!/usr/bin/env python3
"""
PDF Processing Script for Extracting Financial Data
Extracts account numbers, deposit account numbers, and routing numbers from PDF files.
"""

import re
import sys
import csv
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber


def extract_financial_data(text: str) -> Dict[str, List[str]]:
    """
    Extract account numbers, deposit account numbers, and routing numbers from text.
    
    Args:
        text: The text content to search
        
    Returns:
        Dictionary with keys: 'account_numbers', 'deposit_account_numbers', 'routing_numbers'
    """
    results = {
        'account_numbers': [],
        'deposit_account_numbers': [],
        'routing_numbers': []
    }
    
    # Pattern for account numbers (typically 9-17 digits)
    # Matches patterns like "Account #: 123456789" or "Account +A1:D42#: 123456789"
    account_patterns = [
        r'(?:Account\s*(?:\+[A-Z]\d+:[A-Z]\d+)?\s*#?\s*:?\s*)(\d{9,17})',
        r'(?:Account\s+Number\s*:?\s*)(\d{9,17})',
        r'(?:Acct\s*\.?\s*#?\s*:?\s*)(\d{9,17})',
    ]
    
    # Pattern for deposit account numbers
    deposit_patterns = [
        r'(?:Deposit\s+Account\s*#?\s*:?\s*)(\d{9,17})',
        r'(?:Deposit\s+Acct\s*\.?\s*#?\s*:?\s*)(\d{9,17})',
    ]
    
    # Pattern for routing numbers (typically 9 digits)
    routing_patterns = [
        r'(?:Routing\s*#?\s*:?\s*)(\d{9})',
        r'(?:Bank\s+Routing\s*#?\s*:?\s*)(\d{9})',
        r'(?:ABA\s+(?:number|#)?\s*:?\s*)(\d{9})',
        r'(?:Routing\s+Number\s*:?\s*)(\d{9})',
    ]
    
    # Extract account numbers
    for pattern in account_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        results['account_numbers'].extend(matches)
    
    # Extract deposit account numbers
    for pattern in deposit_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        results['deposit_account_numbers'].extend(matches)
    
    # Extract routing numbers
    for pattern in routing_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        results['routing_numbers'].extend(matches)
    
    # Remove duplicates while preserving order
    for key in results:
        seen = set()
        results[key] = [x for x in results[key] if not (x in seen or seen.add(x))]
    
    return results


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    text_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    
    return "\n".join(text_content)


def save_to_csv(data: Dict[str, List[str]], output_path: str):
    """
    Save extracted financial data to a CSV file.
    
    Args:
        data: Dictionary with financial data
        output_path: Path to save the CSV file
    """
    # Find the maximum length to determine number of rows
    max_length = max(
        len(data['account_numbers']),
        len(data['deposit_account_numbers']),
        len(data['routing_numbers'])
    )
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Account Number', 'Deposit Account Number', 'Routing Number'])
        
        # Write data rows
        for i in range(max_length):
            row = [
                data['account_numbers'][i] if i < len(data['account_numbers']) else '',
                data['deposit_account_numbers'][i] if i < len(data['deposit_account_numbers']) else '',
                data['routing_numbers'][i] if i < len(data['routing_numbers']) else ''
            ]
            writer.writerow(row)


def process_pdf(pdf_path: str, output_csv: str = None):
    """
    Process a PDF file and extract financial data.
    
    Args:
        pdf_path: Path to the PDF file
        output_csv: Optional path to save CSV output (default: same name as PDF with .csv extension)
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print(f"Processing PDF: {pdf_path}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(str(pdf_path))
    
    if not text:
        print("Warning: No text could be extracted from the PDF")
        return
    
    # Extract financial data
    financial_data = extract_financial_data(text)
    
    # Print summary
    print("\nExtraction Summary:")
    print(f"  Account Numbers: {len(financial_data['account_numbers'])}")
    print(f"  Deposit Account Numbers: {len(financial_data['deposit_account_numbers'])}")
    print(f"  Routing Numbers: {len(financial_data['routing_numbers'])}")
    
    # Save to CSV if output path is provided
    if output_csv is None:
        output_csv = pdf_path.with_suffix('.csv')
    
    save_to_csv(financial_data, str(output_csv))
    print(f"\nData saved to: {output_csv}")
    
    # Print first few examples
    if financial_data['account_numbers']:
        print("\nSample Account Numbers:")
        for acc in financial_data['account_numbers'][:5]:
            print(f"  {acc}")
    
    if financial_data['routing_numbers']:
        print("\nSample Routing Numbers:")
        for routing in financial_data['routing_numbers'][:5]:
            print(f"  {routing}")


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python process_pdf.py <pdf_file> [output_csv]")
        print("Example: python process_pdf.py myfilecsv.pdf output.csv")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_pdf(pdf_file, output_file)


if __name__ == "__main__":
    main()
