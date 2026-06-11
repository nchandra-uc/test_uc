#!/usr/bin/env python3
"""Run multiple validations on DLP test files with custom messages."""

import re
import sys
from pathlib import Path

from validation_messages import SUMMARY, VALIDATION_HEADER, VALIDATIONS

SSN_PATTERN = re.compile(r"\b(\d{3})[-\s]?(\d{2})[-\s]?(\d{4})\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(\d{13,19})\b")
ROUTING_PATTERN = re.compile(r"(?:Routing|Bank Routing)\s*#?\s*:?\s*(\d{9})\b", re.IGNORECASE)
ACCOUNT_PATTERN = re.compile(r"(?:Account|Deposit Account)\s*#?\s*:?\s*(\d{4,17})\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b(\d{3}[-\s]?\d{3}[-\s]?\d{4})\b")


def luhn_check(number: str) -> bool:
    digits = [int(d) for d in number]
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def validate_ssn(area: str, group: str, serial: str) -> str | None:
    messages = VALIDATIONS["ssn"]
    if area == "000" or area == "666" or 900 <= int(area) <= 999:
        return messages["invalid_area"]
    if group == "00":
        return messages["invalid_group"]
    if serial == "0000":
        return messages["invalid_serial"]
    return None


def validate_phone(value: str) -> str | None:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 10:
        return VALIDATIONS["phone"]["invalid"]
    return None


def check_file(path: Path) -> list[str]:
    if not path.exists():
        return [SUMMARY["file_not_found"].format(path=path)]

    text = path.read_text(encoding="utf-8", errors="replace")
    issues: list[str] = []

    for match in SSN_PATTERN.finditer(text):
        area, group, serial = match.groups()
        error = validate_ssn(area, group, serial)
        if error:
            label = VALIDATIONS["ssn"]["label"]
            issues.append(f"{path.name}: {label} {match.group(0)} - {error}")

    for match in CREDIT_CARD_PATTERN.finditer(text):
        number = match.group(1)
        if len(number) in (13, 15, 16, 19) and not luhn_check(number):
            label = VALIDATIONS["credit_card"]["label"]
            message = VALIDATIONS["credit_card"]["invalid"]
            issues.append(f"{path.name}: {label} {number} - {message}")

    for match in ROUTING_PATTERN.finditer(text):
        routing = match.group(1)
        if len(routing) != 9:
            label = VALIDATIONS["routing"]["label"]
            issues.append(f"{path.name}: {label} {routing} - {VALIDATIONS['routing']['invalid']}")

    for match in ACCOUNT_PATTERN.finditer(text):
        account = match.group(1)
        if not 4 <= len(account) <= 17:
            label = VALIDATIONS["account"]["label"]
            issues.append(f"{path.name}: {label} {account} - {VALIDATIONS['account']['invalid']}")

    if path.suffix == ".csv":
        for match in PHONE_PATTERN.finditer(text):
            phone = match.group(1)
            error = validate_phone(phone)
            if error:
                label = VALIDATIONS["phone"]["label"]
                issues.append(f"{path.name}: {label} {phone} - {error}")

    return issues


def main() -> int:
    files = [
        Path("myfile.csv"),
        Path("myfile2.txt"),
        Path("dlp_pci_small_csv.csv"),
        Path("validation_message.txt"),
    ]

    print(VALIDATION_HEADER)
    print()

    all_issues: list[str] = []
    for file_path in files:
        all_issues.extend(check_file(file_path))

    if all_issues:
        print(SUMMARY["validation_failed"].format(count=len(all_issues)))
        for issue in all_issues:
            print(f"  - {issue}")
        return 1

    print(SUMMARY["validation_passed"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
