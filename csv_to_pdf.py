#!/usr/bin/env python3
"""
Convert CSV file to PDF format
"""
import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import sys
import os

def csv_to_pdf(csv_file, pdf_file):
    """Convert CSV file to PDF"""
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Add title
    title = Paragraph("CSV Data Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Read CSV file
    data = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            data.append(row)
    
    if not data:
        print("Error: CSV file is empty")
        return False
    
    # Get headers
    headers = data[0]
    rows = data[1:]
    
    # Prepare table data
    table_data = [headers] + rows
    
    # Create table
    # Calculate column widths based on content
    num_cols = len(headers)
    col_widths = [doc.width / num_cols] * num_cols
    
    # Create table with appropriate styling
    table = Table(table_data, colWidths=col_widths)
    
    # Apply table style
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    print(f"Successfully created PDF: {pdf_file}")
    return True

if __name__ == "__main__":
    csv_file = "myfile.csv"
    pdf_file = "myfilecsv.pdf"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        pdf_file = sys.argv[2]
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        sys.exit(1)
    
    csv_to_pdf(csv_file, pdf_file)
