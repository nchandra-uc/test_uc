#!/usr/bin/env python3
"""
Process myfile.csv to normalize SSN formatting and clean data.
"""

import csv
import re
from pathlib import Path


def normalize_ssn(ssn_str):
    """
    Normalize SSN to format: XXX-XX-XXXX
    Handles formats: XXX-XX-XXXX, XXX XX XXXX, or XXXXXXXXX
    """
    if not ssn_str or ssn_str.strip() == '':
        return ''
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', ssn_str)
    
    # Check if we have 9 digits
    if len(digits_only) == 9:
        # Format as XXX-XX-XXXX
        return f"{digits_only[:3]}-{digits_only[3:5]}-{digits_only[5:]}"
    else:
        # Return original if not 9 digits
        return ssn_str


def process_csv(input_file, output_file):
    """
    Process the CSV file:
    1. Normalize SSN formatting
    2. Remove the "USA Social Security Number" label row
    3. Keep complete records and SSN-only records separately
    """
    complete_records = []
    ssn_only_records = []
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        
        # Get the actual SSN column name (might have BOM)
        ssn_key = None
        for key in reader.fieldnames:
            if 'SSN' in key:
                ssn_key = key
                break
        
        if not ssn_key:
            raise ValueError("Could not find SSN column in CSV")
        
        for row in reader:
            # Normalize SSN
            ssn = normalize_ssn(row[ssn_key])
            
            # Skip the label row
            if ssn.upper() == 'USA-SOCIAL-SECURITY-NUMBER' or \
               row[ssn_key].strip().upper() == 'USA SOCIAL SECURITY NUMBER':
                continue
            
            # Check if this is a complete record (has at least gender or other fields)
            has_other_data = any([
                row.get('gender', '').strip(),
                row.get('birthdate', '').strip(),
                row.get('last name', '').strip(),
                row.get('first name', '').strip()
            ])
            
            # Update the SSN in the row (use clean key)
            row['US SSN'] = ssn
            
            if has_other_data:
                complete_records.append(row)
            elif ssn:  # Only add if SSN is not empty
                ssn_only_records.append(row)
    
    # Write complete records
    if complete_records:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['US SSN', 'gender', 'birthdate', 'maiden name', 
                         'last name', 'first name', 'address', 'city', 
                         'state', 'zip', 'phone']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(complete_records)
        
        print(f"✓ Processed {len(complete_records)} complete records")
    
    # Write SSN-only records to a separate file
    if ssn_only_records:
        ssn_only_file = output_file.replace('.csv', '_ssn_only.csv')
        with open(ssn_only_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['US SSN']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in ssn_only_records:
                writer.writerow({'US SSN': row['US SSN']})
        
        print(f"✓ Processed {len(ssn_only_records)} SSN-only records -> {ssn_only_file}")
    
    return len(complete_records), len(ssn_only_records)


if __name__ == '__main__':
    input_file = 'myfile.csv'
    output_file = 'myfile_processed.csv'
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        exit(1)
    
    print(f"Processing {input_file}...")
    complete_count, ssn_only_count = process_csv(input_file, output_file)
    print(f"\nSummary:")
    print(f"  Complete records: {complete_count}")
    print(f"  SSN-only records: {ssn_only_count}")
    print(f"  Output file: {output_file}")
