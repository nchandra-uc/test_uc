# PDF Financial Data Extraction

This project processes PDF files to extract financial information including:
- Account Numbers
- Deposit Account Numbers  
- Routing Numbers

## Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Process a PDF file:

```bash
python process_pdf.py <pdf_file> [output_csv]
```

### Examples

```bash
# Process myfilecsv.pdf and save to myfilecsv.csv
python process_pdf.py myfilecsv.pdf

# Process myfilecsv.pdf and save to custom_output.csv
python process_pdf.py myfilecsv.pdf custom_output.csv
```

## Features

- Extracts account numbers (9-17 digits)
- Extracts deposit account numbers
- Extracts routing numbers (9 digits)
- Supports various text patterns and formats
- Outputs results to CSV format
- Removes duplicates automatically

## Output Format

The script generates a CSV file with three columns:
- Account Number
- Deposit Account Number
- Routing Number
