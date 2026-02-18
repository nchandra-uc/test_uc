#!/usr/bin/env python3
"""
CSV File Processing Script
Extracts and analyzes sensitive data from CSV files including:
- Social Security Numbers (SSN)
- Bank Account Numbers
- Routing Numbers
- Credit Card Numbers
"""

import csv
import re
import sys
from collections import defaultdict
from typing import List, Dict, Tuple


class CSVProcessor:
    """Process CSV files to extract sensitive information."""
    
    # Patterns for detecting sensitive data
    SSN_PATTERN = re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b')
    SSN_ALT_PATTERN = re.compile(r'\b\d{9}\b')
    
    # Credit card patterns (13-19 digits, may have spaces/dashes)
    CC_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
    CC_ALT_PATTERN = re.compile(r'\b\d{13,19}\b')
    
    # Bank account numbers (typically 8-17 digits)
    ACCOUNT_PATTERN = re.compile(r'\b\d{8,17}\b')
    
    # Routing numbers (9 digits)
    ROUTING_PATTERN = re.compile(r'\b\d{9}\b')
    
    def __init__(self, filename: str):
        self.filename = filename
        self.results = {
            'ssn': [],
            'credit_cards': [],
            'account_numbers': [],
            'routing_numbers': [],
            'total_rows': 0,
            'columns': []
        }
    
    def normalize_ssn(self, ssn: str) -> str:
        """Normalize SSN format to XXX-XX-XXXX"""
        digits = re.sub(r'[^\d]', '', ssn)
        if len(digits) == 9:
            return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
        return ssn
    
    def normalize_cc(self, cc: str) -> str:
        """Normalize credit card format"""
        digits = re.sub(r'[^\d]', '', cc)
        return digits
    
    def extract_from_cell(self, cell_value: str) -> Dict[str, List[str]]:
        """Extract sensitive data from a single cell"""
        found = {
            'ssn': [],
            'credit_cards': [],
            'account_numbers': [],
            'routing_numbers': []
        }
        
        if not cell_value or not isinstance(cell_value, str):
            return found
        
        # Extract SSNs
        ssn_matches = self.SSN_PATTERN.findall(cell_value)
        for ssn in ssn_matches:
            normalized = self.normalize_ssn(ssn)
            if normalized not in found['ssn']:
                found['ssn'].append(normalized)
        
        # Also check for 9-digit numbers that might be SSNs
        alt_ssn = self.SSN_ALT_PATTERN.findall(cell_value)
        for ssn in alt_ssn:
            # Exclude if it's part of a credit card or account number
            if len(ssn) == 9 and not any(cc in cell_value for cc in self.CC_PATTERN.findall(cell_value)):
                normalized = self.normalize_ssn(ssn)
                if normalized not in found['ssn']:
                    found['ssn'].append(normalized)
        
        # Extract credit cards
        cc_matches = self.CC_PATTERN.findall(cell_value)
        for cc in cc_matches:
            normalized = self.normalize_cc(cc)
            if normalized not in found['credit_cards']:
                found['credit_cards'].append(normalized)
        
        # Extract account numbers (8-17 digits, but not SSNs or credit cards)
        account_matches = self.ACCOUNT_PATTERN.findall(cell_value)
        for acc in account_matches:
            # Filter out SSNs and credit cards
            if len(acc) == 9:
                # Could be SSN or routing number, check context
                if 'routing' in cell_value.lower() or 'aba' in cell_value.lower():
                    if acc not in found['routing_numbers']:
                        found['routing_numbers'].append(acc)
                elif 'ssn' not in cell_value.lower() and 'social' not in cell_value.lower():
                    # Might be routing number
                    if acc not in found['routing_numbers']:
                        found['routing_numbers'].append(acc)
            elif len(acc) >= 8 and len(acc) <= 17:
                # Check if it's not a credit card (13-19 digits)
                if not (13 <= len(acc) <= 19):
                    if acc not in found['account_numbers']:
                        found['account_numbers'].append(acc)
        
        return found
    
    def process_file(self) -> Dict:
        """Process the CSV file and extract sensitive data"""
        try:
            with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                # Default to comma, try to detect
                delimiter = ','
                try:
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    # If detection fails, try common delimiters
                    if '\t' in sample and sample.count('\t') > sample.count(','):
                        delimiter = '\t'
                    elif ';' in sample and sample.count(';') > sample.count(','):
                        delimiter = ';'
                
                reader = csv.reader(f, delimiter=delimiter)
                
                # Read header
                try:
                    header = next(reader)
                    self.results['columns'] = header
                except StopIteration:
                    print(f"Warning: {self.filename} appears to be empty")
                    return self.results
                
                # Process each row
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
                    self.results['total_rows'] += 1
                    
                    for col_idx, cell in enumerate(row):
                        if col_idx < len(header):
                            col_name = header[col_idx]
                        else:
                            col_name = f"Column_{col_idx + 1}"
                        
                        extracted = self.extract_from_cell(cell)
                        
                        # Add to results with context
                        for ssn in extracted['ssn']:
                            self.results['ssn'].append({
                                'value': ssn,
                                'row': row_num,
                                'column': col_name
                            })
                        
                        for cc in extracted['credit_cards']:
                            self.results['credit_cards'].append({
                                'value': cc,
                                'row': row_num,
                                'column': col_name
                            })
                        
                        for acc in extracted['account_numbers']:
                            self.results['account_numbers'].append({
                                'value': acc,
                                'row': row_num,
                                'column': col_name
                            })
                        
                        for routing in extracted['routing_numbers']:
                            self.results['routing_numbers'].append({
                                'value': routing,
                                'row': row_num,
                                'column': col_name
                            })
        
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing file: {e}")
            sys.exit(1)
        
        return self.results
    
    def print_summary(self):
        """Print a summary of extracted sensitive data"""
        print(f"\n{'='*60}")
        print(f"CSV File Processing Summary: {self.filename}")
        print(f"{'='*60}")
        print(f"Total rows processed: {self.results['total_rows']}")
        print(f"Columns: {', '.join(self.results['columns'])}")
        print(f"\n{'='*60}")
        print("Sensitive Data Found:")
        print(f"{'='*60}")
        
        print(f"\nSocial Security Numbers (SSN): {len(self.results['ssn'])}")
        if self.results['ssn']:
            unique_ssns = list(set([item['value'] for item in self.results['ssn']]))
            print(f"  Unique SSNs: {len(unique_ssns)}")
            for ssn in unique_ssns[:10]:  # Show first 10
                print(f"    - {ssn}")
            if len(unique_ssns) > 10:
                print(f"    ... and {len(unique_ssns) - 10} more")
        
        print(f"\nCredit Card Numbers: {len(self.results['credit_cards'])}")
        if self.results['credit_cards']:
            unique_ccs = list(set([item['value'] for item in self.results['credit_cards']]))
            print(f"  Unique Credit Cards: {len(unique_ccs)}")
            for cc in unique_ccs[:5]:  # Show first 5 (masked)
                masked = f"{cc[:4]}****{cc[-4:]}" if len(cc) >= 8 else "****"
                print(f"    - {masked}")
            if len(unique_ccs) > 5:
                print(f"    ... and {len(unique_ccs) - 5} more")
        
        print(f"\nAccount Numbers: {len(self.results['account_numbers'])}")
        if self.results['account_numbers']:
            unique_accounts = list(set([item['value'] for item in self.results['account_numbers']]))
            print(f"  Unique Account Numbers: {len(unique_accounts)}")
            for acc in unique_accounts[:10]:
                print(f"    - {acc}")
            if len(unique_accounts) > 10:
                print(f"    ... and {len(unique_accounts) - 10} more")
        
        print(f"\nRouting Numbers: {len(self.results['routing_numbers'])}")
        if self.results['routing_numbers']:
            unique_routing = list(set([item['value'] for item in self.results['routing_numbers']]))
            print(f"  Unique Routing Numbers: {len(unique_routing)}")
            for routing in unique_routing[:10]:
                print(f"    - {routing}")
            if len(unique_routing) > 10:
                print(f"    ... and {len(unique_routing) - 10} more")
        
        print(f"\n{'='*60}\n")


def main():
    """Main function to process CSV files"""
    if len(sys.argv) < 2:
        print("Usage: python process_csv.py <csv_file> [csv_file2] ...")
        print("\nExample:")
        print("  python process_csv.py myfile.csv")
        print("  python process_csv.py myfile.csv dlp_pci_small_csv.csv")
        sys.exit(1)
    
    files = sys.argv[1:]
    
    for filename in files:
        processor = CSVProcessor(filename)
        processor.process_file()
        processor.print_summary()


if __name__ == "__main__":
    main()
