#!/usr/bin/env python3
"""
Process myfile.csv to normalize SSN formats and clean the data.
"""

import csv
import re

def normalize_ssn(ssn):
    """
    Normalize SSN to XXX-XX-XXXX format.
    Handles formats: XXX-XX-XXXX, XXX XX XXXX, XXXXXXXXX
    """
    if not ssn or ssn.strip() == '':
        return ''
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', ssn.strip())
    
    # Check if we have 9 digits
    if len(digits_only) == 9:
        return f"{digits_only[:3]}-{digits_only[3:5]}-{digits_only[5:]}"
    
    # If already in XXX-XX-XXXX format, return as is
    if re.match(r'^\d{3}-\d{2}-\d{4}$', ssn.strip()):
        return ssn.strip()
    
    # Return original if can't normalize
    return ssn.strip()

def process_csv(input_file, output_file):
    """
    Process the CSV file:
    1. Normalize all SSN formats to XXX-XX-XXXX
    2. Remove the section header row ("USA Social Security Number")
    3. Keep all other data intact
    """
    rows_processed = 0
    rows_skipped = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Process header row
        header = next(reader)
        writer.writerow(header)
        rows_processed += 1
        
        # Process data rows
        for row in reader:
            # Skip empty rows
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            
            # Skip the section header row
            if row[0].strip().lower() == 'usa social security number':
                rows_skipped += 1
                continue
            
            # Normalize SSN in first column
            if len(row) > 0:
                row[0] = normalize_ssn(row[0])
            
            writer.writerow(row)
            rows_processed += 1
    
    print(f"Processing complete!")
    print(f"Rows processed: {rows_processed}")
    print(f"Rows skipped: {rows_skipped}")
    print(f"Output written to: {output_file}")

if __name__ == '__main__':
    process_csv('myfile.csv', 'myfile_processed.csv')
