#!/usr/bin/env python3
"""
Image-based Financial Data Extractor
Processes images containing financial account information and extracts structured data.
"""

import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class FinancialRecord:
    """Structured representation of financial account information."""
    name: Optional[str] = None
    account_type: Optional[str] = None
    account_number: Optional[str] = None
    credit_card_number: Optional[str] = None
    routing_number: Optional[str] = None
    checking_account: Optional[str] = None
    raw_text: Optional[str] = None


class FinancialDataExtractor:
    """Extracts and structures financial data from text/images."""
    
    # Patterns for different types of financial identifiers
    CREDIT_CARD_PATTERN = r'\b\d{13,19}\b'  # 13-19 digits (credit card)
    ACCOUNT_PATTERN = r'\b\d{8,12}\b'  # 8-12 digits (account numbers)
    ROUTING_PATTERN = r'\b\d{9}\b'  # 9 digits (routing numbers)
    HYPHENATED_ACCOUNT = r'\b\d+-\d+\b'  # Hyphenated account numbers
    
    # Common account type keywords
    ACCOUNT_KEYWORDS = [
        'account', 'deposit account', 'bank account', 
        'checking', 'savings', 'credit card'
    ]
    
    def __init__(self):
        self.records: List[FinancialRecord] = []
    
    def extract_from_text(self, text: str) -> List[FinancialRecord]:
        """Extract financial data from unstructured text."""
        lines = text.strip().split('\n')
        records = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Try to extract multiple records from a single line
            line_records = self._parse_line_multi(line)
            if line_records:
                records.extend(line_records)
            else:
                # Fallback to single record parsing
                record = self._parse_line(line)
                if record:
                    records.append(record)
        
        self.records = records
        return records
    
    def _parse_line_multi(self, line: str) -> List[FinancialRecord]:
        """Parse a line that may contain multiple financial records."""
        records = []
        
        # Extract all names first
        excluded_terms = {'Client', 'Bank', 'Account', 'Credit', 'Card', 'Deposit', 
                         'Checking', 'Savings', 'Routing', 'ABA', 'USA'}
        # Match names: 2-3 capitalized words, handling names like McCartney, O'Brien, etc.
        # Pattern: Capital letter, then lowercase (possibly with internal capital like Mc, O', etc.)
        name_pattern = r'\b([A-Z][a-z]+(?:\'[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+(?:\'[A-Z][a-z]+)?){1,2})\b'
        all_names = re.findall(name_pattern, line)
        # Filter out names that contain excluded terms as whole words
        names = []
        for n in all_names:
            # Check if any excluded term appears as a whole word in the name
            name_words = set(n.split())
            if not name_words.intersection(excluded_terms):
                names.append(n)
        
        # Also try a simpler pattern that handles Mc/Mac prefixes better
        if not names or len(names) < 2:
            simple_pattern = r'\b([A-Z][a-z]+\s+[A-Z][A-Za-z]+)\b'
            simple_matches = re.findall(simple_pattern, line)
            for match in simple_matches:
                match_words = set(match.split())
                if not match_words.intersection(excluded_terms) and match not in names:
                    names.append(match)
        
        # Extract all numbers
        all_numbers = re.findall(r'\b\d+\b', line)
        hyphenated_numbers = re.findall(self.HYPHENATED_ACCOUNT, line)
        
        # Group numbers by type
        credit_cards = [n for n in all_numbers if len(n) == 16]
        account_numbers = [n for n in all_numbers if 8 <= len(n) <= 15 and len(n) != 16]
        routing_numbers = [n for n in all_numbers if len(n) == 9]
        
        # If we have multiple names, try to create separate records
        if len(names) > 1:
            # Try to associate names with nearby numbers
            used_ccs = set()
            used_accounts = set()
            
            # First, find positions of all names and numbers to associate them better
            name_positions = [(line.find(name), name) for name in names if line.find(name) >= 0]
            name_positions.sort()  # Sort by position in line
            
            # Find positions of all numbers
            cc_positions = [(line.find(cc), cc) for cc in credit_cards if line.find(cc) >= 0]
            account_positions = [(line.find(acc), acc) for acc in account_numbers if line.find(acc) >= 0]
            
            # First pass: Process names with checking accounts to assign account numbers
            checking_account_records = []
            regular_records = []
            
            for name_pos, name in name_positions:
                name_lower = name.lower()
                line_lower = line.lower()
                name_idx = line_lower.find(name_lower)
                has_checking = False
                
                if name_idx >= 0:
                    check_start = max(0, name_idx - 20)
                    check_end = min(len(line), name_idx + len(name) + 20)
                    check_context = line_lower[check_start:check_end]
                    has_checking = 'checking' in check_context
                
                if has_checking:
                    checking_account_records.append((name_pos, name))
                else:
                    regular_records.append((name_pos, name))
            
            # Process checking accounts first
            for name_pos, name in checking_account_records:
                record = FinancialRecord(name=name, raw_text=line)
                
                # Find the closest credit card to this name
                # Prefer numbers immediately before or after the name
                closest_cc = None
                min_distance = float('inf')
                for cc_pos, cc in cc_positions:
                    if cc not in used_ccs:
                        # Credit cards after the name
                        if cc_pos > name_pos:
                            distance = cc_pos - (name_pos + len(name))
                            if distance < min_distance and distance < 50:
                                min_distance = distance
                                closest_cc = cc
                        # Credit cards before the name - prefer those immediately before
                        elif name_pos - (cc_pos + len(cc)) < 30:
                            # Numbers immediately before name (within 5 chars) get priority
                            gap = name_pos - (cc_pos + len(cc))
                            if gap <= 5:
                                distance = gap  # No penalty for immediate proximity
                            else:
                                distance = gap + 3  # Small penalty for further away
                            if distance < min_distance:
                                min_distance = distance
                                closest_cc = cc
                
                if closest_cc:
                    record.credit_card_number = closest_cc
                    used_ccs.add(closest_cc)
                
                # Find the closest account number to this name
                closest_account = None
                min_distance = float('inf')
                for acc_pos, acc in account_positions:
                    if acc not in used_accounts:
                        if acc_pos > name_pos:
                            distance = acc_pos - (name_pos + len(name))
                            if distance < min_distance and distance < 50:
                                min_distance = distance
                                closest_account = acc
                        elif name_pos - (acc_pos + len(acc)) < 30:
                            # Numbers immediately before name get priority
                            gap = name_pos - (acc_pos + len(acc))
                            if gap <= 5:
                                distance = gap  # No penalty for immediate proximity
                            else:
                                distance = gap + 3  # Small penalty
                            if distance < min_distance:
                                min_distance = distance
                                closest_account = acc
                
                if closest_account:
                    record.account_number = closest_account
                    # If checking account is mentioned, use that type
                    if record.checking_account == 'Yes':
                        record.account_type = 'Checking Account'
                    else:
                        record.account_type = 'Bank Account'
                    used_accounts.add(closest_account)
                
                # Check for checking account mention near this name
                name_lower = name.lower()
                line_lower = line.lower()
                name_idx = line_lower.find(name_lower)
                if name_idx >= 0:
                    # Check if "checking" appears near this name
                    check_start = max(0, name_idx - 20)
                    check_end = min(len(line), name_idx + len(name) + 20)
                    check_context = line_lower[check_start:check_end]
                    if 'checking' in check_context:
                        record.account_type = 'Checking Account'
                        record.checking_account = 'Yes'
                        
                        # If this person has a checking account, prioritize account numbers near them
                        # Find account numbers very close to this name (within 30 chars before or after)
                        for acc_pos, acc in account_positions:
                            if acc not in used_accounts:
                                # Check if account is before or after the name
                                if acc_pos < name_pos:
                                    gap = name_pos - (acc_pos + len(acc))
                                else:
                                    gap = acc_pos - (name_pos + len(name))
                                
                                if gap < 30:
                                    record.account_number = acc
                                    used_accounts.add(acc)
                                    break
                
                # Always add record if we have a name, even without numbers
                records.append(record)
            
            # Second pass: Process regular records (non-checking accounts)
            for name_pos, name in regular_records:
                record = FinancialRecord(name=name, raw_text=line)
                
                # Find the closest credit card to this name
                closest_cc = None
                min_distance = float('inf')
                for cc_pos, cc in cc_positions:
                    if cc not in used_ccs:
                        if cc_pos > name_pos:
                            distance = cc_pos - (name_pos + len(name))
                            if distance < min_distance and distance < 50:
                                min_distance = distance
                                closest_cc = cc
                        elif name_pos - (cc_pos + len(cc)) < 30:
                            gap = name_pos - (cc_pos + len(cc))
                            if gap <= 5:
                                distance = gap
                            else:
                                distance = gap + 3
                            if distance < min_distance:
                                min_distance = distance
                                closest_cc = cc
                
                if closest_cc:
                    record.credit_card_number = closest_cc
                    used_ccs.add(closest_cc)
                
                # Find the closest account number to this name (only if not already assigned)
                closest_account = None
                min_distance = float('inf')
                for acc_pos, acc in account_positions:
                    if acc not in used_accounts:
                        if acc_pos > name_pos:
                            distance = acc_pos - (name_pos + len(name))
                            if distance < min_distance and distance < 50:
                                min_distance = distance
                                closest_account = acc
                        elif name_pos - (acc_pos + len(acc)) < 30:
                            gap = name_pos - (acc_pos + len(acc))
                            if gap <= 5:
                                distance = gap
                            else:
                                distance = gap + 3
                            if distance < min_distance:
                                min_distance = distance
                                closest_account = acc
                
                if closest_account:
                    record.account_number = closest_account
                    record.account_type = 'Bank Account'
                    used_accounts.add(closest_account)
                
                records.append(record)
        
        # If we have credit cards but no names, create records for them
        if credit_cards and not names:
            for cc in credit_cards:
                record = FinancialRecord(
                    credit_card_number=cc,
                    account_type='Credit Card',
                    raw_text=line
                )
                records.append(record)
        
        # If we have account numbers but no names, create records
        if account_numbers and not names and not records:
            for acc in account_numbers:
                record = FinancialRecord(
                    account_number=acc,
                    account_type='Bank Account',
                    raw_text=line
                )
                records.append(record)
        
        # Handle hyphenated account numbers (add them even if other records exist)
        if hyphenated_numbers:
            for acc in hyphenated_numbers:
                # Check if this hyphenated account is already in a record
                already_included = any(r.account_number == acc for r in records)
                if not already_included:
                    # Check if we should add it to an existing record or create a new one
                    if records and not any(r.account_number for r in records):
                        # Add to first record without an account number
                        for r in records:
                            if not r.account_number:
                                r.account_number = acc
                                r.account_type = 'Bank Account'
                                break
                    else:
                        # Create a new record for the hyphenated account
                        record = FinancialRecord(
                            account_number=acc,
                            account_type='Bank Account',
                            raw_text=line
                        )
                        records.append(record)
        
        return records if records else []
    
    def _parse_line(self, line: str) -> Optional[FinancialRecord]:
        """Parse a single line of text to extract financial information."""
        record = FinancialRecord(raw_text=line)
        
        # Extract names (capitalized words, typically 2-3 words, but not common keywords)
        # Exclude common financial terms
        excluded_terms = {'Client', 'Bank', 'Account', 'Credit', 'Card', 'Deposit', 
                         'Checking', 'Savings', 'Routing', 'ABA', 'USA'}
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
        all_names = re.findall(name_pattern, line)
        # Filter out excluded terms
        names = [n for n in all_names if not any(term in n for term in excluded_terms)]
        if names:
            record.name = names[0] if names else None
        
        # Extract all numbers first
        all_numbers = re.findall(r'\b\d+\b', line)
        hyphenated_numbers = re.findall(self.HYPHENATED_ACCOUNT, line)
        
        # Extract credit card numbers (16 digits typically)
        credit_cards = [n for n in all_numbers if len(n) == 16]
        if credit_cards:
            record.credit_card_number = credit_cards[0]
        
        # Extract account numbers
        # Look for patterns like "Account:", "Account #", etc.
        account_label_pattern = r'(?:account|deposit\s+account|bank\s+account)[\s#:]*(\d+(?:-\d+)?)'
        account_matches = re.findall(account_label_pattern, line, re.IGNORECASE)
        if account_matches:
            record.account_number = account_matches[0]
            record.account_type = 'Bank Account'
        
        # Extract hyphenated account numbers (like 9046127-432)
        if hyphenated_numbers and not record.account_number:
            record.account_number = hyphenated_numbers[0]
            record.account_type = 'Bank Account'
        
        # Extract other account-like numbers (8-15 digits, not credit cards)
        if not record.account_number:
            account_like = [n for n in all_numbers if 8 <= len(n) <= 15 and len(n) != 16]
            if account_like:
                # Prefer longer numbers for account numbers
                record.account_number = max(account_like, key=len)
        
        # Extract routing numbers (9 digits)
        routing_label_pattern = r'(?:routing|aba|bank\s+routing)[\s#:]*(\d{9})'
        routing_matches = re.findall(routing_label_pattern, line, re.IGNORECASE)
        if routing_matches:
            record.routing_number = routing_matches[0]
        elif not record.routing_number:
            # Look for 9-digit numbers that might be routing numbers
            routing_candidates = [n for n in all_numbers if len(n) == 9]
            if routing_candidates:
                record.routing_number = routing_candidates[0]
        
        # Check for checking account mentions
        if 'checking' in line.lower():
            record.account_type = 'Checking Account'
            record.checking_account = 'Yes'
        
        # If we found any meaningful data, return the record
        if (record.name or record.account_number or record.credit_card_number or 
            record.routing_number or record.checking_account):
            return record
        
        return None
    
    def to_json(self, indent: int = 2) -> str:
        """Convert records to JSON format."""
        return json.dumps([asdict(r) for r in self.records], indent=indent)
    
    def to_csv(self) -> str:
        """Convert records to CSV format."""
        if not self.records:
            return ""
        
        headers = ['name', 'account_type', 'account_number', 'credit_card_number', 
                  'routing_number', 'checking_account', 'raw_text']
        
        lines = [','.join(headers)]
        for record in self.records:
            values = [
                record.name or '',
                record.account_type or '',
                record.account_number or '',
                record.credit_card_number or '',
                record.routing_number or '',
                record.checking_account or '',
                f'"{record.raw_text or ""}"'  # Quote raw text to handle commas
            ]
            lines.append(','.join(values))
        
        return '\n'.join(lines)


def process_capture_image():
    """Process the Capture.JPG image data."""
    # Based on the image description provided
    image_text = """Client Bank Account # Credit Card # Agnes McCartney 6011125223709063 Sandra Gooch
5116845485280950 Alex Hunt 4126246328149117 30013622322912 Ben Lawton Checking
Account: 9046127-432 341303856308768"""
    
    extractor = FinancialDataExtractor()
    records = extractor.extract_from_text(image_text)
    
    print("Extracted Financial Records:")
    print("=" * 80)
    print(extractor.to_json())
    print("\n" + "=" * 80)
    print("\nCSV Format:")
    print(extractor.to_csv())
    
    # Save to files
    with open('/workspace/capture_extracted.json', 'w') as f:
        f.write(extractor.to_json())
    
    with open('/workspace/capture_extracted.csv', 'w') as f:
        f.write(extractor.to_csv())
    
    print(f"\n✓ Extracted {len(records)} records")
    print("✓ Saved to capture_extracted.json and capture_extracted.csv")
    
    return records


def process_image_file(image_path: str):
    """Process an image file (requires OCR library like pytesseract)."""
    try:
        from PIL import Image
        import pytesseract
        
        # Open and process image
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        
        extractor = FinancialDataExtractor()
        records = extractor.extract_from_text(text)
        
        print(f"Processed image: {image_path}")
        print(f"Extracted {len(records)} records")
        
        return records
    except ImportError:
        print("OCR libraries not installed. Install with: pip install pytesseract pillow")
        return []
    except Exception as e:
        print(f"Error processing image: {e}")
        return []


if __name__ == '__main__':
    process_capture_image()
