#!/usr/bin/env python3
"""
CSV File Analyzer for Sensitive Data Detection
Detects account numbers, routing numbers, SSNs, and other sensitive information
"""

import csv
import re
import sys
from typing import List, Dict, Tuple
from collections import defaultdict

class CSVAnalyzer:
    def __init__(self):
        # Patterns for sensitive data detection
        self.patterns = {
            'ssn': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # Standard SSN format: 123-45-6789
                r'\b\d{3}\s\d{2}\s\d{4}\b',  # SSN with spaces: 123 45 6789
                r'\b\d{9}\b',  # 9 consecutive digits (potential SSN)
            ],
            'account_number': [
                r'\b\d{10,12}\b',  # 10-12 digit account numbers
                r'Account\s*#?\s*:?\s*(\d{10,12})',  # Account #: 1234567890
                r'Deposit\s+Account\s*#?\s*:?\s*(\d{10,12})',  # Deposit Account #: 1234567890
            ],
            'routing_number': [
                r'\b\d{9}\b',  # 9 digit routing numbers
                r'Routing\s*#?\s*:?\s*(\d{9})',  # Routing #: 123456789
                r'Bank\s+Routing\s*#?\s*:?\s*(\d{9})',  # Bank Routing #: 123456789
                r'ABA\s+number\s*:?\s*(\d{9})',  # ABA number: 123456789
            ],
            'credit_card': [
                r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card format
            ],
            'phone': [
                r'\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b',  # Phone numbers
            ],
        }
    
    def detect_pattern(self, text: str, pattern: str) -> List[str]:
        """Detect matches for a given pattern in text"""
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches if isinstance(matches, list) else [matches] if matches else []
    
    def analyze_cell(self, cell_value: str) -> Dict[str, List[str]]:
        """Analyze a single cell for sensitive data"""
        findings = defaultdict(list)
        
        if not cell_value or not isinstance(cell_value, str):
            return findings
        
        for data_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = self.detect_pattern(cell_value, pattern)
                if matches:
                    # Filter out matches that are too short or common false positives
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0] if match[0] else match
                        if match and len(str(match).replace('-', '').replace(' ', '')) >= 9:
                            findings[data_type].append(str(match))
        
        return findings
    
    def analyze_csv(self, file_path: str) -> Dict:
        """Analyze a CSV file for sensitive data"""
        results = {
            'file': file_path,
            'total_rows': 0,
            'findings': defaultdict(lambda: {'count': 0, 'locations': []}),
            'row_details': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(f, delimiter=delimiter)
                headers = next(reader, None)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    results['total_rows'] += 1
                    row_findings = defaultdict(list)
                    
                    for col_num, cell in enumerate(row):
                        cell_findings = self.analyze_cell(cell)
                        for data_type, matches in cell_findings.items():
                            for match in matches:
                                results['findings'][data_type]['count'] += 1
                                location = {
                                    'row': row_num,
                                    'column': headers[col_num] if headers and col_num < len(headers) else f'Column {col_num + 1}',
                                    'value': match,
                                    'cell_content': cell[:100]  # First 100 chars of cell
                                }
                                results['findings'][data_type]['locations'].append(location)
                                row_findings[data_type].extend(matches)
                    
                    if row_findings:
                        results['row_details'].append({
                            'row': row_num,
                            'findings': dict(row_findings)
                        })
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def print_report(self, results: Dict):
        """Print a formatted report of findings"""
        print(f"\n{'='*60}")
        print(f"CSV Analysis Report: {results['file']}")
        print(f"{'='*60}")
        print(f"Total Rows Analyzed: {results['total_rows']}")
        
        if 'error' in results:
            print(f"\nError: {results['error']}")
            return
        
        if not results['findings']:
            print("\n✓ No sensitive data patterns detected.")
            return
        
        print(f"\n{'='*60}")
        print("SENSITIVE DATA DETECTED:")
        print(f"{'='*60}")
        
        for data_type, data in results['findings'].items():
            count = data['count']
            print(f"\n{data_type.upper().replace('_', ' ')}: {count} occurrence(s)")
            print("-" * 60)
            
            # Show first 10 locations
            for i, location in enumerate(data['locations'][:10], 1):
                print(f"  {i}. Row {location['row']}, {location['column']}")
                print(f"     Value: {location['value']}")
                if len(location['cell_content']) > 50:
                    print(f"     Context: ...{location['cell_content'][-50:]}")
                else:
                    print(f"     Context: {location['cell_content']}")
            
            if len(data['locations']) > 10:
                print(f"  ... and {len(data['locations']) - 10} more occurrence(s)")
        
        print(f"\n{'='*60}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python csv_analyzer.py <csv_file_path>")
        print("Example: python csv_analyzer.py myfile.csv")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyzer = CSVAnalyzer()
    results = analyzer.analyze_csv(file_path)
    analyzer.print_report(results)
    
    # Return exit code based on findings
    if results.get('findings'):
        sys.exit(1)  # Exit with error if sensitive data found
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
