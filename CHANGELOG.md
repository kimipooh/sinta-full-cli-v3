# Changelog

All notable changes to **SINTA Journal Metadata CLI** will be documented in this file.

The format is based on *Keep a Changelog* and the project follows **Semantic Versioning**.

---

## [1.0.1] - 2026-03-09

### Changed
- Clarified documentation to avoid confusion between **SINTA journal ranking (S1–S6)** and the SINTA platform itself
- Updated README title from **"SINTA 3 Journal Metadata CLI"** to **"SINTA Journal Metadata CLI"**
- Minor wording updates in README and README_ja

### Fixed
- Corrected CLI command typo (`sinta-full-cli_v3.py` → `sinta-full-cli-v3.py`)
- Minor comment improvements in the Python source code

### Notes
No changes to the CLI functionality or metadata extraction logic.

---

## [1.0.0] - 2026-03-08

### Added
- Initial public release of **sinta-full-cli-v3.py**
- Command line interface for retrieving journal metadata from **SINTA**
- Support for the current domain:
  - https://sinta.kemdiktisaintek.go.id

### Metadata Extraction
- journal_name
- sinta_level
- p_issn
- e_issn
- affiliation
- sinta_score_3y
- sinta_score_overall
- h_index_google
- h_index_sinta
- citations_google
- citations_sinta

### CLI Features
- Keyword search (`-q / --query`)
- Search mode selection (`-m title | all`)
- Affiliation filtering (`-a / --affil`)
- Output format selection (`-f json | csv`)
- JSON output for pipeline processing
- CSV export support

### Technical Features
- HTML parsing with BeautifulSoup
- HTTP requests using requests
- Randomized delay to reduce server load
- Browser-like User-Agent header
- Regex extraction for ISSN values

### Documentation
- English README (`README.md`)
- Japanese README (`README_ja.md`)
- Mermaid architecture diagram
- Usage examples with `jq`

### Repository Setup
- MIT License
- requirements.txt
- CITATION.cff for GitHub citation support
- Zenodo DOI integration prepared