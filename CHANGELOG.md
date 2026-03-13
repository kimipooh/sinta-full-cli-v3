# Changelog

## [1.1.0] - 2026-03-13

### Added
- Added `--fetch-mode basic|detail`
- Added optional profile-page enrichment in `detail` mode
- Added additional fields such as `journal_id`, `profile_url`, `website_url`, `subject_area`, and fetch status fields

### Changed
- Preserved the original 1.0.1 search-result extraction as the basis of `basic` mode
- Kept the original core metadata fields available in both modes
- Added randomized waiting and simple backoff for detail retrieval

### Fixed
- Fixed malformed duplicated `profile_url`
- Restored correct `journal_name` extraction from `div.affil-name`
- Restored the full file set from 1.0.1 while extending functionality

## [1.0.1] - 2026-03-09

Documentation and minor fixes.


### Adjusted in packaged 1.1.0
- basic mode now outputs only stable search-result fields
- detail mode outputs the agreed enriched field set
- ISSN parsing now preserves trailing X
- Google Scholar value follows the SINTA-registered value policy
- SINTA level display is normalized (e.g. `S3 Accredited`)
