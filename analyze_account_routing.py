#!/usr/bin/env python3
"""
Analysis script for account and routing numbers data.
Parses the tab-separated data and provides comprehensive analysis.
"""

import re
import csv
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

def parse_line(line: str) -> Dict:
    """Parse a single line of the data file."""
    parts = line.strip().split('\t')
    if len(parts) < 3:
        return None
    
    # Extract account numbers (columns 1 and 2)
    account1 = parts[0] if len(parts) > 0 else ""
    account2 = parts[1] if len(parts) > 1 else ""
    routing = parts[2] if len(parts) > 2 else ""
    label = parts[3] if len(parts) > 3 else ""
    
    # Extract numeric values after colon (format: "X. Label: NUMBER")
    # Look for pattern: colon followed by space and then digits
    account1_match = re.search(r':\s*(\d+)', account1)
    account2_match = re.search(r':\s*(\d+)', account2)
    routing_match = re.search(r':\s*(\d+)', routing)
    
    # If no colon pattern, try to find the longest sequence of digits (at least 9 digits)
    if not account1_match:
        account1_match = re.search(r'(\d{9,})', account1)
    if not account2_match:
        account2_match = re.search(r'(\d{9,})', account2)
    if not routing_match:
        routing_match = re.search(r'(\d{9})', routing)  # Exactly 9 digits for routing
    
    return {
        'raw_account1': account1,
        'raw_account2': account2,
        'raw_routing': routing,
        'account1': account1_match.group(1) if account1_match else None,
        'account2': account2_match.group(1) if account2_match else None,
        'routing': routing_match.group(1) if routing_match else None,
        'label': label.strip(),
        'line': line.strip()
    }

def analyze_data(filename: str) -> Dict:
    """Analyze the account and routing numbers data."""
    results = {
        'total_records': 0,
        'account_numbers': [],
        'routing_numbers': [],
        'labels': [],
        'account_lengths': Counter(),
        'routing_lengths': Counter(),
        'account_patterns': Counter(),
        'routing_patterns': Counter(),
        'unique_accounts': set(),
        'unique_routings': set(),
        'duplicate_accounts': [],
        'duplicate_routings': [],
        'parsed_records': []
    }
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            parsed = parse_line(line)
            if not parsed:
                continue
            
            results['total_records'] += 1
            results['parsed_records'].append(parsed)
            
            # Collect account numbers
            if parsed['account1']:
                results['account_numbers'].append(parsed['account1'])
                results['unique_accounts'].add(parsed['account1'])
                results['account_lengths'][len(parsed['account1'])] += 1
                
            if parsed['account2']:
                results['account_numbers'].append(parsed['account2'])
                results['unique_accounts'].add(parsed['account2'])
                results['account_lengths'][len(parsed['account2'])] += 1
            
            # Collect routing numbers
            if parsed['routing']:
                results['routing_numbers'].append(parsed['routing'])
                results['unique_routings'].add(parsed['routing'])
                results['routing_lengths'][len(parsed['routing'])] += 1
            
            # Collect labels
            if parsed['label']:
                results['labels'].append(parsed['label'])
            
            # Analyze patterns
            if parsed['account1']:
                pattern = get_account_pattern(parsed['account1'])
                results['account_patterns'][pattern] += 1
            
            if parsed['routing']:
                pattern = get_routing_pattern(parsed['routing'])
                results['routing_patterns'][pattern] += 1
    
    # Find duplicates
    account_counter = Counter(results['account_numbers'])
    routing_counter = Counter(results['routing_numbers'])
    
    results['duplicate_accounts'] = [(acc, count) for acc, count in account_counter.items() if count > 1]
    results['duplicate_routings'] = [(rout, count) for rout, count in routing_counter.items() if count > 1]
    
    return results

def get_account_pattern(account: str) -> str:
    """Identify pattern in account number."""
    if len(account) == 12:
        return "12-digit"
    elif len(account) == 9:
        return "9-digit"
    elif len(account) == 10:
        return "10-digit"
    elif len(account) == 11:
        return "11-digit"
    else:
        return f"{len(account)}-digit"

def get_routing_pattern(routing: str) -> str:
    """Identify pattern in routing number."""
    if len(routing) == 9:
        return "9-digit (standard)"
    elif len(routing) == 8:
        return "8-digit"
    else:
        return f"{len(routing)}-digit"

def validate_routing_number(routing: str) -> bool:
    """Validate US routing number using checksum algorithm."""
    if len(routing) != 9:
        return False
    
    try:
        digits = [int(d) for d in routing]
        checksum = (3 * (digits[0] + digits[3] + digits[6]) +
                   7 * (digits[1] + digits[4] + digits[7]) +
                   1 * (digits[2] + digits[5] + digits[8])) % 10
        return checksum == 0
    except (ValueError, IndexError):
        return False

def generate_report(results: Dict) -> str:
    """Generate a comprehensive analysis report."""
    report = []
    report.append("=" * 80)
    report.append("ACCOUNT AND ROUTING NUMBERS ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Basic Statistics
    report.append("BASIC STATISTICS")
    report.append("-" * 80)
    report.append(f"Total Records: {results['total_records']}")
    report.append(f"Total Account Numbers Found: {len(results['account_numbers'])}")
    report.append(f"Unique Account Numbers: {len(results['unique_accounts'])}")
    report.append(f"Total Routing Numbers Found: {len(results['routing_numbers'])}")
    report.append(f"Unique Routing Numbers: {len(results['unique_routings'])}")
    report.append("")
    
    # Account Number Analysis
    report.append("ACCOUNT NUMBER ANALYSIS")
    report.append("-" * 80)
    report.append("Account Number Length Distribution:")
    for length, count in sorted(results['account_lengths'].items()):
        report.append(f"  {length} digits: {count} occurrences")
    report.append("")
    
    report.append("Account Number Patterns:")
    for pattern, count in sorted(results['account_patterns'].items(), key=lambda x: -x[1]):
        report.append(f"  {pattern}: {count} occurrences")
    report.append("")
    
    if results['duplicate_accounts']:
        report.append(f"Duplicate Account Numbers ({len(results['duplicate_accounts'])}):")
        for acc, count in sorted(results['duplicate_accounts'], key=lambda x: -x[1])[:10]:
            report.append(f"  {acc}: appears {count} times")
        if len(results['duplicate_accounts']) > 10:
            report.append(f"  ... and {len(results['duplicate_accounts']) - 10} more")
    else:
        report.append("No duplicate account numbers found.")
    report.append("")
    
    # Routing Number Analysis
    report.append("ROUTING NUMBER ANALYSIS")
    report.append("-" * 80)
    report.append("Routing Number Length Distribution:")
    for length, count in sorted(results['routing_lengths'].items()):
        report.append(f"  {length} digits: {count} occurrences")
    report.append("")
    
    report.append("Routing Number Patterns:")
    for pattern, count in sorted(results['routing_patterns'].items(), key=lambda x: -x[1]):
        report.append(f"  {pattern}: {count} occurrences")
    report.append("")
    
    # Validate routing numbers (9-digit standard)
    valid_routings = []
    invalid_routings = []
    for routing in results['unique_routings']:
        if len(routing) == 9:
            if validate_routing_number(routing):
                valid_routings.append(routing)
            else:
                invalid_routings.append(routing)
    
    report.append(f"Valid 9-digit Routing Numbers (checksum): {len(valid_routings)}")
    report.append(f"Invalid 9-digit Routing Numbers (checksum): {len(invalid_routings)}")
    if invalid_routings:
        report.append("Invalid routing numbers:")
        for rout in invalid_routings[:10]:
            report.append(f"  {rout}")
        if len(invalid_routings) > 10:
            report.append(f"  ... and {len(invalid_routings) - 10} more")
    report.append("")
    
    if results['duplicate_routings']:
        report.append(f"Duplicate Routing Numbers ({len(results['duplicate_routings'])}):")
        for rout, count in sorted(results['duplicate_routings'], key=lambda x: -x[1])[:10]:
            report.append(f"  {rout}: appears {count} times")
        if len(results['duplicate_routings']) > 10:
            report.append(f"  ... and {len(results['duplicate_routings']) - 10} more")
    else:
        report.append("No duplicate routing numbers found.")
    report.append("")
    
    # Label Analysis
    if results['labels']:
        report.append("LABEL ANALYSIS")
        report.append("-" * 80)
        label_counter = Counter(results['labels'])
        report.append("Labels found:")
        for label, count in sorted(label_counter.items(), key=lambda x: -x[1]):
            report.append(f"  '{label}': {count} occurrences")
        report.append("")
    
    # Sample Data
    report.append("SAMPLE RECORDS")
    report.append("-" * 80)
    for i, record in enumerate(results['parsed_records'][:5], 1):
        report.append(f"Record {i}:")
        report.append(f"  Account 1: {record['account1']} (from: {record['raw_account1']})")
        report.append(f"  Account 2: {record['account2']} (from: {record['raw_account2']})")
        report.append(f"  Routing: {record['routing']} (from: {record['raw_routing']})")
        if record['label']:
            report.append(f"  Label: {record['label']}")
        report.append("")
    
    report.append("=" * 80)
    return "\n".join(report)

def export_to_csv(results: Dict, output_file: str):
    """Export parsed data to CSV format."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Record #', 'Account 1', 'Account 2', 'Routing Number', 'Label'])
        
        for i, record in enumerate(results['parsed_records'], 1):
            writer.writerow([
                i,
                record['account1'] or '',
                record['account2'] or '',
                record['routing'] or '',
                record['label']
            ])

if __name__ == "__main__":
    input_file = "myfile2.txt"
    output_csv = "account_routing_analysis.csv"
    output_report = "analysis_report.txt"
    
    print(f"Analyzing data from {input_file}...")
    results = analyze_data(input_file)
    
    # Generate and save report
    report = generate_report(results)
    print(report)
    
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Export to CSV
    export_to_csv(results, output_csv)
    
    print(f"\nAnalysis complete!")
    print(f"Report saved to: {output_report}")
    print(f"CSV export saved to: {output_csv}")
