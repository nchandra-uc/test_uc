#!/usr/bin/env python3
"""
Detailed analysis script for financial account data
"""

import re
import csv
from collections import defaultdict, Counter

def detailed_analyze_file(filename):
    """Perform detailed analysis of the financial account data"""
    
    results = {
        'account_numbers': [],
        'deposit_account_numbers': [],
        'routing_numbers': [],
        'bank_routing_numbers': [],
        'total_records': 0,
        'line_data': []
    }
    
    # Patterns for extraction
    account_pattern = r'Account\s*(?:\+A1:D42)?#:\s*(\d+)'
    deposit_pattern = r'Deposit\s+Account\s*#:\s*(\d+)'
    routing_pattern = r'Routing\s*#:\s*(\d+)'
    bank_routing_pattern = r'Bank\s+Routing\s*#:\s*(\d+)'
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            results['total_records'] += 1
            
            line_info = {
                'line': line_num,
                'accounts': [],
                'deposits': [],
                'routings': [],
                'bank_routings': []
            }
            
            # Extract Account Numbers
            account_matches = re.findall(account_pattern, line, re.IGNORECASE)
            for match in account_matches:
                acc_data = {'number': match, 'line': line_num}
                results['account_numbers'].append(acc_data)
                line_info['accounts'].append(match)
            
            # Extract Deposit Account Numbers
            deposit_matches = re.findall(deposit_pattern, line, re.IGNORECASE)
            for match in deposit_matches:
                dep_data = {'number': match, 'line': line_num}
                results['deposit_account_numbers'].append(dep_data)
                line_info['deposits'].append(match)
            
            # Extract Routing Numbers
            routing_matches = re.findall(routing_pattern, line, re.IGNORECASE)
            for match in routing_matches:
                rt_data = {'number': match, 'line': line_num}
                results['routing_numbers'].append(rt_data)
                line_info['routings'].append(match)
            
            # Extract Bank Routing Numbers
            bank_routing_matches = re.findall(bank_routing_pattern, line, re.IGNORECASE)
            for match in bank_routing_matches:
                brt_data = {'number': match, 'line': line_num}
                results['bank_routing_numbers'].append(brt_data)
                line_info['bank_routings'].append(match)
            
            results['line_data'].append(line_info)
    
    return results

def generate_detailed_report(results):
    """Generate comprehensive detailed report"""
    
    report = []
    report.append("=" * 80)
    report.append("DETAILED FINANCIAL ACCOUNT DATA ANALYSIS")
    report.append("=" * 80)
    report.append("")
    
    # Summary Statistics
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Records: {results['total_records']}")
    report.append(f"Total Account Numbers: {len(results['account_numbers'])}")
    report.append(f"Total Deposit Account Numbers: {len(results['deposit_account_numbers'])}")
    report.append(f"Total Routing Numbers: {len(results['routing_numbers'])}")
    report.append(f"Total Bank Routing Numbers: {len(results['bank_routing_numbers'])}")
    report.append("")
    
    # Account Number Analysis
    if results['account_numbers']:
        report.append("ACCOUNT NUMBER ANALYSIS")
        report.append("-" * 80)
        account_nums = [acc['number'] for acc in results['account_numbers']]
        lengths = [len(acc) for acc in account_nums]
        
        report.append(f"Total Count: {len(account_nums)}")
        report.append(f"Unique Count: {len(set(account_nums))}")
        report.append(f"Length: All are {lengths[0]} digits")
        report.append("")
        
        # Check for duplicates
        counter = Counter(account_nums)
        duplicates = {num: count for num, count in counter.items() if count > 1}
        if duplicates:
            report.append(f"⚠️  Duplicates Found: {len(duplicates)}")
            for num, count in list(duplicates.items())[:5]:
                report.append(f"   {num}: appears {count} times")
        else:
            report.append("✓ No duplicates found")
        report.append("")
    
    # Deposit Account Analysis
    if results['deposit_account_numbers']:
        report.append("DEPOSIT ACCOUNT NUMBER ANALYSIS")
        report.append("-" * 80)
        deposit_nums = [dep['number'] for dep in results['deposit_account_numbers']]
        lengths = [len(dep) for dep in deposit_nums]
        
        report.append(f"Total Count: {len(deposit_nums)}")
        report.append(f"Unique Count: {len(set(deposit_nums))}")
        report.append(f"Length: All are {lengths[0]} digits")
        report.append("")
        
        # Check for duplicates
        counter = Counter(deposit_nums)
        duplicates = {num: count for num, count in counter.items() if count > 1}
        if duplicates:
            report.append(f"⚠️  Duplicates Found: {len(duplicates)}")
            for num, count in list(duplicates.items())[:5]:
                report.append(f"   {num}: appears {count} times")
        else:
            report.append("✓ No duplicates found")
        report.append("")
    
    # Routing Number Analysis
    if results['routing_numbers']:
        report.append("ROUTING NUMBER ANALYSIS")
        report.append("-" * 80)
        routing_nums = [rt['number'] for rt in results['routing_numbers']]
        lengths = [len(rt) for rt in routing_nums]
        
        report.append(f"Total Count: {len(routing_nums)}")
        report.append(f"Unique Count: {len(set(routing_nums))}")
        report.append(f"Length: All are {lengths[0]} digits (standard US format)")
        report.append("")
        
        # Analyze routing number patterns (first 2 digits indicate Federal Reserve district)
        fed_districts = Counter([rt[:2] for rt in routing_nums])
        report.append("Federal Reserve District Distribution (first 2 digits):")
        for district, count in sorted(fed_districts.items())[:10]:
            report.append(f"   District {district}: {count} routing numbers")
        report.append("")
        
        # Check for duplicates
        counter = Counter(routing_nums)
        duplicates = {num: count for num, count in counter.items() if count > 1}
        if duplicates:
            report.append(f"⚠️  Duplicates Found: {len(duplicates)}")
            for num, count in list(duplicates.items())[:5]:
                report.append(f"   {num}: appears {count} times")
        else:
            report.append("✓ No duplicates found")
        report.append("")
    
    # Bank Routing Number Analysis
    if results['bank_routing_numbers']:
        report.append("BANK ROUTING NUMBER ANALYSIS")
        report.append("-" * 80)
        bank_routing_nums = [brt['number'] for brt in results['bank_routing_numbers']]
        
        report.append(f"Total Count: {len(bank_routing_nums)}")
        report.append(f"Unique Count: {len(set(bank_routing_nums))}")
        report.append("")
        
        # Check overlap with regular routing numbers
        routing_set = set([rt['number'] for rt in results['routing_numbers']])
        bank_routing_set = set(bank_routing_nums)
        overlap = routing_set & bank_routing_set
        if overlap:
            report.append(f"Note: {len(overlap)} bank routing numbers also appear as regular routing numbers")
        report.append("")
    
    # Data Structure Analysis
    report.append("DATA STRUCTURE ANALYSIS")
    report.append("-" * 80)
    
    # Count records with multiple accounts
    multi_account_lines = sum(1 for line in results['line_data'] if len(line['accounts']) > 1)
    report.append(f"Lines with multiple account numbers: {multi_account_lines}")
    
    # Count records with both account and deposit account
    mixed_lines = sum(1 for line in results['line_data'] 
                     if line['accounts'] and line['deposits'])
    report.append(f"Lines with both Account and Deposit Account: {mixed_lines}")
    
    # Count records with routing numbers
    routing_lines = sum(1 for line in results['line_data'] 
                       if line['routings'] or line['bank_routings'])
    report.append(f"Lines with routing numbers: {routing_lines}")
    report.append("")
    
    # Security and Compliance Notes
    report.append("SECURITY & COMPLIANCE NOTES")
    report.append("-" * 80)
    report.append("⚠️  This file contains sensitive financial information:")
    report.append("   - Account numbers (PII - Personally Identifiable Information)")
    report.append("   - Routing numbers (sensitive financial data)")
    report.append("   - Deposit account numbers (PII)")
    report.append("")
    report.append("Recommendations:")
    report.append("   1. Ensure proper access controls are in place")
    report.append("   2. Encrypt this data at rest and in transit")
    report.append("   3. Follow PCI-DSS and financial data protection regulations")
    report.append("   4. Implement data masking for non-production environments")
    report.append("   5. Maintain audit logs for access to this data")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)

if __name__ == "__main__":
    filename = "/workspace/myfile2.txt"
    print(f"Performing detailed analysis of: {filename}")
    print("")
    
    results = detailed_analyze_file(filename)
    report = generate_detailed_report(results)
    print(report)
    
    # Save detailed report
    with open("/workspace/detailed_analysis_report.txt", "w") as f:
        f.write(report)
    
    print("\nDetailed report saved to: detailed_analysis_report.txt")
