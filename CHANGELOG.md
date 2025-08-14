# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.1] - 2025-08-14

### Changed

- Keys in JSON output files are now sorted alphabetically. This does not affect
  comparisons against JSON files that are not alphabetically sorted, as the
  comparison first checks the sets of keys in both files, and then ensures that
  the value assigned to the same key in both files are the same. Neither of
  these operations are dependent on the key ordering in the file itself. This
  does, however, prepare the way for future functionality to display the
  difference between two files with different hash values.

## [v1.0.0] - 2025-07-22

### Added

- Initial repository setup, including README and LICENSE.
- Migration of hashing code from Harmony Regression Tests repository.
- Addition of unit tests.
- Packaging using hatch.
- pre-commit CI/CD checks, including mypy and ruff.
- CI/CD workflows as GitHub actions.

[v1.0.1]: https://github.com/nasa/earthdata-hashdiff/releases/tag/1.0.1
[v1.0.0]: https://github.com/nasa/earthdata-hashdiff/releases/tag/1.0.0
