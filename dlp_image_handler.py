#!/usr/bin/env python3
"""
DLP Image Handler
Processes images to detect sensitive information using OCR and pattern matching.
"""

import os
import sys
import re
from typing import List, Dict, Tuple
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("Required packages not installed. Install with:")
    print("  pip install pillow pytesseract")
    sys.exit(1)


class DLPImageHandler:
    """Handles DLP scanning of image files."""
    
    # Sensitive data patterns
    PATTERNS = {
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'account_number': r'\b\d{9,12}\b',
        'routing_number': r'\b\d{9}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    }
    
    def __init__(self, image_path: str):
        """Initialize with image path."""
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        self.image = None
        self.text = None
        self.findings = []
    
    def load_image(self) -> None:
        """Load the image file."""
        try:
            self.image = Image.open(self.image_path)
            print(f"✓ Loaded image: {self.image_path.name}")
            print(f"  Size: {self.image.size[0]}x{self.image.size[1]} pixels")
            print(f"  Format: {self.image.format}")
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")
    
    def extract_text(self) -> str:
        """Extract text from image using OCR."""
        if self.image is None:
            self.load_image()
        
        try:
            print("Extracting text using OCR...")
            self.text = pytesseract.image_to_string(self.image)
            print(f"✓ Extracted {len(self.text)} characters")
            return self.text
        except Exception as e:
            print(f"⚠ OCR error: {e}")
            return ""
    
    def scan_for_sensitive_data(self) -> List[Dict]:
        """Scan extracted text for sensitive data patterns."""
        if self.text is None:
            self.extract_text()
        
        self.findings = []
        
        for pattern_name, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, self.text, re.IGNORECASE)
            for match in matches:
                # Mask sensitive data for display
                masked_value = self._mask_sensitive_data(match.group(), pattern_name)
                
                self.findings.append({
                    'type': pattern_name,
                    'value': match.group(),
                    'masked_value': masked_value,
                    'position': match.span(),
                    'line': self._get_line_number(match.start())
                })
        
        return self.findings
    
    def _mask_sensitive_data(self, value: str, pattern_type: str) -> str:
        """Mask sensitive data for safe display."""
        if pattern_type == 'credit_card':
            if len(value.replace('-', '').replace(' ', '')) == 16:
                return f"****-****-****-{value[-4:]}"
        elif pattern_type == 'ssn':
            return f"***-**-{value[-4:]}"
        elif pattern_type == 'email':
            parts = value.split('@')
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
        elif pattern_type == 'phone':
            return f"***-***-{value[-4:]}"
        return "***MASKED***"
    
    def _get_line_number(self, position: int) -> int:
        """Get line number for a character position."""
        return self.text[:position].count('\n') + 1
    
    def generate_report(self) -> str:
        """Generate a DLP scan report."""
        if not self.findings:
            self.scan_for_sensitive_data()
        
        report = []
        report.append("=" * 60)
        report.append("DLP IMAGE SCAN REPORT")
        report.append("=" * 60)
        report.append(f"Image: {self.image_path.name}")
        report.append(f"Total findings: {len(self.findings)}")
        report.append("")
        
        if self.findings:
            # Group by type
            by_type = {}
            for finding in self.findings:
                ftype = finding['type']
                if ftype not in by_type:
                    by_type[ftype] = []
                by_type[ftype].append(finding)
            
            report.append("SENSITIVE DATA DETECTED:")
            report.append("-" * 60)
            for ftype, findings_list in by_type.items():
                report.append(f"\n{ftype.upper().replace('_', ' ')}: {len(findings_list)} occurrence(s)")
                for finding in findings_list:
                    report.append(f"  - {finding['masked_value']} (line {finding['line']})")
        else:
            report.append("✓ No sensitive data patterns detected")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, output_path: str = None) -> str:
        """Save scan report to file."""
        if output_path is None:
            output_path = str(self.image_path.with_suffix('.dlp_report.txt'))
        
        report = self.generate_report()
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"✓ Report saved to: {output_path}")
        return output_path


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python dlp_image_handler.py <image_path>")
        print("\nExample:")
        print("  python dlp_image_handler.py dlpimage.JPG")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        handler = DLPImageHandler(image_path)
        handler.load_image()
        handler.extract_text()
        handler.scan_for_sensitive_data()
        
        # Print report to console
        print("\n" + handler.generate_report())
        
        # Save report to file
        handler.save_report()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
