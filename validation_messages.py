"""Custom validation messages for DLP test data checks."""

MESSAGES = {
    "ssn_invalid_format": "SSN must contain exactly 9 digits in XXX-XX-XXXX format.",
    "ssn_invalid_area": "SSN area number is invalid (000, 666, or 900-999 are not allowed).",
    "ssn_invalid_group": "SSN group number cannot be 00.",
    "ssn_invalid_serial": "SSN serial number cannot be 0000.",
    "credit_card_invalid": "Credit card number failed validation (must be 13-19 digits and pass Luhn check).",
    "routing_invalid": "Bank routing number must be exactly 9 digits.",
    "account_invalid": "Bank account number must be 4-17 digits.",
    "file_not_found": "File not found: {path}",
    "validation_passed": "All checked values passed validation.",
    "validation_failed": "Validation failed with {count} issue(s).",
}
