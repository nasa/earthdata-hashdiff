"""A module containing common functionality used by multiple regression
tests. These functions are kept out of the Jupyter notebook to increase the
readability of the regression test suite.

This module focuses on comparing output specifically with xarray.
"""

import json

from earthdata_hashdiff.generate import (
    XARRAY_DECODE_DEFAULTS,
    get_hashes_from_xarray_input,
)


def matches_reference_hash_file_using_xarray(
    request_output_path: str,
    reference_file_path: str,
    skipped_variables_or_groups: set[str] = set(),
    skipped_metadata_attributes: set[str] = set(),
    xarray_kwargs: dict = XARRAY_DECODE_DEFAULTS,
) -> bool:
    """Generate hashes for request output and compare to reference file.

    Args:
        request_output_path: netCDF4 or HDF5 file retrieved from a Harmony request.
        reference_file_path: File containing generated SHA256 values for every
            group and variable in the original test output.
        skipped_variables_or_groups: Variables or groups that are known to vary
            between different test executions. For example, `/subset_files` in the
            output from SAMBAH, which varies between production and UAT.
        skipped_metadata_attributes: Names of metadata attributes to omit from
            the derivation of the SHA256 hash for all group and variable metadata.
            These will be values that are known to vary and are in addition to
            `history` and `history_json`. The main use-case is metadata attributes
            with timestamps dependent on request execution time.
        xarray_kwargs: dict containing arguments used by `xarray` to open the
            request output file as a `DataTree` object. Default is to switch off all
            decoding options.

    """
    actual_hashes = get_hashes_from_xarray_input(
        request_output_path,
        skipped_metadata_attributes=skipped_metadata_attributes,
        xarray_kwargs=xarray_kwargs,
    )

    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_hashes = json.load(file_handler)

    has_expected_groups_and_variables = set(actual_hashes.keys()) == set(
        reference_hashes.keys()
    )
    has_expected_hashes = all(
        actual_hashes.get(variable_or_group_name) == reference_hash
        for variable_or_group_name, reference_hash in reference_hashes.items()
        if variable_or_group_name not in skipped_variables_or_groups
    )

    return has_expected_groups_and_variables and has_expected_hashes


# Aliases for matches_reference_hash_file_using_xarray (for public API).
nc4_matches_reference_hash_file = matches_reference_hash_file_using_xarray
h5_matches_reference_hash_file = matches_reference_hash_file_using_xarray
