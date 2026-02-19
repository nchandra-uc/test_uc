# JPG Image Financial Data Processing

This script processes captured JPG images containing unstructured financial data and extracts structured information including names, credit cards, bank accounts, routing numbers, and account types.

## Features

- Extracts financial data from unstructured text
- Identifies and classifies:
  - Credit card numbers (13-19 digits, typically 15-16)
  - Bank account numbers (8-17 digits)
  - Routing numbers (9 digits)
  - Account numbers (with or without hyphens)
  - Account types (Checking, Savings)
  - Client names (First Last format)
- Supports multiple output formats (JSON, CSV)
- Handles various input formats including:
  - "Client Bank Account # Credit Card # Name CC# Name"
  - "Number Name Number Number Name"
  - "Account: number number"

## Usage

### Basic Usage

```bash
python3 process_captured_jpg.py <input_text_file> [output_file] [format]
```

### Parameters

- `input_text_file`: Path to text file containing the extracted text from the image
- `output_file`: (Optional) Path to save the output. If not provided, results are printed to stdout
- `format`: (Optional) Output format - `json` (default) or `csv`

### Examples

```bash
# Process a text file and output JSON to stdout
python3 process_captured_jpg.py capture_sample.txt

# Process and save to JSON file
python3 process_captured_jpg.py capture_sample.txt output.json json

# Process and save to CSV file
python3 process_captured_jpg.py capture_sample.txt output.csv csv
```

## Input Format

The script expects text extracted from images. Example input:

```
Client Bank Account # Credit Card # Agnes McCartney 6011125223709063 Sandra Gooch
5116845485280950 Alex Hunt 4126246328149117 30013622322912 Ben Lawton Checking
Account: 9046127-432 341303856308768
```

## Output Format

### JSON Output

```json
[
  {
    "name": "Agnes McCartney",
    "bank_account": null,
    "credit_card": "6011125223709063",
    "account_number": null,
    "routing_number": null,
    "account_type": null
  },
  {
    "name": "Alex Hunt",
    "bank_account": null,
    "credit_card": "5116845485280950",
    "account_number": null,
    "routing_number": null,
    "account_type": "Checking"
  }
]
```

### CSV Output

The CSV format includes columns: `name`, `bank_account`, `credit_card`, `account_number`, `routing_number`, `account_type`

## How It Works

1. **Text Parsing**: The script parses each line of input text
2. **Name Extraction**: Identifies names in "First Last" format, excluding common financial terms
3. **Number Classification**: Classifies numbers based on:
   - Length and format (credit cards: 13-19 digits, typically 15-16)
   - Starting digits (credit cards typically start with 3, 4, 5, or 6)
   - Context (routing numbers are 9 digits)
4. **Association**: Associates numbers with names based on proximity and order in the text
5. **Structured Output**: Generates structured records in JSON or CSV format

## Notes

- The script handles names with capital letters in the middle (e.g., "McCartney")
- Multiple credit cards for the same person are stored in separate records
- Numbers without associated names are included as standalone records
- Account types (Checking/Savings) are extracted from keywords in the text

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)
