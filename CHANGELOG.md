# Changelog

All notable changes to **SINTA 3 Journal Metadata CLI** will be documented in this file.

The format is based on *Keep a Changelog* and the project follows **Semantic Versioning**.

---

## [1.0.0] - 2026-03-08

### Added
- Initial public release of **sinta-full-cli-v3.py**
- Command line interface for retrieving journal metadata from **SINTA 3**
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

---
