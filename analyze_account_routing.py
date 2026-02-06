#!/usr/bin/env python3
"""
Analysis script for account and routing number data in myfile2.txt
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

def parse_file(filename: str) -> List[Dict]:
    """Parse the file and extract account and routing numbers."""
    records = []
    
    with open(filename, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # Split by tab
            parts = line.split('\t')
            
            # Extract account numbers (various formats)
            account_patterns = [
                r'Account\s*\+?[A-Z0-9:]*#:\s*(\d+)',
                r'Deposit\s+Account\s*#:\s*(\d+)',
                r'Account\s*#:\s*(\d+)',
            ]
            
            # Extract routing numbers
            routing_patterns = [
                r'Routing\s*#:\s*(\d+)',
                r'Bank\s+Routing\s*#:\s*(\d+)',
            ]
            
            accounts = []
            routings = []
            
            for part in parts:
                # Find account numbers
                for pattern in account_patterns:
                    matches = re.findall(pattern, part, re.IGNORECASE)
                    accounts.extend(matches)
                
                # Find routing numbers
                for pattern in routing_patterns:
                    matches = re.findall(pattern, part, re.IGNORECASE)
                    routings.extend(matches)
            
            if accounts or routings:
                records.append({
                    'line': line_num,
                    'raw': line,
                    'accounts': accounts,
                    'routings': routings,
                    'parts': parts
                })
    
    return records

def analyze_accounts(records: List[Dict]) -> Dict:
    """Analyze account number patterns."""
    all_accounts = []
    account_lengths = []
    
    for record in records:
        all_accounts.extend(record['accounts'])
        account_lengths.extend([len(acc) for acc in record['accounts']])
    
    analysis = {
        'total_unique': len(set(all_accounts)),
        'total_count': len(all_accounts),
        'length_distribution': Counter(account_lengths),
        'duplicates': [acc for acc, count in Counter(all_accounts).items() if count > 1],
        'sample_accounts': all_accounts[:10]
    }
    
    return analysis

def analyze_routings(records: List[Dict]) -> Dict:
    """Analyze routing number patterns."""
    all_routings = []
    routing_lengths = []
    
    for record in records:
        all_routings.extend(record['routings'])
        routing_lengths.extend([len(rt) for rt in record['routings']])
    
    analysis = {
        'total_unique': len(set(all_routings)),
        'total_count': len(all_routings),
        'length_distribution': Counter(routing_lengths),
        'duplicates': [rt for rt, count in Counter(all_routings).items() if count > 1],
        'sample_routings': all_routings[:10]
    }
    
    return analysis

def analyze_structure(records: List[Dict]) -> Dict:
    """Analyze the structure and format of the data."""
    structure_analysis = {
        'total_records': len(records),
        'records_with_accounts': sum(1 for r in records if r['accounts']),
        'records_with_routings': sum(1 for r in records if r['routings']),
        'records_with_both': sum(1 for r in records if r['accounts'] and r['routings']),
        'accounts_per_record': [len(r['accounts']) for r in records],
        'routings_per_record': [len(r['routings']) for r in records],
        'column_count_distribution': Counter([len(r['parts']) for r in records])
    }
    
    return structure_analysis

def generate_report(records: List[Dict], account_analysis: Dict, routing_analysis: Dict, structure_analysis: Dict) -> str:
    """Generate a comprehensive analysis report."""
    report = []
    report.append("=" * 80)
    report.append("ACCOUNT AND ROUTING NUMBER DATA ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # File Overview
    report.append("## FILE OVERVIEW")
    report.append("-" * 80)
    report.append(f"Total Records Analyzed: {structure_analysis['total_records']}")
    report.append(f"Records with Account Numbers: {structure_analysis['records_with_accounts']}")
    report.append(f"Records with Routing Numbers: {structure_analysis['records_with_routings']}")
    report.append(f"Records with Both: {structure_analysis['records_with_both']}")
    report.append("")
    
    # Account Number Analysis
    report.append("## ACCOUNT NUMBER ANALYSIS")
    report.append("-" * 80)
    report.append(f"Total Account Numbers Found: {account_analysis['total_count']}")
    report.append(f"Unique Account Numbers: {account_analysis['total_unique']}")
    report.append(f"Duplicate Account Numbers: {len(account_analysis['duplicates'])}")
    if account_analysis['duplicates']:
        report.append(f"  Examples: {', '.join(account_analysis['duplicates'][:5])}")
    report.append("")
    report.append("Account Number Length Distribution:")
    for length, count in sorted(account_analysis['length_distribution'].items()):
        report.append(f"  {length} digits: {count} accounts")
    report.append("")
    report.append("Sample Account Numbers:")
    for acc in account_analysis['sample_accounts'][:10]:
        report.append(f"  {acc}")
    report.append("")
    
    # Routing Number Analysis
    report.append("## ROUTING NUMBER ANALYSIS")
    report.append("-" * 80)
    report.append(f"Total Routing Numbers Found: {routing_analysis['total_count']}")
    report.append(f"Unique Routing Numbers: {routing_analysis['total_unique']}")
    report.append(f"Duplicate Routing Numbers: {len(routing_analysis['duplicates'])}")
    if routing_analysis['duplicates']:
        report.append(f"  Examples: {', '.join(routing_analysis['duplicates'][:5])}")
    report.append("")
    report.append("Routing Number Length Distribution:")
    for length, count in sorted(routing_analysis['length_distribution'].items()):
        report.append(f"  {length} digits: {count} routings")
    report.append("")
    report.append("Sample Routing Numbers:")
    for rt in routing_analysis['sample_routings'][:10]:
        report.append(f"  {rt}")
    report.append("")
    
    # Data Structure Analysis
    report.append("## DATA STRUCTURE ANALYSIS")
    report.append("-" * 80)
    report.append("Column Count Distribution:")
    for cols, count in sorted(structure_analysis['column_count_distribution'].items()):
        report.append(f"  {cols} columns: {count} records")
    report.append("")
    report.append("Accounts per Record Statistics:")
    acc_per_rec = structure_analysis['accounts_per_record']
    if acc_per_rec:
        report.append(f"  Min: {min(acc_per_rec)}, Max: {max(acc_per_rec)}, Avg: {sum(acc_per_rec)/len(acc_per_rec):.2f}")
    report.append("")
    report.append("Routings per Record Statistics:")
    rt_per_rec = structure_analysis['routings_per_record']
    if rt_per_rec:
        report.append(f"  Min: {min(rt_per_rec)}, Max: {max(rt_per_rec)}, Avg: {sum(rt_per_rec)/len(rt_per_rec):.2f}")
    report.append("")
    
    # Format Patterns
    report.append("## FORMAT PATTERNS IDENTIFIED")
    report.append("-" * 80)
    report.append("Account Number Formats Found:")
    report.append("  - 'Account #: <number>'")
    report.append("  - 'Deposit Account #: <number>'")
    report.append("  - 'Account +A1:D42#: <number>' (spreadsheet reference)")
    report.append("")
    report.append("Routing Number Formats Found:")
    report.append("  - 'Routing #: <number>'")
    report.append("  - 'Bank Routing #: <number>'")
    report.append("")
    
    # Data Quality Observations
    report.append("## DATA QUALITY OBSERVATIONS")
    report.append("-" * 80)
    
    # Check for valid US routing numbers (9 digits)
    valid_routing_count = sum(1 for rt in routing_analysis['sample_routings'] if len(rt) == 9)
    report.append(f"US Routing Number Format (9 digits): {valid_routing_count}/{len(routing_analysis['sample_routings'])} in sample")
    
    # Check account number lengths (typically 10-17 digits)
    valid_account_count = sum(1 for acc in account_analysis['sample_accounts'] if 10 <= len(acc) <= 17)
    report.append(f"Typical Account Number Length (10-17 digits): {valid_account_count}/{len(account_analysis['sample_accounts'])} in sample")
    
    report.append("")
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    """Main analysis function."""
    filename = 'myfile2.txt'
    
    print(f"Analyzing file: {filename}")
    records = parse_file(filename)
    
    print(f"Parsed {len(records)} records")
    
    account_analysis = analyze_accounts(records)
    routing_analysis = analyze_routings(records)
    structure_analysis = analyze_structure(records)
    
    report = generate_report(records, account_analysis, routing_analysis, structure_analysis)
    
    # Print to console
    print("\n" + report)
    
    # Save to file
    output_file = 'account_routing_analysis_report.txt'
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_file}")
    
    # Also create a CSV summary
    csv_output = 'account_routing_summary.csv'
    with open(csv_output, 'w') as f:
        f.write("Record_Number,Account_Count,Routing_Count,Account_Numbers,Routing_Numbers\n")
        for record in records:
            accounts_str = ';'.join(record['accounts'])
            routings_str = ';'.join(record['routings'])
            f.write(f"{record['line']},{len(record['accounts'])},{len(record['routings'])},\"{accounts_str}\",\"{routings_str}\"\n")
    
    print(f"CSV summary saved to: {csv_output}")

if __name__ == '__main__':
    main()
