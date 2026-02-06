#!/usr/bin/env python3
"""
Analysis script for account and routing numbers in myfile2.txt
This script provides comprehensive analysis of the financial data.
"""

import re
from collections import defaultdict, Counter
from typing import List, Dict, Tuple

def analyze_file(filepath: str = 'myfile2.txt') -> Dict:
    """Analyze the account and routing numbers file."""
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Data structures
    account_numbers = []
    routing_numbers = []
    account_types = defaultdict(int)
    routing_types = defaultdict(int)
    metadata_tags = []
    line_structures = []
    
    # Parse each line
    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
        
        # Extract account numbers (handles various formats)
        account_matches = re.findall(
            r'(?:Account|Deposit Account)\s*\+?[A-Z0-9:]*\s*#?\s*:\s*(\d+)', 
            line, 
            re.IGNORECASE
        )
        account_numbers.extend(account_matches)
        
        # Extract routing numbers
        routing_matches = re.findall(
            r'(?:Routing|Bank Routing)\s*#?\s*:\s*(\d+)', 
            line, 
            re.IGNORECASE
        )
        routing_numbers.extend(routing_matches)
        
        # Count account types
        if 'Deposit Account' in line:
            account_types['Deposit Account'] += 1
        elif 'Account' in line:
            account_types['Account'] += 1
        
        # Count routing types
        if 'Bank Routing' in line:
            routing_types['Bank Routing'] += 1
        elif 'Routing' in line:
            routing_types['Routing'] += 1
        
        # Extract metadata tags
        metadata = re.findall(r'\b(ABA number|aba numbers|bank acct\.?\s*no\.?|USA)\b', line, re.IGNORECASE)
        metadata_tags.extend(metadata)
        
        # Analyze line structure
        parts = line.split('\t')
        line_structures.append({
            'line_num': line_num,
            'parts_count': len(parts),
            'has_account': bool(account_matches),
            'has_routing': bool(routing_matches),
            'has_metadata': bool(metadata)
        })
    
    # Analyze account numbers
    account_lengths = Counter(len(acc) for acc in account_numbers)
    unique_accounts = len(set(account_numbers))
    duplicate_accounts = len(account_numbers) - unique_accounts
    
    # Analyze routing numbers
    routing_lengths = Counter(len(rout) for rout in routing_numbers)
    unique_routings = len(set(routing_numbers))
    duplicate_routings = len(routing_numbers) - unique_routings
    
    # Routing number validation (US routing numbers are 9 digits)
    valid_routing_count = sum(1 for rout in routing_numbers if len(rout) == 9)
    
    # Account number patterns
    account_patterns = {
        'starts_with_zero': sum(1 for acc in account_numbers if acc.startswith('0')),
        'all_digits_same': sum(1 for acc in account_numbers if len(set(acc)) == 1),
        'has_repeating_pattern': sum(1 for acc in account_numbers if len(set(acc)) < len(acc) * 0.5)
    }
    
    return {
        'file_info': {
            'total_lines': len([l for l in lines if l.strip()]),
            'total_bytes': sum(len(l) for l in lines)
        },
        'account_numbers': {
            'total': len(account_numbers),
            'unique': unique_accounts,
            'duplicates': duplicate_accounts,
            'length_distribution': dict(account_lengths),
            'types': dict(account_types),
            'patterns': account_patterns
        },
        'routing_numbers': {
            'total': len(routing_numbers),
            'unique': unique_routings,
            'duplicates': duplicate_routings,
            'length_distribution': dict(routing_lengths),
            'types': dict(routing_types),
            'valid_9_digit_count': valid_routing_count
        },
        'metadata': {
            'tags_found': dict(Counter(metadata_tags)),
            'total_tags': len(metadata_tags)
        },
        'line_structures': line_structures
    }

def print_analysis(results: Dict):
    """Print formatted analysis results."""
    
    print("=" * 70)
    print("ACCOUNT AND ROUTING NUMBERS DATA ANALYSIS")
    print("=" * 70)
    
    # File Information
    print(f"\n📄 FILE INFORMATION")
    print(f"   Total lines: {results['file_info']['total_lines']}")
    print(f"   Total size: {results['file_info']['total_bytes']:,} bytes")
    
    # Account Numbers Analysis
    print(f"\n💳 ACCOUNT NUMBERS ANALYSIS")
    print(f"   Total account numbers: {results['account_numbers']['total']}")
    print(f"   Unique account numbers: {results['account_numbers']['unique']}")
    print(f"   Duplicate account numbers: {results['account_numbers']['duplicates']}")
    print(f"   Account number types:")
    for acc_type, count in results['account_numbers']['types'].items():
        print(f"     - {acc_type}: {count}")
    print(f"   Length distribution:")
    for length, count in sorted(results['account_numbers']['length_distribution'].items()):
        print(f"     - {length} digits: {count} numbers")
    print(f"   Patterns:")
    print(f"     - Starting with zero: {results['account_numbers']['patterns']['starts_with_zero']}")
    print(f"     - All digits same: {results['account_numbers']['patterns']['all_digits_same']}")
    
    # Routing Numbers Analysis
    print(f"\n🏦 ROUTING NUMBERS ANALYSIS")
    print(f"   Total routing numbers: {results['routing_numbers']['total']}")
    print(f"   Unique routing numbers: {results['routing_numbers']['unique']}")
    print(f"   Duplicate routing numbers: {results['routing_numbers']['duplicates']}")
    print(f"   Routing number types:")
    for rout_type, count in results['routing_numbers']['types'].items():
        print(f"     - {rout_type}: {count}")
    print(f"   Length distribution:")
    for length, count in sorted(results['routing_numbers']['length_distribution'].items()):
        print(f"     - {length} digits: {count} numbers")
    print(f"   Valid 9-digit routing numbers: {results['routing_numbers']['valid_9_digit_count']}")
    
    # Metadata Analysis
    print(f"\n🏷️  METADATA ANALYSIS")
    print(f"   Total metadata tags: {results['metadata']['total_tags']}")
    if results['metadata']['tags_found']:
        print(f"   Tags found:")
        for tag, count in results['metadata']['tags_found'].items():
            print(f"     - '{tag}': {count}")
    
    # Data Structure Analysis
    print(f"\n📊 DATA STRUCTURE")
    avg_parts = sum(s['parts_count'] for s in results['line_structures']) / len(results['line_structures'])
    print(f"   Average parts per line: {avg_parts:.1f}")
    print(f"   Lines with account numbers: {sum(1 for s in results['line_structures'] if s['has_account'])}")
    print(f"   Lines with routing numbers: {sum(1 for s in results['line_structures'] if s['has_routing'])}")
    print(f"   Lines with metadata: {sum(1 for s in results['line_structures'] if s['has_metadata'])}")
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    results = analyze_file('myfile2.txt')
    print_analysis(results)
