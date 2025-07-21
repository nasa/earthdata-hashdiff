"""Unit tests for the earthdata_hashdiff.compare.py module."""

from os.path import join as path_join

from earthdata_hashdiff.compare import (
    h5_matches_reference_hash_file,
    matches_reference_hash_file_using_xarray,
    nc4_matches_reference_hash_file,
)


def test_matches_reference_hash_file_using_xarray(sample_nc4_file, sample_hash_file):
    """Generate a hashes reference file and ensure it matches expected output."""
    assert matches_reference_hash_file_using_xarray(sample_nc4_file, sample_hash_file)


def test_matches_reference_hash_file_skip_variable(
    sample_datatree, temp_dir, sample_hash_file
):
    """Ensure a specified variable is ignored in comparison.

    One of the variables in the sample xarray.DataTree fixture will be updated
    such that it should fail validation. Then the comparison function will be
    told to ignore that variable during the comparison.

    """
    amended_datatree_path = path_join(temp_dir, 'amended_datatree.nc4')
    sample_datatree['/group_one/science_variable'].attrs['extra attribute'] = 'EXTRA!'
    sample_datatree.to_netcdf(amended_datatree_path)

    assert matches_reference_hash_file_using_xarray(
        amended_datatree_path,
        sample_hash_file,
        skipped_variables_or_groups={'/group_one/science_variable'},
    )


def test_matches_reference_hash_file_skip_metadata(
    sample_datatree, temp_dir, sample_hash_file
):
    """Ensure a specified metadata attribute is ignored in comparison."""
    amended_datatree_path = path_join(temp_dir, 'amended_datatree.nc4')
    sample_datatree['/group_one'].attrs['IGNORE_ME'] = 'Bad metadata!'
    sample_datatree.to_netcdf(amended_datatree_path)

    assert matches_reference_hash_file_using_xarray(
        amended_datatree_path,
        sample_hash_file,
        skipped_metadata_attributes={'IGNORE_ME'},
    )


def test_nc4_matches_reference_hash_file(sample_nc4_file, sample_hash_file):
    """Ensure netCDF4 specific alias for the public API works as expected."""
    assert nc4_matches_reference_hash_file(sample_nc4_file, sample_hash_file)


def test_h5_matches_reference_hash_file(sample_h5_file, sample_hash_file):
    """Ensure HDF-5 specific alias for the public API works as expected."""
    assert h5_matches_reference_hash_file(sample_h5_file, sample_hash_file)
