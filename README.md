# earthdata-hashdiff

This repository contains functionality to read Earth science data file formats
and hash the contents of those files into a JSON object. This enables the easy
storage of a smaller artefact for tasks such as regression tests, while omitting
metadata and data attributes that may change between test executions (such as
timestamps in history attributes).

## Features

### Generating hashed files

...

### Comparisons against reference files

...

## Installing

### Using pip

Install the latest version of the package from PyPI using pip:

```bash
$ pip install earthdata-hashdiff
```

### Other methods:

For local development, it is possible to clone the repository and then install
the version being developed in editable mode:

```bash
$ git clone https://github.com/nasa/earthdata-hashdiff
$ cd earthdata-hashdiff
$ pip install -e .
```

## Developing

Development within this repository should occur on a feature branch. Pull
Requests (PRs) are created with a target of the `main` branch before being
reviewed and merged.

Releases are created when a feature branch is merged to `main` and that branch
also contains an update to the `earthdata_hashdiff.__about__.py` file.

### Development Setup:

Prerequisites:

  - Python 3.10+, ideally installed in a virtual environment, such as `pyenv`
    or `conda`.
  - A local copy of this repository.

As an example to set up a conda virtual environment:

```bash
conda create --name earthdata-hashdiff python=3.12 --channel conda-forge \
    --override-channels -y
conda activate earthdata-hashdiff
```

Install dependencies:

```
pip install -r requirements.txt -r dev-requirements.txt -r tests/test_requirements.txt
```

## Running tests

`earthdata-hashdiff` uses `pytest` to execute tests. Once test requirements have
been installed via pip, you can execute the tests:

```
pytest tests
```

The CI/CD workflows that execute the tests also make use of `pytest` plugins to
additionally create code test coverage reports and JUnit XML output. These
extra outputs can be produced with the following command:

```
pytest tests --junitxml=tests/reports/earthdata-hashdiff_junit.xml \
    --cov earthdata_hashdiff --cov-report html:tests/coverage --cov-report term
```

This will produce:

* The test results (pass/fail) in the terminal.
* A coverage report in the terminal running the tests. The coverage report will
  cover the contents within the `earthdata_hashdiff` directory.
* An HTML format coverage report in the `tests/coverage` directory. The entry
  point for this output is `tests/coverage/index.html`.
* JUnit style output in `tests/reports/earthdata-hashdiff_junit.xml`.

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

Releases for the `earthdata-hashdiff` adhere to [semantic version](https://semver.org/)
numbers: major.minor.patch.

* Major increments: These are non-backwards compatible API changes.
* Minor increments: These are backwards compatible API changes.
* Patch increments: These updates do not affect the API to the service.

## Contibuting

Contributions are welcome! For more information see `CONTRIBUTING.md`.
