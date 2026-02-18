# CSV File Processing Tool

A Python script to extract and analyze sensitive data from CSV files, including:
- Social Security Numbers (SSN)
- Bank Account Numbers
- Routing Numbers (ABA)
- Credit Card Numbers

## Features

- Automatically detects CSV delimiters (comma, tab, semicolon)
- Extracts sensitive data patterns from all cells
- Normalizes SSN format to XXX-XX-XXXX
- Provides summary statistics and unique counts
- Handles multiple CSV files in a single run

## Usage

```bash
python3 process_csv.py <csv_file> [csv_file2] ...
```

### Examples

Process a single CSV file:
```bash
python3 process_csv.py myfile.csv
```

Process multiple CSV files:
```bash
python3 process_csv.py myfile.csv dlp_pci_small_csv.csv
```

## Output

The script provides a detailed summary including:
- Total rows processed
- Column names
- Count of each type of sensitive data found
- Unique values (with masking for credit cards)
- Location information (row and column) for each finding

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Pattern Detection

The script uses regex patterns to identify:
- **SSN**: 9-digit numbers in formats XXX-XX-XXXX, XXX XX XXXX, or XXXXXXXXX
- **Credit Cards**: 13-19 digit numbers, typically in groups of 4
- **Account Numbers**: 8-17 digit numbers (excluding SSNs and credit cards)
- **Routing Numbers**: 9-digit numbers in banking context

## Security Note

This tool is designed for data analysis and compliance purposes. Always handle sensitive data according to your organization's security policies.
