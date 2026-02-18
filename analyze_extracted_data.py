#!/usr/bin/env python3
"""
Analyze extracted financial data from text files or structured data.
This script can analyze data that has already been extracted from images.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict


class FinancialDataAnalyzer:
    """Analyzes extracted financial data (account numbers, routing numbers)."""
    
    def __init__(self):
        self.records = []
        self.account_numbers = set()
        self.routing_numbers = set()
        self.pairs = []
        
    def parse_text_file(self, file_path: str) -> List[Dict]:
        """Parse a text file containing financial data."""
        records = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Split by tabs or multiple spaces
            parts = re.split(r'[\t\s]{2,}', line)
            
            record = {
                'line_number': line_num,
                'raw_line': line,
                'parts': parts,
                'account_numbers': [],
                'routing_numbers': []
            }
            
            # Extract account numbers (8-12 digits)
            account_pattern = r'\b([0-9]{8,12})\b'
            account_matches = re.findall(account_pattern, line)
            
            # Extract routing numbers (exactly 9 digits)
            routing_pattern = r'\b([0-9]{9})\b'
            routing_matches = re.findall(routing_pattern, line)
            
            # Filter: routing numbers are 9 digits, accounts are typically longer or context-specific
            for num in account_matches:
                if len(num) == 9:
                    # Could be routing or account, check context
                    if 'routing' in line.lower() or 'aba' in line.lower() or 'bank routing' in line.lower():
                        record['routing_numbers'].append(num)
                        self.routing_numbers.add(num)
                    else:
                        record['account_numbers'].append(num)
                        self.account_numbers.add(num)
                else:
                    record['account_numbers'].append(num)
                    self.account_numbers.add(num)
            
            for num in routing_matches:
                if num not in [a for a in account_matches if len(a) == 9]:
                    record['routing_numbers'].append(num)
                    self.routing_numbers.add(num)
            
            # Also look for explicit labels
            for i, part in enumerate(parts):
                part_lower = part.lower()
                if 'account' in part_lower or 'deposit' in part_lower:
                    # Next part might be a number
                    if i + 1 < len(parts):
                        next_part = parts[i + 1].strip()
                        if re.match(r'^[0-9]{8,12}$', next_part):
                            if next_part not in record['account_numbers']:
                                record['account_numbers'].append(next_part)
                                self.account_numbers.add(next_part)
                
                if 'routing' in part_lower or 'aba' in part_lower:
                    if i + 1 < len(parts):
                        next_part = parts[i + 1].strip()
                        if re.match(r'^[0-9]{9}$', next_part):
                            if next_part not in record['routing_numbers']:
                                record['routing_numbers'].append(next_part)
                                self.routing_numbers.add(next_part)
            
            if record['account_numbers'] or record['routing_numbers']:
                records.append(record)
                
                # Create pairs if both are present
                if record['account_numbers'] and record['routing_numbers']:
                    for acc in record['account_numbers']:
                        for rout in record['routing_numbers']:
                            self.pairs.append({
                                'account': acc,
                                'routing': rout,
                                'line_number': line_num,
                                'line': line
                            })
        
        self.records = records
        return records
    
    def analyze(self, file_path: str) -> Dict:
        """Perform comprehensive analysis."""
        print(f"Analyzing file: {file_path}")
        print("=" * 60)
        
        if not Path(file_path).exists():
            return {'error': f'File not found: {file_path}'}
        
        records = self.parse_text_file(file_path)
        
        # Statistics
        stats = {
            'total_lines_processed': len(records),
            'unique_account_numbers': len(self.account_numbers),
            'unique_routing_numbers': len(self.routing_numbers),
            'total_pairs': len(self.pairs),
            'accounts_with_routing': len(set(p['account'] for p in self.pairs)),
            'routings_with_account': len(set(p['routing'] for p in self.pairs))
        }
        
        # Account number analysis
        account_lengths = defaultdict(int)
        for acc in self.account_numbers:
            account_lengths[len(acc)] += 1
        
        # Routing number analysis
        routing_prefixes = defaultdict(int)
        for rout in self.routing_numbers:
            prefix = rout[:2] if len(rout) >= 2 else 'N/A'
            routing_prefixes[prefix] += 1
        
        results = {
            'file_path': file_path,
            'statistics': stats,
            'account_analysis': {
                'length_distribution': dict(account_lengths),
                'total_unique': len(self.account_numbers),
                'sample_accounts': list(self.account_numbers)[:10]
            },
            'routing_analysis': {
                'prefix_distribution': dict(routing_prefixes),
                'total_unique': len(self.routing_numbers),
                'sample_routings': list(self.routing_numbers)[:10]
            },
            'pairs': self.pairs[:20],  # First 20 pairs
            'records': records[:10]  # First 10 records
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print analysis summary."""
        if 'error' in results:
            print(f"\nError: {results['error']}")
            return
        
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        
        stats = results.get('statistics', {})
        print(f"\nOverall Statistics:")
        print(f"  - Total records processed: {stats.get('total_lines_processed', 0)}")
        print(f"  - Unique account numbers: {stats.get('unique_account_numbers', 0)}")
        print(f"  - Unique routing numbers: {stats.get('unique_routing_numbers', 0)}")
        print(f"  - Account-Routing pairs: {stats.get('total_pairs', 0)}")
        
        account_analysis = results.get('account_analysis', {})
        print(f"\nAccount Number Analysis:")
        print(f"  - Total unique accounts: {account_analysis.get('total_unique', 0)}")
        length_dist = account_analysis.get('length_distribution', {})
        if length_dist:
            print(f"  - Length distribution:")
            for length, count in sorted(length_dist.items()):
                print(f"      {length} digits: {count} accounts")
        
        routing_analysis = results.get('routing_analysis', {})
        print(f"\nRouting Number Analysis:")
        print(f"  - Total unique routings: {routing_analysis.get('total_unique', 0)}")
        prefix_dist = routing_analysis.get('prefix_distribution', {})
        if prefix_dist:
            print(f"  - Prefix distribution (first 2 digits):")
            for prefix, count in sorted(prefix_dist.items()):
                print(f"      {prefix}xx: {count} routings")
        
        pairs = results.get('pairs', [])
        if pairs:
            print(f"\nSample Account-Routing Pairs (showing first {min(10, len(pairs))}):")
            for i, pair in enumerate(pairs[:10], 1):
                print(f"  {i}. Account: {pair['account']}, Routing: {pair['routing']}")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_extracted_data.py <text_file>")
        print("\nExample:")
        print("  python analyze_extracted_data.py myfile2.txt")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyzer = FinancialDataAnalyzer()
    
    results = analyzer.analyze(file_path)
    analyzer.print_summary(results)
    
    # Save results to JSON
    output_file = Path(file_path).stem + '_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == '__main__':
    main()
