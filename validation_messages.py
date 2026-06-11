"""Custom messages for each validation type."""

VALIDATION_HEADER = "Custom message for validations"

VALIDATIONS = {
    "ssn": {
        "label": "SSN",
        "invalid_format": "SSN must contain exactly 9 digits in XXX-XX-XXXX format.",
        "invalid_area": "SSN area number is invalid (000, 666, or 900-999 are not allowed).",
        "invalid_group": "SSN group number cannot be 00.",
        "invalid_serial": "SSN serial number cannot be 0000.",
    },
    "credit_card": {
        "label": "Credit card",
        "invalid": "Credit card number failed validation (must be 13-19 digits and pass Luhn check).",
    },
    "routing": {
        "label": "Routing number",
        "invalid": "Bank routing number must be exactly 9 digits.",
    },
    "account": {
        "label": "Account number",
        "invalid": "Bank account number must be 4-17 digits.",
    },
    "phone": {
        "label": "Phone number",
        "invalid": "Phone number must contain 10 digits (optionally formatted with dashes or spaces).",
    },
}

SUMMARY = {
    "file_not_found": "File not found: {path}",
    "validation_passed": "All validations passed.",
    "validation_failed": "Validations failed with {count} issue(s).",
}
