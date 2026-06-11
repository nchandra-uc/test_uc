# AGENTS.md

## Cursor Cloud specific instructions

This repository is **data-only**. It contains synthetic DLP (Data Loss Prevention)
sample datasets used as test inputs (PII / PHI / PCI examples). There is **no
application** here:

- No source code, no `package.json` / `requirements.txt` / other dependency manifests.
- No build system, no automated tests, no lint configuration, no services to run.
- Nothing to install — the only tooling needed to inspect the files (Python 3) is
  already present in the base image. The startup update script is intentionally a no-op.

### Files

- `myfile.csv` — CSV with a header (`US SSN, gender, birthdate, ...`) and 288 data rows. Encoded UTF-8 with BOM, so read it with `encoding="utf-8-sig"`.
- `dlp_pci_small_csv.csv` — CSV-style PCI sample data (~410 rows, CRLF line endings).
- `myfile2.txt` — tab-separated bank account/routing sample text (50 lines).
- `dlp_phi_small_documents.txt` — plain-text list of drug names (255 lines, CRLF).
- `dlp_phi_small_json.json` — **despite the `.json` extension this is NOT valid JSON**; it is the same plain-text drug list as the `.txt` file. Do not attempt to `json.load()` it.

### Working with the data

There is no app to build/run/test. To "use" the repo, parse the files with standard
tools, e.g. Python's built-in `csv` module (remember the BOM on `myfile.csv` and the
mislabeled `.json` file noted above).
