# earthdata-hashdiff

This repository contains functionality to read Earth science data file formats
and hash the contents of those files into a JSON object. This enables the easy
storage of a smaller artefact for tasks such as regression tests, while omitting
metadata and data attributes that may change between test executions (such as
timestamps in history attributes).

## `pre-commit` hooks

This repository uses [pre-commit](https://pre-commit.com/) to enable pre-commit
checks that enforce coding standard best practices. These include:

* Removing trailing whitespaces.
* Removing blank lines at the end of a file.
* Ensure JSON files have valid formats.
* [ruff](https://github.com/astral-sh/ruff) Python linting checks.
* [black](https://black.readthedocs.io/en/stable/index.html) Python code
  formatting checks.

To enable these checks locally:

```bash
# Install pre-commit Python package:
pip install pre-commit

# Install the git hook scripts:
pre-commit install
```

## Versioning

Releasees for the `earthdata-hashdiff` adhere to [semantic version](https://semver.org/)
numbers: major.minor.patch.

* Major increments: These are non-backwards compatible API changes.
* Minor increments: These are backwards compatible API changes.
* Patch increments: These updates do not affect the API to the service.
