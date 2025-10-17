"""A module containing common functionality used by multiple regression
tests. These functions are kept out of the Jupyter notebook to increase the
readability of the regression test suite.

This module focuses on comparing output specifically with xarray.
"""

import json
from collections.abc import Callable
from os.path import splitext
from typing import Literal, TypedDict, overload

from earthdata_hashdiff.generate import (
    GEOTIFF_HASH_KEY,
    XARRAY_DECODE_DEFAULTS,
    get_hash_from_geotiff_file,
    get_hashes_from_xarray_input,
)

HashedFileTypes = Literal['GeoTIFF', 'HDF-5', 'netCDF4']


class XarrayParams(TypedDict):
    """Typing for unique inputs to matches_reference_hash_file_using_xarray."""

    skipped_variables_or_groups: set[str]
    skipped_metadata_attributes: set[str]
    xarray_kwargs: dict


class GeoTIFFParams(TypedDict):
    """Typing for unique inputs to geotiff_matches_reference_hash_file."""

    skipped_metadata_tags: set[str]


@overload
def matches_reference_hash_file(
    binary_file_path: str,
    reference_file_path: str,
    **kwargs: XarrayParams,
) -> bool: ...


@overload
def matches_reference_hash_file(
    binary_file_path: str,
    reference_file_path: str,
    **kwargs: GeoTIFFParams,
) -> bool: ...


def matches_reference_hash_file(
    binary_file_path: str,
    reference_file_path: str,
    **kwargs: XarrayParams | GeoTIFFParams,
) -> bool:
    """Generate hashes for request output and compare to reference file.

    Possible kwargs:

    * skipped_variables_or_groups - For netCDF4 or HDF-5 files.
    * skipped_metadata_attributes - For netCDF4 or HDF-5 files.
    * xarray_kwargs - For netCDF4 or HDF-5 files.
    * skipped_metadata_tags - For GeoTIFF files.

    """
    file_type_comparisons: dict[HashedFileTypes, Callable[..., bool]] = {
        'GeoTIFF': geotiff_matches_reference_hash_file,
        'HDF-5': h5_matches_reference_hash_file,
        'netCDF4': nc4_matches_reference_hash_file,
    }

    file_type = guess_file_type(binary_file_path)

    comparison_function = file_type_comparisons.get(file_type)

    if comparison_function is None:
        raise ValueError('file_type not recognised: {file_type}')

    return comparison_function(binary_file_path, reference_file_path, **kwargs)


def guess_file_type(file_path: str) -> HashedFileTypes:
    """Return a file type guessed based on the extension for the file.

    If the extension is an entirely unrecognised one, a `ValueError` is raised.

    """
    file_extension = splitext(file_path)[-1].lower()

    if file_extension in ['.tif', '.tiff']:
        file_type: HashedFileTypes = 'GeoTIFF'
    elif file_extension in ['.h5', '.hdf', '.hdf5']:
        file_type = 'HDF-5'
    elif file_extension in ['.nc', '.nc4']:
        file_type = 'netCDF4'
    else:
        raise ValueError(f'File extension not recognised: "{file_extension}"')

    return file_type


def matches_reference_hash_file_using_xarray(
    binary_file_path: str,
    reference_file_path: str,
    skipped_variables_or_groups: set[str] = set(),
    skipped_metadata_attributes: set[str] = set(),
    xarray_kwargs: dict = XARRAY_DECODE_DEFAULTS,
) -> bool:
    """Generate hashes for request output and compare to reference file.

    Args:
        binary_file_path: netCDF4 or HDF5 file, e.g., retrieved from a Harmony
            request.
        reference_file_path: File containing generated SHA256 values for every
            group and variable in a previously hashed file.
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
        binary_file_path,
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


def geotiff_matches_reference_hash_file(
    geotiff_file_path: str,
    reference_file_path: str,
    skipped_metadata_tags: set[str] = set(),
) -> bool:
    """Generate hash for GeoTIFF file and compare to reference file.

    Args:
        geotiff_file_path: GeoTIFF file to compared against reference file.
        reference_file_path: File containing generated SHA256 value in a
            previously hashed file.
        skipped_metadata_tags: Names of GeoTIFF metadata tags to omit from the
            derivation of the SHA256 hash for the input GeoTIFF file. These
            will be values that are known to vary. The main use-case is
            metadata tags with timestamps dependent on request execution time.

    """
    actual_hash = get_hash_from_geotiff_file(
        geotiff_file_path,
        skipped_metadata_tags,
    )

    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_hash = json.load(file_handler)

    return actual_hash[GEOTIFF_HASH_KEY] == reference_hash[GEOTIFF_HASH_KEY]
