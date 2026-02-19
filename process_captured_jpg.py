#!/usr/bin/env python3
"""
Script to process captured JPG images and extract structured financial data
from unstructured text containing bank accounts, credit cards, and names.
"""

import re
import json
import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class FinancialRecord:
    """Represents a structured financial record extracted from text."""
    name: Optional[str] = None
    bank_account: Optional[str] = None
    credit_card: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    account_type: Optional[str] = None


class FinancialDataExtractor:
    """Extracts structured financial data from unstructured text."""
    
    # Patterns for different types of financial identifiers
    CREDIT_CARD_PATTERN = r'\b\d{13,19}\b'  # 13-19 digits (credit card)
    BANK_ACCOUNT_PATTERN = r'\b\d{8,17}\b'  # 8-17 digits (bank account)
    ROUTING_PATTERN = r'\b\d{9}\b'  # 9 digits (routing number)
    ACCOUNT_WITH_HYPHEN = r'\b\d+-\d+\b'  # Account numbers with hyphens
    # Name pattern: First name (starts with capital, may have capitals in middle like "McCartney")
    # followed by Last name (starts with capital, may have capitals in middle)
    NAME_PATTERN = r'\b[A-Z][A-Za-z]+ [A-Z][A-Za-z]+\b'  # First Last name format
    
    # Words to exclude from name matching
    EXCLUDE_WORDS = {'client', 'bank', 'account', 'credit', 'card', 'checking', 'savings', 'deposit', 'routing'}
    
    def __init__(self):
        self.records: List[FinancialRecord] = []
    
    def _is_credit_card(self, num: str) -> bool:
        """Check if a number is likely a credit card."""
        clean_num = num.replace('-', '')
        # Credit cards are typically 15-16 digits, sometimes 13-19
        # Must start with 3, 4, 5, or 6
        return (len(clean_num) >= 13 and len(clean_num) <= 19 and 
                clean_num[0] in ['3', '4', '5', '6'] and
                (len(clean_num) == 15 or len(clean_num) == 16 or len(clean_num) == 13))
    
    def _is_routing(self, num: str) -> bool:
        """Check if a number is likely a routing number."""
        return len(num.replace('-', '')) == 9
    
    def extract_from_text(self, text: str) -> List[FinancialRecord]:
        """
        Extract financial data from unstructured text.
        
        Args:
            text: Raw text containing financial information
            
        Returns:
            List of FinancialRecord objects
        """
        self.records = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract account type
            account_type = None
            if 'checking' in line.lower():
                account_type = 'Checking'
            elif 'savings' in line.lower():
                account_type = 'Savings'
            
            # Extract all names (First Last format), excluding common financial terms
            potential_names = re.findall(r'\b([A-Z][A-Za-z]+ [A-Z][A-Za-z]+)\b', line)
            names = []
            for name in potential_names:
                # Exclude if it contains financial terms
                name_lower = name.lower()
                if not any(word in name_lower for word in self.EXCLUDE_WORDS):
                    names.append(name)
            
            # Extract all numbers
            all_numbers = re.findall(r'\b(\d{8,19}|\d+-\d+)\b', line)
            
            # Special handling for "Client Bank Account # Credit Card #" format
            if 'client bank account' in line.lower() and 'credit card' in line.lower():
                # Format: "Client Bank Account # Credit Card # Agnes McCartney 6011125223709063 Sandra Gooch"
                # Associate credit cards with the name immediately before them
                tokens = line.split()
                
                for i, token in enumerate(tokens):
                    if self._is_credit_card(token):
                        # Find the name immediately before this credit card
                        associated_name = None
                        # Look backwards for a name (check tokens[i-2] + ' ' + tokens[i-1])
                        if i >= 2:
                            potential_name = tokens[i-2] + ' ' + tokens[i-1]
                            if potential_name in names:
                                associated_name = potential_name
                        
                        record = FinancialRecord(
                            name=associated_name,
                            credit_card=token
                        )
                        self.records.append(record)
                
                # Add records for names without credit cards
                used_names = set()
                for record in self.records:
                    if record.name:
                        used_names.add(record.name)
                for name in names:
                    if name not in used_names:
                        record = FinancialRecord(name=name)
                        self.records.append(record)
            
            # Handle lines with names and numbers
            elif names:
                # Associate numbers with the name immediately before them
                tokens = line.split()
                name_to_numbers = {}
                
                # Find all numbers and their positions
                number_positions = []
                for i, token in enumerate(tokens):
                    if re.match(r'^\d{8,19}$', token) or re.match(r'^\d+-\d+$', token):
                        number_positions.append((i, token))
                
                # Find all name positions
                name_positions = []
                for i in range(len(tokens) - 1):
                    potential_name = tokens[i] + ' ' + tokens[i+1]
                    if potential_name in names:
                        name_positions.append((i, potential_name))
                
                # Associate numbers with names
                # Priority: 1) Immediately following name (if number is right before it with no other numbers), 
                #           2) Preceding name (if exists), 3) Following name (if no preceding)
                for num_pos, num in number_positions:
                    associated_name = None
                    
                    # Find closest following name
                    closest_following_pos = len(tokens)
                    closest_following_name = None
                    for name_pos, name in name_positions:
                        if name_pos > num_pos and name_pos < closest_following_pos:
                            closest_following_name = name
                            closest_following_pos = name_pos
                    
                    # Find closest preceding name
                    closest_preceding_pos = -1
                    closest_preceding_name = None
                    for name_pos, name in name_positions:
                        if name_pos < num_pos and name_pos > closest_preceding_pos:
                            closest_preceding_name = name
                            closest_preceding_pos = name_pos
                    
                    # Check if there are other numbers between this number and the following name
                    has_number_between = False
                    if closest_following_name:
                        for other_num_pos, _ in number_positions:
                            if num_pos < other_num_pos < closest_following_pos:
                                has_number_between = True
                                break
                    
                    # If number is immediately before a name (no other numbers in between), use that name
                    # This handles cases like "30013622322912 Ben Lawton"
                    if closest_following_name and not has_number_between:
                        associated_name = closest_following_name
                    elif closest_preceding_name:
                        # Use preceding name (for numbers between two names with other numbers)
                        associated_name = closest_preceding_name
                    elif closest_following_name:
                        # No preceding name, use following name
                        associated_name = closest_following_name
                    
                    if associated_name:
                        if associated_name not in name_to_numbers:
                            name_to_numbers[associated_name] = []
                        name_to_numbers[associated_name].append(num)
                    else:
                        # Number without a name - create standalone record
                        record = FinancialRecord(account_type=account_type)
                        if self._is_credit_card(num):
                            record.credit_card = num
                        elif self._is_routing(num):
                            record.routing_number = num
                        elif '-' in num:
                            record.account_number = num
                        else:
                            record.bank_account = num
                        self.records.append(record)
                
                # Create records for names with their associated numbers
                for name, numbers in name_to_numbers.items():
                    record = FinancialRecord(name=name, account_type=account_type)
                    for num in numbers:
                        if self._is_credit_card(num):
                            # Can have multiple credit cards - create separate records if needed
                            if not record.credit_card:
                                record.credit_card = num
                            else:
                                # Create new record for additional credit card
                                new_record = FinancialRecord(
                                    name=name,
                                    credit_card=num,
                                    account_type=account_type
                                )
                                self.records.append(new_record)
                        elif self._is_routing(num) and not record.routing_number:
                            record.routing_number = num
                        elif '-' in num and not record.account_number:
                            record.account_number = num
                        elif not record.bank_account:
                            record.bank_account = num
                        elif not record.account_number:
                            record.account_number = num
                    self.records.append(record)
                
                # Handle names without numbers
                for name in names:
                    if name not in name_to_numbers:
                        # Check if we already created a record for this name
                        found = False
                        for record in self.records:
                            if record.name == name:
                                found = True
                                break
                        if not found:
                            record = FinancialRecord(name=name, account_type=account_type)
                            self.records.append(record)
            
            # Handle "Account:" format
            elif 'account:' in line.lower():
                match = re.search(r'account:\s*([\d-]+)', line, re.IGNORECASE)
                if match:
                    record = FinancialRecord(account_number=match.group(1), account_type=account_type)
                    # Check for additional numbers after the account
                    remaining = line[match.end():].strip()
                    remaining_numbers = re.findall(r'\b\d{8,17}\b', remaining)
                    if remaining_numbers:
                        record.bank_account = remaining_numbers[0]
                    self.records.append(record)
            
            # Handle lines with just numbers
            elif all_numbers:
                for num in all_numbers:
                    record = FinancialRecord(account_type=account_type)
                    if self._is_credit_card(num):
                        record.credit_card = num
                    elif self._is_routing(num):
                        record.routing_number = num
                    elif '-' in num:
                        record.account_number = num
                    else:
                        record.bank_account = num
                    self.records.append(record)
        
        return self.records
    
    def to_json(self, output_file: Optional[str] = None) -> str:
        """Convert records to JSON format."""
        data = [asdict(record) for record in self.records]
        json_str = json.dumps(data, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    def to_csv(self, output_file: str):
        """Convert records to CSV format."""
        if not self.records:
            return
        
        fieldnames = ['name', 'bank_account', 'credit_card', 'account_number', 
                     'routing_number', 'account_type']
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records:
                writer.writerow(asdict(record))


def process_image_text(text: str, output_format: str = 'json') -> Tuple[List[FinancialRecord], str]:
    """
    Process text extracted from an image and return structured data.
    
    Args:
        text: Text content from image
        output_format: 'json' or 'csv'
        
    Returns:
        Tuple of (records list, output string)
    """
    extractor = FinancialDataExtractor()
    records = extractor.extract_from_text(text)
    
    if output_format == 'json':
        output = extractor.to_json()
    else:
        # For CSV, write to string
        import io
        output_buffer = io.StringIO()
        fieldnames = ['name', 'bank_account', 'credit_card', 'account_number', 
                     'routing_number', 'account_type']
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
        output = output_buffer.getvalue()
    
    return records, output


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python process_captured_jpg.py <input_text_file> [output_file] [format]")
        print("Format: json (default) or csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    output_format = sys.argv[3] if len(sys.argv) > 3 else 'json'
    
    # Read input text file
    with open(input_file, 'r') as f:
        text = f.read()
    
    # Process the text
    records, output = process_image_text(text, output_format)
    
    # Print results
    print(f"Extracted {len(records)} financial records:")
    print("\n" + "="*60)
    print(output)
    print("="*60)
    
    # Save to file if specified
    if output_file:
        if output_format == 'json':
            extractor = FinancialDataExtractor()
            extractor.records = records
            extractor.to_json(output_file)
        else:
            extractor = FinancialDataExtractor()
            extractor.records = records
            extractor.to_csv(output_file)
        print(f"\nResults saved to {output_file}")


if __name__ == '__main__':
    main()
