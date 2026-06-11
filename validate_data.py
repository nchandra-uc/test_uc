#!/usr/bin/env python3
"""Validate sensitive data in DLP test files using custom error messages."""

import re
import sys
from pathlib import Path

from validation_messages import MESSAGES

SSN_PATTERN = re.compile(r"\b(\d{3})[-\s]?(\d{2})[-\s]?(\d{4})\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(\d{13,19})\b")
ROUTING_PATTERN = re.compile(r"(?:Routing|Bank Routing)\s*#?\s*:?\s*(\d{9})\b", re.IGNORECASE)
ACCOUNT_PATTERN = re.compile(r"(?:Account|Deposit Account)\s*#?\s*:?\s*(\d{4,17})\b", re.IGNORECASE)


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
    if area == "000" or area == "666" or 900 <= int(area) <= 999:
        return MESSAGES["ssn_invalid_area"]
    if group == "00":
        return MESSAGES["ssn_invalid_group"]
    if serial == "0000":
        return MESSAGES["ssn_invalid_serial"]
    return None


def check_file(path: Path) -> list[str]:
    if not path.exists():
        return [MESSAGES["file_not_found"].format(path=path)]

    text = path.read_text(encoding="utf-8", errors="replace")
    issues: list[str] = []

    for match in SSN_PATTERN.finditer(text):
        area, group, serial = match.groups()
        error = validate_ssn(area, group, serial)
        if error:
            issues.append(f"{path.name}: SSN {match.group(0)} - {error}")

    for match in CREDIT_CARD_PATTERN.finditer(text):
        number = match.group(1)
        if len(number) in (13, 15, 16, 19) and not luhn_check(number):
            issues.append(
                f"{path.name}: Credit card {number} - {MESSAGES['credit_card_invalid']}"
            )

    for match in ROUTING_PATTERN.finditer(text):
        routing = match.group(1)
        if len(routing) != 9:
            issues.append(
                f"{path.name}: Routing {routing} - {MESSAGES['routing_invalid']}"
            )

    for match in ACCOUNT_PATTERN.finditer(text):
        account = match.group(1)
        if not 4 <= len(account) <= 17:
            issues.append(
                f"{path.name}: Account {account} - {MESSAGES['account_invalid']}"
            )

    return issues


def main() -> int:
    files = [
        Path("myfile.csv"),
        Path("myfile2.txt"),
        Path("dlp_pci_small_csv.csv"),
        Path("validation_message.txt"),
    ]

    all_issues: list[str] = []
    for file_path in files:
        all_issues.extend(check_file(file_path))

    if all_issues:
        print(MESSAGES["validation_failed"].format(count=len(all_issues)))
        for issue in all_issues:
            print(f"  - {issue}")
        return 1

    print(MESSAGES["validation_passed"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
