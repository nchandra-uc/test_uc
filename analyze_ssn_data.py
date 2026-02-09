#!/usr/bin/env python3
"""
Script to analyze and process US Social Security Number (SSN) data from CSV file.
Handles various SSN formats and provides statistics.
"""

import csv
import re
from collections import Counter
from typing import List, Dict, Tuple

def normalize_ssn(ssn: str) -> str:
    """
    Normalize SSN to standard format: XXX-XX-XXXX
    Handles formats like:
    - XXX-XX-XXXX (standard)
    - XXX XX XXXX (spaces)
    - XXXXXXXXX (no separators)
    """
    if not ssn or ssn.strip() == '':
        return ''
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', ssn.strip())
    
    # Validate length (should be 9 digits)
    if len(digits_only) != 9:
        return ssn  # Return original if invalid
    
    # Format as XXX-XX-XXXX
    return f"{digits_only[:3]}-{digits_only[3:5]}-{digits_only[5:]}"

def validate_ssn(ssn: str) -> bool:
    """
    Validate SSN format and basic rules:
    - Must be 9 digits
    - First 3 digits (area) cannot be 000, 666, or 900-999
    - Middle 2 digits (group) cannot be 00
    - Last 4 digits (serial) cannot be 0000
    """
    normalized = normalize_ssn(ssn)
    if not normalized or '-' not in normalized:
        return False
    
    parts = normalized.split('-')
    if len(parts) != 3:
        return False
    
    area = parts[0]
    group = parts[1]
    serial = parts[2]
    
    # Check invalid area numbers
    if area == '000' or area == '666' or (900 <= int(area) <= 999):
        return False
    
    # Check invalid group
    if group == '00':
        return False
    
    # Check invalid serial
    if serial == '0000':
        return False
    
    return True

def analyze_ssn_file(filename: str) -> Dict:
    """
    Analyze the SSN CSV file and return statistics.
    """
    complete_records = []
    ssn_only_records = []
    invalid_ssns = []
    ssn_formats = Counter()
    
    with open(filename, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        
        for row in reader:
            # Handle BOM in header - try both with and without BOM
            ssn = row.get('US SSN', '') or row.get('\ufeffUS SSN', '')
            ssn = ssn.strip()
            
            if not ssn or ssn == 'USA Social Security Number':
                continue
            
            # Detect format
            if '-' in ssn:
                ssn_formats['XXX-XX-XXXX (dashes)'] += 1
            elif ' ' in ssn:
                ssn_formats['XXX XX XXXX (spaces)'] += 1
            elif ssn.isdigit():
                ssn_formats['XXXXXXXXX (digits only)'] += 1
            else:
                ssn_formats['Other format'] += 1
            
            # Normalize SSN
            normalized_ssn = normalize_ssn(ssn)
            
            # Check if record has complete data
            # Try both with and without BOM in field names
            has_complete_data = any([
                row.get('first name', '').strip() or row.get('\ufefffirst name', '').strip(),
                row.get('last name', '').strip() or row.get('\ufefflast name', '').strip(),
                row.get('address', '').strip() or row.get('\ufeffaddress', '').strip()
            ])
            
            if has_complete_data:
                record = row.copy()
                record['normalized_ssn'] = normalized_ssn
                record['is_valid'] = validate_ssn(ssn)
                complete_records.append(record)
            else:
                ssn_only_records.append({
                    'original_ssn': ssn,
                    'normalized_ssn': normalized_ssn,
                    'is_valid': validate_ssn(ssn)
                })
                if not validate_ssn(ssn):
                    invalid_ssns.append(ssn)
    
    return {
        'complete_records': complete_records,
        'ssn_only_records': ssn_only_records,
        'invalid_ssns': invalid_ssns,
        'ssn_formats': dict(ssn_formats),
        'total_complete': len(complete_records),
        'total_ssn_only': len(ssn_only_records),
        'total_invalid': len(invalid_ssns)
    }

def write_normalized_output(input_file: str, output_file: str):
    """
    Read input CSV and write normalized version with standardized SSN format.
    """
    with open(input_file, 'r', encoding='utf-8-sig') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        if fieldnames:
            # Clean fieldnames (remove BOM if present)
            clean_fieldnames = [fname.replace('\ufeff', '') for fname in fieldnames]
            writer = csv.DictWriter(outfile, fieldnames=clean_fieldnames)
            writer.writeheader()
            
            for row in reader:
                # Handle BOM in header - find the actual key
                ssn_key = None
                for key in row.keys():
                    if 'US SSN' in key:
                        ssn_key = key
                        break
                
                if ssn_key:
                    ssn = row[ssn_key].strip()
                    
                    if ssn and ssn != 'USA Social Security Number':
                        # Normalize the SSN
                        normalized = normalize_ssn(ssn)
                        # Update row with clean fieldname
                        clean_row = {}
                        for key, value in row.items():
                            clean_key = key.replace('\ufeff', '')
                            clean_row[clean_key] = value
                        clean_row['US SSN'] = normalized
                        writer.writerow(clean_row)
                    elif ssn == 'USA Social Security Number':
                        # Keep separator row
                        clean_row = {}
                        for key, value in row.items():
                            clean_key = key.replace('\ufeff', '')
                            clean_row[clean_key] = value
                        writer.writerow(clean_row)

def main():
    input_file = 'myfile.csv'
    output_file = 'myfile_normalized.csv'
    
    print("=" * 60)
    print("US Social Security Number Data Analysis")
    print("=" * 60)
    print()
    
    # Analyze the file
    analysis = analyze_ssn_file(input_file)
    
    # Print statistics
    print(f"Total complete records (with personal info): {analysis['total_complete']}")
    print(f"Total SSN-only records: {analysis['total_ssn_only']}")
    print(f"Total invalid SSNs: {analysis['total_invalid']}")
    print()
    
    print("SSN Format Distribution:")
    for format_type, count in analysis['ssn_formats'].items():
        print(f"  {format_type}: {count}")
    print()
    
    if analysis['invalid_ssns']:
        print(f"Invalid SSNs found ({len(analysis['invalid_ssns'])}):")
        for invalid in analysis['invalid_ssns'][:10]:  # Show first 10
            print(f"  {invalid}")
        if len(analysis['invalid_ssns']) > 10:
            print(f"  ... and {len(analysis['invalid_ssns']) - 10} more")
        print()
    
    # Create normalized output file
    print(f"Creating normalized output file: {output_file}")
    write_normalized_output(input_file, output_file)
    print("Done!")
    print()
    
    # Show sample of normalized SSNs
    print("Sample of normalized SSNs (first 10 SSN-only records):")
    for i, record in enumerate(analysis['ssn_only_records'][:10], 1):
        status = "✓ Valid" if record['is_valid'] else "✗ Invalid"
        print(f"  {i}. {record['original_ssn']:15} -> {record['normalized_ssn']:15} {status}")

if __name__ == '__main__':
    main()
