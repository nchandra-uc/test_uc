#!/usr/bin/env python3
"""
Analysis script for financial account data in myfile.csv
Extracts and analyzes Account Numbers, Deposit Account Numbers, and Routing Numbers
"""

import re
import csv
from collections import defaultdict

def analyze_file(filename):
    """Analyze the CSV file for financial account information"""
    
    results = {
        'account_numbers': [],
        'deposit_account_numbers': [],
        'routing_numbers': [],
        'bank_routing_numbers': [],
        'aba_numbers': [],
        'total_records': 0,
        'patterns': defaultdict(int)
    }
    
    # Patterns for extraction
    account_pattern = r'Account\s*(?:\+A1:D42)?#:\s*(\d+)'
    deposit_pattern = r'Deposit\s+Account\s*#:\s*(\d+)'
    routing_pattern = r'Routing\s*#:\s*(\d+)'
    bank_routing_pattern = r'Bank\s+Routing\s*#:\s*(\d+)'
    aba_pattern = r'ABA\s+number'
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            results['total_records'] += 1
            
            # Extract Account Numbers
            account_matches = re.findall(account_pattern, line, re.IGNORECASE)
            for match in account_matches:
                results['account_numbers'].append({
                    'number': match,
                    'line': line_num,
                    'type': 'Account'
                })
            
            # Extract Deposit Account Numbers
            deposit_matches = re.findall(deposit_pattern, line, re.IGNORECASE)
            for match in deposit_matches:
                results['deposit_account_numbers'].append({
                    'number': match,
                    'line': line_num,
                    'type': 'Deposit Account'
                })
            
            # Extract Routing Numbers
            routing_matches = re.findall(routing_pattern, line, re.IGNORECASE)
            for match in routing_matches:
                results['routing_numbers'].append({
                    'number': match,
                    'line': line_num,
                    'type': 'Routing'
                })
            
            # Extract Bank Routing Numbers
            bank_routing_matches = re.findall(bank_routing_pattern, line, re.IGNORECASE)
            for match in bank_routing_matches:
                results['bank_routing_numbers'].append({
                    'number': match,
                    'line': line_num,
                    'type': 'Bank Routing'
                })
            
            # Check for ABA number mentions
            if re.search(aba_pattern, line, re.IGNORECASE):
                results['aba_numbers'].append({
                    'line': line_num,
                    'content': line.strip()
                })
    
    return results

def generate_report(results):
    """Generate a comprehensive analysis report"""
    
    report = []
    report.append("=" * 80)
    report.append("FINANCIAL ACCOUNT DATA ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary Statistics
    report.append("SUMMARY STATISTICS")
    report.append("-" * 80)
    report.append(f"Total Records Analyzed: {results['total_records']}")
    report.append(f"Account Numbers Found: {len(results['account_numbers'])}")
    report.append(f"Deposit Account Numbers Found: {len(results['deposit_account_numbers'])}")
    report.append(f"Routing Numbers Found: {len(results['routing_numbers'])}")
    report.append(f"Bank Routing Numbers Found: {len(results['bank_routing_numbers'])}")
    report.append(f"ABA Number References: {len(results['aba_numbers'])}")
    report.append("")
    
    # Account Number Analysis
    if results['account_numbers']:
        report.append("ACCOUNT NUMBERS")
        report.append("-" * 80)
        account_lengths = [len(acc['number']) for acc in results['account_numbers']]
        report.append(f"Count: {len(results['account_numbers'])}")
        report.append(f"Length Range: {min(account_lengths)} - {max(account_lengths)} digits")
        report.append(f"Average Length: {sum(account_lengths) / len(account_lengths):.1f} digits")
        report.append("")
        report.append("Sample Account Numbers (first 10):")
        for acc in results['account_numbers'][:10]:
            report.append(f"  Line {acc['line']}: {acc['number']}")
        report.append("")
    
    # Deposit Account Number Analysis
    if results['deposit_account_numbers']:
        report.append("DEPOSIT ACCOUNT NUMBERS")
        report.append("-" * 80)
        deposit_lengths = [len(dep['number']) for dep in results['deposit_account_numbers']]
        report.append(f"Count: {len(results['deposit_account_numbers'])}")
        report.append(f"Length Range: {min(deposit_lengths)} - {max(deposit_lengths)} digits")
        report.append(f"Average Length: {sum(deposit_lengths) / len(deposit_lengths):.1f} digits")
        report.append("")
        report.append("Sample Deposit Account Numbers (first 10):")
        for dep in results['deposit_account_numbers'][:10]:
            report.append(f"  Line {dep['line']}: {dep['number']}")
        report.append("")
    
    # Routing Number Analysis
    if results['routing_numbers']:
        report.append("ROUTING NUMBERS")
        report.append("-" * 80)
        routing_lengths = [len(rt['number']) for rt in results['routing_numbers']]
        report.append(f"Count: {len(results['routing_numbers'])}")
        report.append(f"Length Range: {min(routing_lengths)} - {max(routing_lengths)} digits")
        report.append(f"Average Length: {sum(routing_lengths) / len(routing_lengths):.1f} digits")
        report.append("")
        report.append("Sample Routing Numbers (first 10):")
        for rt in results['routing_numbers'][:10]:
            report.append(f"  Line {rt['line']}: {rt['number']}")
        report.append("")
    
    # Bank Routing Number Analysis
    if results['bank_routing_numbers']:
        report.append("BANK ROUTING NUMBERS")
        report.append("-" * 80)
        bank_routing_lengths = [len(brt['number']) for brt in results['bank_routing_numbers']]
        report.append(f"Count: {len(results['bank_routing_numbers'])}")
        report.append(f"Length Range: {min(bank_routing_lengths)} - {max(bank_routing_lengths)} digits")
        report.append(f"Average Length: {sum(bank_routing_lengths) / len(bank_routing_lengths):.1f} digits")
        report.append("")
        report.append("Sample Bank Routing Numbers (first 10):")
        for brt in results['bank_routing_numbers'][:10]:
            report.append(f"  Line {brt['line']}: {brt['number']}")
        report.append("")
    
    # Data Quality Checks
    report.append("DATA QUALITY ANALYSIS")
    report.append("-" * 80)
    
    # Check for duplicate account numbers
    account_nums = [acc['number'] for acc in results['account_numbers']]
    duplicates = [num for num in set(account_nums) if account_nums.count(num) > 1]
    if duplicates:
        report.append(f"⚠️  WARNING: Found {len(duplicates)} duplicate account numbers")
        report.append(f"   Examples: {', '.join(duplicates[:5])}")
    else:
        report.append("✓ No duplicate account numbers found")
    
    # Check routing number format (should be 9 digits for US)
    invalid_routing = []
    all_routing = [rt['number'] for rt in results['routing_numbers']] + \
                  [brt['number'] for brt in results['bank_routing_numbers']]
    for rt in all_routing:
        if len(rt) != 9:
            invalid_routing.append(rt)
    
    if invalid_routing:
        report.append(f"⚠️  WARNING: Found {len(invalid_routing)} routing numbers with non-standard length")
        report.append(f"   Examples: {', '.join(invalid_routing[:5])}")
    else:
        report.append("✓ All routing numbers have standard 9-digit format")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

if __name__ == "__main__":
    filename = "/workspace/myfile2.txt"
    print(f"Analyzing file: {filename}")
    print("")
    
    results = analyze_file(filename)
    report = generate_report(results)
    print(report)
    
    # Save report to file
    with open("/workspace/analysis_report.txt", "w") as f:
        f.write(report)
    
    print("\nReport saved to: analysis_report.txt")
