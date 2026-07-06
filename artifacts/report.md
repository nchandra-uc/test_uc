# Repository Summary Report

**Repository:** `nchandra-uc/test_uc`
**Default Branch:** `main`
**Generated:** 2026-07-06

---

## Overview

This is a **data-only repository** used for **Data Loss Prevention (DLP) testing**. It contains no application source code, build systems, or runtime dependencies. The repository holds sample datasets that include synthetic sensitive data spanning PII (Personally Identifiable Information), PCI (Payment Card Industry), and PHI (Protected Health Information) categories.

---

## Repository Statistics

| Metric | Value |
|---|---|
| Total commits (all branches) | 79 |
| Commits on `main` | 8 |
| Total branches | 118 |
| Contributors | 3 (`Cursor Agent`, `nchandra-uc`, `ns-ayadav`) |
| First commit | 2025-12-16 |
| Latest commit on `main` | 2026-02-07 |
| Total tracked files | 5 data files + 1 config |
| Total data size | ~60 KB |

---

## File Inventory

| File | Format | Size | Lines | Content Description |
|---|---|---|---|---|
| `myfile.csv` | CSV | 12 KB | 289 | US Social Security Numbers (SSNs) with demographic data (names, addresses, phone numbers) |
| `myfile2.txt` | TXT | 8 KB | 50 | Bank account numbers, deposit account numbers, and ABA routing numbers |
| `dlp_phi_small_documents.txt` | TXT | 12 KB | 255 | Pharmaceutical / drug product listings with active ingredients |
| `dlp_phi_small_json.json` | JSON | 12 KB | 255 | Same pharmaceutical listing as above in JSON-compatible format |
| `dlp_pci_small_csv.csv` | CSV | 16 KB | 410 | Credit card numbers, SSNs, bank accounts, and names with active/retired status |

---

## Sensitive Data Classification

### PII (Personally Identifiable Information)
- **SSNs**: ~288 Social Security Numbers across `myfile.csv` and `dlp_pci_small_csv.csv`
- **Names**: Full names associated with SSN and financial records
- **Addresses**: Street addresses, cities, states, ZIP codes
- **Phone numbers**: US phone numbers in multiple formats

### PCI (Payment Card Industry Data)
- **Credit card numbers**: Visa, MasterCard, Discover, and Diners Club card numbers in `dlp_pci_small_csv.csv`
- **Bank account numbers**: 50 account/deposit account entries in `myfile2.txt`
- **Routing numbers (ABA)**: 50 ABA routing numbers in `myfile2.txt`
- **Checking account numbers**: Additional checking account references in `dlp_pci_small_csv.csv`

### PHI (Protected Health Information)
- **Drug/medication names**: 255 pharmaceutical product entries (brand names, generics, dosage forms)
- **Active ingredients**: Chemical compound names and formulations
- Present in both `dlp_phi_small_documents.txt` and `dlp_phi_small_json.json`

---

## Branch Activity

The repository has **118 branches**, the vast majority created by automated `Cursor Agent` runs. Common branch themes include:

- **Data analysis branches** (account/routing data, CSV processing, file analysis)
- **Code experiment branches** (C qsort programs, Perl scripts, Node.js setup)
- **Greeting/hello-world branches** (simple test outputs)
- **DLP-specific branches** (image handling, PDF processing, sensitive data detection)

Most branches are single-commit forks off `main` used for isolated experiments; none have been merged back.

---

## Dependencies

This repository has **no software dependencies**. There are no `package.json`, `requirements.txt`, `Makefile`, `Dockerfile`, or any other build/dependency manifest files. The repository is purely a collection of static data files used as test fixtures for DLP scanning and sensitive-data detection workflows.

---

## Architecture

```
test_uc/
├── .cursor/
│   └── environment.json      # Cursor IDE environment config
├── myfile.csv                 # PII dataset (SSNs + demographics)
├── myfile2.txt                # PCI dataset (bank accounts + routing numbers)
├── dlp_phi_small_documents.txt # PHI dataset (drug listings, text format)
├── dlp_phi_small_json.json    # PHI dataset (drug listings, JSON format)
└── dlp_pci_small_csv.csv      # PCI/PII dataset (credit cards + SSNs + names)
```

---

## Key Observations

1. **No executable code on `main`**: The default branch contains only data files. Code experiments (C, Perl, Python, Node.js) exist only on unmerged feature branches.
2. **DLP test corpus**: The data files form a comprehensive test set covering all three major sensitive-data categories (PII, PCI, PHI), useful for validating DLP scanner rules.
3. **Data duplication**: `dlp_pci_small_csv.csv` contains the same person/SSN block repeated 4 times, and `dlp_phi_small_json.json` mirrors `dlp_phi_small_documents.txt` exactly.
4. **High branch churn**: 70 of 79 total commits are attributed to `Cursor Agent`, indicating heavy automated experimentation without consolidation.
