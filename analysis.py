#!/usr/bin/env python3
"""
Analysis script for bank account and routing numbers data.
"""

import csv
from collections import Counter, defaultdict

def analyze_bank_data(csv_file):
    """Analyze bank account and routing number data."""
    
    accounts_1 = []
    accounts_2 = []
    routing_numbers = []
    account_types_1 = []
    account_types_2 = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts_1.append(row['Account_Number_1'])
            accounts_2.append(row['Account_Number_2'])
            routing_numbers.append(row['Routing_Number'])
            account_types_1.append(row['Account_Type_1'])
            account_types_2.append(row['Account_Type_2'])
    
    # Analysis results
    results = {
        'total_rows': len(accounts_1),
        'unique_accounts_1': len(set(accounts_1)),
        'unique_accounts_2': len(set(accounts_2)),
        'unique_routing_numbers': len(set(routing_numbers)),
        'total_unique_accounts': len(set(accounts_1 + accounts_2)),
        'account_type_1_distribution': dict(Counter(account_types_1)),
        'account_type_2_distribution': dict(Counter(account_types_2)),
        'routing_number_frequency': dict(Counter(routing_numbers)),
        'duplicate_routing_numbers': {k: v for k, v in Counter(routing_numbers).items() if v > 1},
        'account_lengths_1': [len(acc) for acc in accounts_1],
        'account_lengths_2': [len(acc) for acc in accounts_2],
        'routing_lengths': [len(rt) for rt in routing_numbers],
    }
    
    return results

def generate_report(results):
    """Generate a formatted analysis report."""
    
    report = []
    report.append("=" * 70)
    report.append("BANK ACCOUNT AND ROUTING NUMBERS DATA ANALYSIS")
    report.append("=" * 70)
    report.append("")
    
    report.append("SUMMARY STATISTICS:")
    report.append("-" * 70)
    report.append(f"Total Rows: {results['total_rows']}")
    report.append(f"Unique Account Numbers (Column 1): {results['unique_accounts_1']}")
    report.append(f"Unique Account Numbers (Column 2): {results['unique_accounts_2']}")
    report.append(f"Total Unique Account Numbers: {results['total_unique_accounts']}")
    report.append(f"Unique Routing Numbers: {results['unique_routing_numbers']}")
    report.append("")
    
    report.append("ACCOUNT TYPE DISTRIBUTION:")
    report.append("-" * 70)
    report.append("Column 1 Account Types:")
    for acc_type, count in results['account_type_1_distribution'].items():
        report.append(f"  {acc_type}: {count}")
    report.append("")
    report.append("Column 2 Account Types:")
    for acc_type, count in results['account_type_2_distribution'].items():
        report.append(f"  {acc_type}: {count}")
    report.append("")
    
    report.append("ACCOUNT NUMBER LENGTH ANALYSIS:")
    report.append("-" * 70)
    lengths_1 = Counter(results['account_lengths_1'])
    lengths_2 = Counter(results['account_lengths_2'])
    report.append("Column 1 Account Lengths:")
    for length, count in sorted(lengths_1.items()):
        report.append(f"  {length} digits: {count} accounts")
    report.append("")
    report.append("Column 2 Account Lengths:")
    for length, count in sorted(lengths_2.items()):
        report.append(f"  {length} digits: {count} accounts")
    report.append("")
    
    report.append("ROUTING NUMBER ANALYSIS:")
    report.append("-" * 70)
    routing_lengths = Counter(results['routing_lengths'])
    report.append("Routing Number Lengths:")
    for length, count in sorted(routing_lengths.items()):
        report.append(f"  {length} digits: {count} routing numbers")
    report.append("")
    
    if results['duplicate_routing_numbers']:
        report.append("DUPLICATE ROUTING NUMBERS:")
        report.append("-" * 70)
        for routing_num, count in sorted(results['duplicate_routing_numbers'].items(), 
                                        key=lambda x: x[1], reverse=True):
            report.append(f"  {routing_num}: appears {count} times")
        report.append("")
    else:
        report.append("No duplicate routing numbers found.")
        report.append("")
    
    report.append("=" * 70)
    
    return "\n".join(report)

if __name__ == "__main__":
    csv_file = "bank_accounts_routing_numbers.csv"
    results = analyze_bank_data(csv_file)
    report = generate_report(results)
    
    print(report)
    
    # Save report to file
    with open("analysis_report.txt", "w") as f:
        f.write(report)
    
    print("\nReport saved to analysis_report.txt")
