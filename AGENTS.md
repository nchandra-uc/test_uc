## Cursor Cloud specific instructions

This is a **data-only repository** containing DLP (Data Loss Prevention) sample/test data files. It has no source code, applications, build systems, package managers, tests, or services.

### Repository contents

| File | Description |
|------|-------------|
| `myfile.csv` | PII test data: US SSNs, names, addresses, phone numbers, birthdates |
| `myfile2.txt` | Financial test data: bank account numbers, routing numbers |
| `dlp_pci_small_csv.csv` | PCI test data: credit card numbers, SSNs, bank accounts |
| `dlp_phi_small_json.json` | PHI test data: pharmaceutical/drug product listings |
| `dlp_phi_small_documents.txt` | PHI test data: identical pharmaceutical/drug listings |

### Development notes

- **No dependencies to install** — no `package.json`, `requirements.txt`, `Makefile`, or similar.
- **No services to run** — there is no application, server, or build pipeline.
- **No tests or linting** — there are no automated tests or lint configurations.
- The git history shows many prior agent branches that added/removed various scripts and analyses, but none of that code was merged to `main`.
- The `.cursor/environment.json` uses a snapshot-based configuration (no Dockerfile).
