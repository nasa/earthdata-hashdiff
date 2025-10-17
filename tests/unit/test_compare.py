"""Unit tests for the earthdata_hashdiff.compare.py module."""

from os.path import join as path_join
from unittest.mock import patch

import numpy as np
import pytest
from tifffile import imwrite

from earthdata_hashdiff.compare import (
    geotiff_matches_reference_hash_file,
    guess_file_type,
    h5_matches_reference_hash_file,
    matches_reference_hash_file,
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


@pytest.mark.parametrize(
    'file_path,expected_file_type',
    [
        ('input.tif', 'GeoTIFF'),
        ('input.tiff', 'GeoTIFF'),
        ('input.h5', 'HDF-5'),
        ('input.hdf', 'HDF-5'),
        ('input.HDF', 'HDF-5'),
        ('input.hdf5', 'HDF-5'),
        ('input.nc', 'netCDF4'),
        ('input.nc4', 'netCDF4'),
    ],
)
def test_guess_file_type_known_extension(file_path, expected_file_type):
    """Ensure known paths with known extensions return the expected file type."""
    assert guess_file_type(file_path) == expected_file_type


def test_guess_file_type_not_recognised():
    """Ensure path with unknown extension raises a ValueError."""
    with pytest.raises(ValueError, match=r'File extension not recognised: ".xyz"'):
        guess_file_type('input.xyz')


@patch('earthdata_hashdiff.compare.geotiff_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.h5_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.nc4_matches_reference_hash_file', autospec=True)
def test_matches_reference_hash_file_netcdf4(
    mock_nc4_matches_reference_hash_file,
    mock_h5_matches_reference_hash_file,
    mock_geotiff_matches_reference_hash_file,
):
    """Ensure netCDF4 input is routed to the correct comparison function."""
    mock_nc4_matches_reference_hash_file.return_value = True

    assert matches_reference_hash_file('input.nc4', 'hashes.json')
    mock_nc4_matches_reference_hash_file.assert_called_once_with(
        'input.nc4',
        'hashes.json',
    )

    # Ensure other comparison functions weren't called
    mock_h5_matches_reference_hash_file.assert_not_called()
    mock_geotiff_matches_reference_hash_file.assert_not_called()


@patch('earthdata_hashdiff.compare.geotiff_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.h5_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.nc4_matches_reference_hash_file', autospec=True)
def test_matches_reference_hash_file_netcdf4_kwargs(
    mock_nc4_matches_reference_hash_file,
    mock_h5_matches_reference_hash_file,
    mock_geotiff_matches_reference_hash_file,
):
    """Ensure netCDF4 input is routed to the comparison function with kwargs."""
    mock_nc4_matches_reference_hash_file.return_value = True

    variables_to_skip = {'variable_one', 'variable_two'}

    assert matches_reference_hash_file(
        'input.nc4',
        'hashes.json',
        skipped_variables_or_groups=variables_to_skip,
    )
    mock_nc4_matches_reference_hash_file.assert_called_once_with(
        'input.nc4',
        'hashes.json',
        skipped_variables_or_groups=variables_to_skip,
    )

    # Ensure other comparison functions weren't called
    mock_h5_matches_reference_hash_file.assert_not_called()
    mock_geotiff_matches_reference_hash_file.assert_not_called()


@patch('earthdata_hashdiff.compare.geotiff_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.h5_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.nc4_matches_reference_hash_file', autospec=True)
def test_matches_reference_hash_file_hdf5(
    mock_nc4_matches_reference_hash_file,
    mock_h5_matches_reference_hash_file,
    mock_geotiff_matches_reference_hash_file,
):
    """Ensure an HDF-5 input is routed to the correct comparison function."""
    mock_h5_matches_reference_hash_file.return_value = True

    metadata_to_skip = {'varying_parameter'}

    assert matches_reference_hash_file(
        'input.h5',
        'hashes.json',
        skipped_metadata_attributes=metadata_to_skip,
    )
    mock_h5_matches_reference_hash_file.assert_called_once_with(
        'input.h5',
        'hashes.json',
        skipped_metadata_attributes=metadata_to_skip,
    )

    # Ensure other comparison functions weren't called
    mock_nc4_matches_reference_hash_file.assert_not_called()
    mock_geotiff_matches_reference_hash_file.assert_not_called()


@patch('earthdata_hashdiff.compare.geotiff_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.h5_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.nc4_matches_reference_hash_file', autospec=True)
def test_matches_reference_hash_file_geotiff(
    mock_nc4_matches_reference_hash_file,
    mock_h5_matches_reference_hash_file,
    mock_geotiff_matches_reference_hash_file,
):
    """Ensure a GeoTIFF input is routed to the correct comparison function."""
    mock_geotiff_matches_reference_hash_file.return_value = True

    assert matches_reference_hash_file('input.tiff', 'hashes.json')

    mock_geotiff_matches_reference_hash_file.assert_called_once_with(
        'input.tiff',
        'hashes.json',
    )

    # Ensure other comparison functions weren't called
    mock_nc4_matches_reference_hash_file.assert_not_called()
    mock_h5_matches_reference_hash_file.assert_not_called()


def test_matches_reference_hash_file_unknown_kwargs():
    """Ensure input with an unknown kwarg raises a TypeError."""
    with pytest.raises(
        TypeError, match=r'got an unexpected keyword argument \'unknown_kwarg\''
    ):
        matches_reference_hash_file(
            'input.nc4',
            'hashes.json',
            unknown_kwarg='whatami',
        )


def test_matches_reference_hash_file_wrong_kwargs():
    """Ensure netCDF4 input with a GeoTIFF kwarg raises a TypeError.

    This test ensures that, even though the function signature is overloaded,
    mixing kwargs from one comparison when trying to execute another will fail.

    """
    with pytest.raises(
        TypeError, match=r'got an unexpected keyword argument \'skipped_metadata_tags\''
    ):
        matches_reference_hash_file(
            'input.nc4',
            'hashes.json',
            skipped_metadata_tags={'skipped'},
        )


@patch('earthdata_hashdiff.compare.geotiff_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.h5_matches_reference_hash_file', autospec=True)
@patch('earthdata_hashdiff.compare.nc4_matches_reference_hash_file', autospec=True)
def test_matches_reference_hash_file_unknown_file_extension(
    mock_nc4_matches_reference_hash_file,
    mock_h5_matches_reference_hash_file,
    mock_geotiff_matches_reference_hash_file,
):
    """Ensure that a file with an unknown extension raises a ValueError."""
    with pytest.raises(ValueError, match=r'File extension not recognised: ".xyz"'):
        matches_reference_hash_file('input.xyz', 'hashes.json')

    # Ensure other comparison functions weren't called
    mock_nc4_matches_reference_hash_file.assert_not_called()
    mock_h5_matches_reference_hash_file.assert_not_called()
    mock_geotiff_matches_reference_hash_file.assert_not_called()
