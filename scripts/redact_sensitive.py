#!/usr/bin/env python3
"""
Redact common sensitive identifiers from files.

Defaults:
- Redacts US SSNs in formats like:
  - 123-45-6789
  - 123 45 6789
  - 123456789
- Redacts likely payment card numbers (13-19 digits, allowing spaces/hyphens) using Luhn check.

This script is intentionally dependency-free.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SSN_RE = re.compile(r"\b(\d{3})[- ]?(\d{2})[- ]?(\d{4})\b")

# Candidate PANs are 13-19 digits, possibly separated by spaces or hyphens.
# We later Luhn-check and avoid redacting obvious non-PAN contexts where possible.
PAN_CANDIDATE_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")


def luhn_is_valid(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for i, ch in enumerate(digits):
        d = ord(ch) - 48
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def normalize_digits(s: str) -> str:
    return re.sub(r"\D+", "", s)


@dataclass(frozen=True)
class RedactionStats:
    ssn_redactions: int = 0
    pan_redactions: int = 0


def redact_ssns(text: str) -> tuple[str, int]:
    count = 0

    def _sub(_: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return "[REDACTED_SSN]"

    return SSN_RE.sub(_sub, text), count


def redact_pans(text: str) -> tuple[str, int]:
    # We replace only the exact matched span when it passes Luhn.
    # Keep replacement length constant-ish to preserve surrounding formatting.
    count = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal count
        candidate = m.group(0)
        digits = normalize_digits(candidate)
        if not (13 <= len(digits) <= 19):
            return candidate
        if not luhn_is_valid(digits):
            return candidate
        count += 1
        return "[REDACTED_PAN]"

    return PAN_CANDIDATE_RE.sub(_sub, text), count


def redact_text(text: str, *, do_ssn: bool, do_pan: bool) -> tuple[str, RedactionStats]:
    stats = RedactionStats()
    if do_ssn:
        text, c = redact_ssns(text)
        stats = RedactionStats(ssn_redactions=stats.ssn_redactions + c, pan_redactions=stats.pan_redactions)
    if do_pan:
        text, c = redact_pans(text)
        stats = RedactionStats(ssn_redactions=stats.ssn_redactions, pan_redactions=stats.pan_redactions + c)
    return text, stats


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for p in paths:
        if p.is_dir():
            for root, _dirs, files in os.walk(p):
                for f in files:
                    yield Path(root) / f
        else:
            yield p


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Redact SSNs and PANs from files.")
    parser.add_argument("input", nargs="+", help="Input file(s) or directory(ies).")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help="Write redacted copies into this directory, preserving relative paths.",
    )
    parser.add_argument("--suffix", default=".redacted", help="Suffix inserted before the file extension.")
    parser.add_argument("--no-ssn", action="store_true", help="Disable SSN redaction.")
    parser.add_argument("--no-pan", action="store_true", help="Disable payment card number redaction.")
    parser.add_argument("--encoding", default="utf-8", help="File encoding (default: utf-8).")
    args = parser.parse_args(argv)

    in_paths = [Path(p) for p in args.input]
    out_dir = Path(args.output_dir).resolve() if args.output_dir else None
    do_ssn = not args.no_ssn
    do_pan = not args.no_pan

    total_ssn = 0
    total_pan = 0
    files_written = 0

    for p in iter_files(in_paths):
        if not p.is_file():
            continue

        # Best-effort skip binary-ish files (e.g., docx) to avoid garbage output.
        # Users can still force handling by extracting text first.
        if p.suffix.lower() in {".docx", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            continue

        try:
            data = p.read_bytes()
        except OSError:
            continue

        # Quick binary heuristic: NUL bytes
        if b"\x00" in data:
            continue

        try:
            text = data.decode(args.encoding, errors="strict")
        except UnicodeDecodeError:
            text = data.decode(args.encoding, errors="replace")

        redacted, stats = redact_text(text, do_ssn=do_ssn, do_pan=do_pan)
        if redacted == text:
            continue

        total_ssn += stats.ssn_redactions
        total_pan += stats.pan_redactions

        if out_dir:
            # Preserve relative path from the provided root if possible; otherwise from CWD.
            rel = None
            for root in in_paths:
                base = root.resolve()
                if base.is_file():
                    base = base.parent
                try:
                    rel = p.resolve().relative_to(base)
                    break
                except ValueError:
                    continue
            if rel is None:
                rel = p.name
                rel = Path(rel)
            out_path = out_dir / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path = out_path.with_name(out_path.stem + args.suffix + out_path.suffix)
        else:
            out_path = p.with_name(p.stem + args.suffix + p.suffix)

        out_path.write_text(redacted, encoding=args.encoding, errors="replace")
        files_written += 1

    print(
        f"Done. Files written: {files_written}. "
        f"SSNs redacted: {total_ssn}. PANs redacted: {total_pan}.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

