# DLP Image Handler

A Python tool for detecting sensitive information in images using OCR (Optical Character Recognition) and pattern matching.

## Features

- Extracts text from images using Tesseract OCR
- Detects various types of sensitive data:
  - Credit card numbers
  - Social Security Numbers (SSN)
  - Email addresses
  - Phone numbers
  - Account numbers
  - Routing numbers
  - IP addresses
- Generates detailed scan reports
- Masks sensitive data in reports for safe viewing

## Installation

1. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # macOS
   brew install tesseract
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python dlp_image_handler.py <image_path>
```

### Example

```bash
python dlp_image_handler.py dlpimage.JPG
```

The script will:
1. Load and analyze the image
2. Extract text using OCR
3. Scan for sensitive data patterns
4. Display results in the console
5. Save a detailed report to `<image_name>.dlp_report.txt`

## Output

The tool generates a report showing:
- Image metadata (size, format)
- Number of sensitive data findings
- Type and location of each finding
- Masked values for safe viewing

## Supported Image Formats

- JPEG/JPG
- PNG
- GIF
- BMP
- TIFF
- And other formats supported by PIL/Pillow
