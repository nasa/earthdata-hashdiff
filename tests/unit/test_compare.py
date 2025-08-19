"""Unit tests for the earthdata_hashdiff.compare.py module."""

from os.path import join as path_join

import numpy as np
from tifffile import imwrite

from earthdata_hashdiff.compare import (
    geotiff_matches_reference_hash_file,
    h5_matches_reference_hash_file,
    matches_reference_hash_file_using_xarray,
    nc4_matches_reference_hash_file,
)


def test_matches_reference_hash_file_using_xarray(sample_nc4_file, sample_hash_file):
    """Generate a hashes reference file and ensure it matches expected output."""
    assert matches_reference_hash_file_using_xarray(sample_nc4_file, sample_hash_file)


def test_matches_reference_hash_file_skip_variable(
    sample_datatree, tmpdir, sample_hash_file
):
    """Ensure a specified variable is ignored in comparison.

    One of the variables in the sample xarray.DataTree fixture will be updated
    such that it should fail validation. Then the comparison function will be
    told to ignore that variable during the comparison.

    """
    amended_datatree_path = path_join(tmpdir, 'amended_datatree.nc4')
    sample_datatree['/group_one/science_variable'].attrs['extra attribute'] = 'EXTRA!'
    sample_datatree.to_netcdf(amended_datatree_path)

    assert matches_reference_hash_file_using_xarray(
        amended_datatree_path,
        sample_hash_file,
        skipped_variables_or_groups={'/group_one/science_variable'},
    )


def test_matches_reference_hash_file_updated_variable_asserts_false(
    sample_datatree, tmpdir, sample_hash_file
):
    """Ensure that when a variable is changed, comparisons return False.

    This test shows that an amended, but non-skipped, variable will be detected
    as different by the comparison functions, because the variable itself
    resolves to a different hash value.

    """
    amended_datatree_path = path_join(tmpdir, 'amended_datatree.nc4')
    sample_datatree['/group_one/science_variable'].attrs['extra attribute'] = 'EXTRA!'
    sample_datatree.to_netcdf(amended_datatree_path)

    assert not matches_reference_hash_file_using_xarray(
        amended_datatree_path,
        sample_hash_file,
    )


def test_matches_reference_hash_file_skip_metadata(
    sample_datatree, tmpdir, sample_hash_file
):
    """Ensure a specified metadata attribute is ignored in comparison."""
    amended_datatree_path = path_join(tmpdir, 'amended_datatree.nc4')
    sample_datatree['/group_one'].attrs['IGNORE_ME'] = 'Bad metadata!'
    sample_datatree.to_netcdf(amended_datatree_path)

    assert matches_reference_hash_file_using_xarray(
        amended_datatree_path,
        sample_hash_file,
        skipped_metadata_attributes={'IGNORE_ME'},
    )


def test_matches_reference_hash_file_updated_metadata_asserts_false(
    sample_datatree, tmpdir, sample_hash_file
):
    """Ensure that when a metadata attribute is changed, comparison is False.

    This test shows that an amended, but non-skipped, metadata attribute on a
    group will be detected as different by the comparison functions, because
    the group itself resolves to a different hash value.

    """
    amended_datatree_path = path_join(tmpdir, 'amended_datatree.nc4')
    sample_datatree['/group_one'].attrs['DONT_IGNORE_ME'] = 'Different metadata!'
    sample_datatree.to_netcdf(amended_datatree_path)

    assert not matches_reference_hash_file_using_xarray(
        amended_datatree_path,
        sample_hash_file,
    )


def test_nc4_matches_reference_hash_file(sample_nc4_file, sample_hash_file):
    """Ensure netCDF4 specific alias for the public API works as expected."""
    assert nc4_matches_reference_hash_file(sample_nc4_file, sample_hash_file)


def test_h5_matches_reference_hash_file(sample_h5_file, sample_hash_file):
    """Ensure HDF-5 specific alias for the public API works as expected."""
    assert h5_matches_reference_hash_file(sample_h5_file, sample_hash_file)


def test_geotiff_matches_reference_hash_file(
    sample_geotiff_file, sample_geotiff_hash_file
):
    """Ensure GeoTIFF generates hashes matching the expected reference value."""
    assert geotiff_matches_reference_hash_file(
        sample_geotiff_file, sample_geotiff_hash_file
    )


def test_geotiff_matches_reference_hash_file_data_difference_fails(
    sample_geotiff_tags, tmpdir, sample_geotiff_hash_file
):
    """Ensure GeoTIFF comparison fails when an array element is different."""
    amended_geotiff_path = path_join(tmpdir, 'amended_metadata.tif')

    imwrite(
        amended_geotiff_path,
        np.array([[1, 2], [3, 5]]),
        extratags=sample_geotiff_tags,
    )

    assert not geotiff_matches_reference_hash_file(
        amended_geotiff_path,
        sample_geotiff_hash_file,
    )


def test_geotiff_matches_reference_hash_file_metadata_difference_fails(
    sample_geotiff_tags, tmpdir, sample_geotiff_hash_file
):
    """Ensure GeoTIFF comparison fails when a metadata attribute is different."""
    amended_geotiff_path = path_join(tmpdir, 'amended_metadata.tif')
    sample_geotiff_tags[1] = (33550, 12, 3, (18000, 18000, 0.0), True)

    imwrite(
        amended_geotiff_path,
        np.array([[1, 2], [3, 4]]),
        extratags=sample_geotiff_tags,
    )

    assert not geotiff_matches_reference_hash_file(
        amended_geotiff_path,
        sample_geotiff_hash_file,
    )
