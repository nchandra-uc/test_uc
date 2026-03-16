#!/usr/bin/env python3
"""
CSV Processing Script for myfile.csv
- Normalizes SSN formats
- Handles incomplete rows
- Outputs cleaned data
"""

import csv
import re
from typing import List, Dict, Optional

def normalize_ssn(ssn: str) -> Optional[str]:
    """Normalize SSN to format XXX-XX-XXXX"""
    if not ssn or not ssn.strip():
        return None
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', ssn)
    
    # Check if we have 9 digits
    if len(digits_only) == 9:
        return f"{digits_only[:3]}-{digits_only[3:5]}-{digits_only[5:]}"
    
    return None

def is_valid_row(row: Dict[str, str]) -> bool:
    """Check if row has meaningful data beyond just SSN"""
    # Check if any field other than SSN has data
    for key, value in row.items():
        if 'SSN' not in key.upper() and value and value.strip():
            return True
    return False

def process_csv(input_file: str, output_file: str):
    """Process the CSV file and create a cleaned version"""
    processed_rows = []
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        header = reader.fieldnames
        
        if not header:
            print("Error: No header found in CSV file")
            return
        
        # Find the SSN column key (handle BOM)
        ssn_key = None
        for key in header:
            if 'SSN' in key.upper():
                ssn_key = key
                break
        
        if not ssn_key:
            print("Error: Could not find SSN column")
            return
        
        for row in reader:
            ssn = row.get(ssn_key, '').strip()
            
            # Skip header-like rows
            if ssn.lower() in ['usa social security number', 'us ssn']:
                continue
            
            # Skip empty rows
            if not ssn:
                continue
            
            normalized_ssn = normalize_ssn(ssn)
            
            if normalized_ssn:
                # Update the SSN in the row
                row[ssn_key] = normalized_ssn
                processed_rows.append(row)
            elif ssn:
                # Keep rows with SSN even if normalization failed (for review)
                processed_rows.append(row)
    
    # Normalize header (remove BOM from first column)
    normalized_header = [h.strip('\ufeff') if h.startswith('\ufeff') else h for h in header]
    
    # Write processed data
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=normalized_header)
        writer.writeheader()
        
        # Normalize row keys to match normalized header
        for row in processed_rows:
            normalized_row = {}
            for i, orig_key in enumerate(header):
                normalized_key = normalized_header[i]
                normalized_row[normalized_key] = row.get(orig_key, '')
            writer.writerow(normalized_row)
    
    # Print statistics
    complete_rows = sum(1 for row in processed_rows if is_valid_row(row))
    ssn_only_rows = len(processed_rows) - complete_rows
    
    print(f"Processing complete!")
    print(f"Total rows processed: {len(processed_rows)}")
    print(f"Complete records: {complete_rows}")
    print(f"SSN-only records: {ssn_only_rows}")
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    process_csv('myfile.csv', 'myfile_cleaned.csv')
