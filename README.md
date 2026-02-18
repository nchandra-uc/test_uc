# Image File Analysis Tool

This repository contains tools for analyzing image files to extract and analyze financial data (account numbers, routing numbers, etc.).

## Tools

### 1. `image_analyzer.py` - Image OCR and Analysis
Analyzes image files (PNG, JPG, etc.) to extract text using OCR and identify financial data.

**Features:**
- Extracts text from images using Tesseract OCR
- Identifies account numbers (8-12 digits)
- Identifies routing numbers (9 digits)
- Finds account-routing pairs
- Analyzes structured data
- Generates JSON reports

**Usage:**
```bash
python3 image_analyzer.py <image_path>
```

**Example:**
```bash
python3 image_analyzer.py image.png
```

**Requirements:**
```bash
pip install pillow pytesseract
sudo apt-get install tesseract-ocr  # On Linux
# On macOS: brew install tesseract
# On Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. `analyze_extracted_data.py` - Text Data Analysis
Analyzes already-extracted text data containing financial information.

**Features:**
- Parses text files with account/routing numbers
- Identifies unique account and routing numbers
- Creates account-routing pairs
- Provides statistics and distributions
- Generates JSON reports

**Usage:**
```bash
python3 analyze_extracted_data.py <text_file>
```

**Example:**
```bash
python3 analyze_extracted_data.py myfile2.txt
```

## Analysis Results

Both tools generate:
- Console output with summary statistics
- JSON file with detailed analysis results

### Sample Output

```
ANALYSIS SUMMARY
============================================================

Overall Statistics:
  - Total records processed: 50
  - Unique account numbers: 100
  - Unique routing numbers: 49
  - Account-Routing pairs: 100

Account Number Analysis:
  - Total unique accounts: 100
  - Length distribution:
      12 digits: 100 accounts

Routing Number Analysis:
  - Total unique routings: 49
  - Prefix distribution (first 2 digits):
      01xx: 3 routings
      02xx: 9 routings
      ...
```

## Example Analysis

The file `myfile2.txt` contains extracted financial data that was analyzed:

- **50 records** processed
- **100 unique account numbers** (all 12 digits)
- **49 unique routing numbers** (all 9 digits)
- **100 account-routing pairs** identified

See `myfile2_analysis.json` for detailed results.

## Notes

- Account numbers are typically 8-12 digits
- Routing numbers (ABA numbers) are exactly 9 digits
- The tools can handle various formats including tab-separated, space-separated, and labeled data
- OCR accuracy depends on image quality and text clarity
