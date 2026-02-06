#!/usr/bin/env python3
"""
Script to analyze bank account and routing numbers from myfile2.txt
Extracts and structures the financial data for analysis.
"""

import re
import csv
from collections import defaultdict

def parse_bank_data(filename):
    """Parse bank account and routing numbers from the input file."""
    accounts = []
    routing_numbers = []
    all_data = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Split by tab
            parts = line.split('\t')
            
            row_accounts = []
            row_routings = []
            
            # Process each column
            for i, part in enumerate(parts):
                # Columns 1 and 2 contain account numbers (12 digits)
                if i < 2:
                    # Extract 12-digit account numbers
                    account_pattern = r'\b(\d{12})\b'
                    account_matches = re.findall(account_pattern, part)
                    row_accounts.extend(account_matches)
                
                # Column 3 contains routing numbers (9 digits)
                elif i == 2:
                    # Extract 9-digit routing numbers
                    routing_pattern = r'\b(\d{9})\b'
                    routing_matches = re.findall(routing_pattern, part)
                    row_routings.extend(routing_matches)
            
            # Store unique account and routing numbers
            for acc in row_accounts:
                if acc not in accounts:
                    accounts.append(acc)
            
            for rout in row_routings:
                if rout not in routing_numbers:
                    routing_numbers.append(rout)
            
            # Store row data
            if row_accounts or row_routings:
                all_data.append({
                    'accounts': row_accounts,
                    'routings': row_routings,
                    'raw_line': line
                })
    
    return accounts, routing_numbers, all_data

def analyze_data(accounts, routing_numbers, all_data):
    """Analyze the extracted data and generate statistics."""
    print("=" * 60)
    print("BANK ACCOUNT AND ROUTING NUMBERS ANALYSIS")
    print("=" * 60)
    print(f"\nTotal unique account numbers found: {len(accounts)}")
    print(f"Total unique routing numbers found: {len(routing_numbers)}")
    print(f"Total data rows processed: {len(all_data)}")
    
    # Account number length distribution
    account_lengths = defaultdict(int)
    for acc in accounts:
        account_lengths[len(acc)] += 1
    
    print("\nAccount Number Length Distribution:")
    for length, count in sorted(account_lengths.items()):
        print(f"  {length} digits: {count} accounts")
    
    # Routing number analysis (should all be 9 digits)
    print(f"\nRouting Number Analysis:")
    print(f"  All routing numbers are 9 digits: {all(len(r) == 9 for r in routing_numbers)}")
    
    # Sample data
    print("\nSample Account Numbers (first 10):")
    for i, acc in enumerate(accounts[:10], 1):
        print(f"  {i}. {acc}")
    
    print("\nSample Routing Numbers (first 10):")
    for i, rout in enumerate(routing_numbers[:10], 1):
        print(f"  {i}. {rout}")
    
    return {
        'total_accounts': len(accounts),
        'total_routings': len(routing_numbers),
        'total_rows': len(all_data),
        'account_lengths': dict(account_lengths)
    }

def export_to_csv(accounts, routing_numbers, all_data, output_file):
    """Export the data to a structured CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Row', 'Account_Number_1', 'Account_Number_2', 'Routing_Number', 'Notes'])
        
        for idx, row_data in enumerate(all_data, 1):
            accs = row_data['accounts']
            routs = row_data['routings']
            
            # Get up to 2 account numbers and 1 routing number per row
            acc1 = accs[0] if len(accs) > 0 else ''
            acc2 = accs[1] if len(accs) > 1 else ''
            rout = routs[0] if len(routs) > 0 else ''
            
            # Extract notes from raw line
            notes = ''
            if 'ABA' in row_data['raw_line'] or 'aba' in row_data['raw_line']:
                notes = 'ABA number'
            elif 'bank acct' in row_data['raw_line'].lower():
                notes = 'bank account'
            elif 'USA' in row_data['raw_line']:
                notes = 'USA'
            
            writer.writerow([idx, acc1, acc2, rout, notes])
    
    print(f"\nData exported to {output_file}")

def main():
    input_file = 'myfile2.txt'
    output_file = 'bank_accounts_analysis.csv'
    
    print("Parsing bank data from", input_file)
    accounts, routing_numbers, all_data = parse_bank_data(input_file)
    
    stats = analyze_data(accounts, routing_numbers, all_data)
    export_to_csv(accounts, routing_numbers, all_data, output_file)
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
