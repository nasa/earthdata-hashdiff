"""Unit tests for the earthdata_hashdiff public API.

These tests duplicate unit tests for the individual modules that the functions
are derived from, but demonstrate the imports and re-exports work as
anticipated.

"""

import json
from os.path import join as path_join

from earthdata_hashdiff import (
    create_geotiff_hash_file,
    create_h5_hash_file,
    create_nc4_hash_file,
    geotiff_matches_reference_hash_file,
    get_hash_from_geotiff_file,
    get_hashes_from_h5_file,
    get_hashes_from_nc4_file,
    h5_matches_reference_hash_file,
    nc4_matches_reference_hash_file,
)


def test_create_geotiff_hash_file(tmpdir, sample_geotiff_file, sample_geotiff_hash):
    """Test GeoTIFF public function for creating hash file."""
    reference_file_path = path_join(tmpdir, 'sample_output.json')
    create_geotiff_hash_file(sample_geotiff_file, reference_file_path)

    # Ensure output hash file exists and matches test fixtures:
    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_file_json = json.load(file_handler)

    assert reference_file_json == sample_geotiff_hash


def test_create_h5_hash_file(tmpdir, sample_h5_file, sample_datatree_hashes):
    """Test HDF-5 alias for creating hash files using xarray."""
    reference_file_path = path_join(tmpdir, 'sample_output.json')
    create_h5_hash_file(sample_h5_file, reference_file_path, {})

    # Ensure output hash file exists and matches test fixtures:
    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_file_json = json.load(file_handler)

    assert reference_file_json == sample_datatree_hashes


def test_create_nc4_hash_file(tmpdir, sample_nc4_file, sample_datatree_hashes):
    """Test netCDF4 alias for creating hash files using xarray."""
    reference_file_path = path_join(tmpdir, 'sample_output.json')
    create_nc4_hash_file(sample_nc4_file, reference_file_path, {})

    # Ensure output hash file exists and matches test fixtures:
    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_file_json = json.load(file_handler)

    assert reference_file_json == sample_datatree_hashes


def test_get_hash_from_geotiff_file(sample_geotiff_file, sample_geotiff_hash):
    """Ensure GeoTIFF function from public API produces correct JSON output."""
    actual_hash = get_hash_from_geotiff_file(sample_geotiff_file, set())
    assert actual_hash == sample_geotiff_hash


def test_get_hash_from_h5_file(sample_h5_file, sample_datatree_hashes):
    """Ensure HDF-5 function from public API produces correct JSON output."""
    actual_hashes = get_hashes_from_h5_file(sample_h5_file)
    assert actual_hashes == sample_datatree_hashes


def test_get_hash_from_nc4_file(sample_nc4_file, sample_datatree_hashes):
    """Ensure netCDF4 function from public API produces correct JSON output."""
    actual_hashes = get_hashes_from_nc4_file(sample_nc4_file)
    assert actual_hashes == sample_datatree_hashes


def test_geotiff_matches_reference_hash_file(
    sample_geotiff_file, sample_geotiff_hash_file
):
    """Ensure GeoTIFF specific function for the public API works as expected."""
    assert geotiff_matches_reference_hash_file(
        sample_geotiff_file,
        sample_geotiff_hash_file,
    )


def test_nc4_matches_reference_hash_file(sample_nc4_file, sample_hash_file):
    """Ensure netCDF4 specific alias for the public API works as expected."""
    assert nc4_matches_reference_hash_file(sample_nc4_file, sample_hash_file)


def test_h5_matches_reference_hash_file(sample_h5_file, sample_hash_file):
    """Ensure HDF-5 specific alias for the public API works as expected."""
    assert h5_matches_reference_hash_file(sample_h5_file, sample_hash_file)
