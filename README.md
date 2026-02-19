# Image-based Financial Data Extractor

This tool extracts and structures financial account information from images or text containing unstructured financial data.

## Features

- Extracts names, account numbers, credit card numbers, routing numbers, and account types
- Handles multiple names and accounts per line
- Associates financial numbers with the correct person based on proximity
- Supports various account formats including hyphenated account numbers
- Exports data to JSON and CSV formats

## Usage

### Basic Usage

```python
from image_processor import FinancialDataExtractor

extractor = FinancialDataExtractor()

# Process text directly
text = """Client Bank Account # Credit Card # Agnes McCartney 6011125223709063 Sandra Gooch"""
records = extractor.extract_from_text(text)

# Export to JSON
print(extractor.to_json())

# Export to CSV
print(extractor.to_csv())
```

### Process Image File

```python
from image_processor import process_image_file

# Requires pytesseract and PIL
records = process_image_file('Capture.JPG')
```

### Run the Script

```bash
python3 image_processor.py
```

This will process the sample data from Capture.JPG and save results to:
- `capture_extracted.json`
- `capture_extracted.csv`

## Output Format

Each record contains:
- `name`: Person's name (if found)
- `account_type`: Type of account (Bank Account, Checking Account, Credit Card)
- `account_number`: Bank account number
- `credit_card_number`: Credit card number (16 digits)
- `routing_number`: Bank routing number (9 digits)
- `checking_account`: "Yes" if checking account is mentioned
- `raw_text`: Original text line

## Requirements

For basic text processing:
- Python 3.6+

For image processing (OCR):
- Python 3.6+
- pytesseract
- Pillow (PIL)
- Tesseract OCR installed on system

Install OCR dependencies:
```bash
pip install pytesseract pillow
```

## Notes

- The tool uses pattern matching and proximity analysis to associate numbers with names
- Names with "Mc", "Mac", "O'" prefixes are handled correctly
- Checking accounts are prioritized when assigning account numbers
- Multiple records can be extracted from a single line of text
