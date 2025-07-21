"""Unit tests for the earthdata_hashdiff.generate.py module."""

import json
from datetime import datetime
from os.path import join as path_join

import numpy as np
import pytest

from earthdata_hashdiff.generate import (
    create_h5_hash_file,
    create_nc4_hash_file,
    create_xarray_reference_file,
    get_full_variable_path,
    get_group_dimensions_bytes,
    get_hash_of_xarray_dataset,
    get_hash_value,
    get_hashes_from_xarray_input,
    get_metadata_bytes,
    get_numpy_array_bytes,
    get_variable_dimensions_bytes,
    get_xarray_object_hash,
    is_varying_attribute,
    serialise_metadata_value,
)
from tests.conftest import is_json_serialisable


def test_create_xarray_reference_file(
    temp_dir, sample_nc4_file, sample_datatree_hashes
):
    """Check a reference file of hashes is created as expected.

    This implicitly tests the write_reference_file helper function, that only
    dumps a dictionary out to a JSON file.

    """
    reference_file_path = path_join(temp_dir, 'sample_output.json')
    create_xarray_reference_file(sample_nc4_file, reference_file_path, {})

    # Ensure output hash file exists and matches test fixtures:
    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_file_json = json.load(file_handler)

    assert reference_file_json == sample_datatree_hashes


def test_create_h5_hash_file(temp_dir, sample_h5_file, sample_datatree_hashes):
    """Test HDF-5 alias for creating hash files using xarray."""
    reference_file_path = path_join(temp_dir, 'sample_output.json')
    create_h5_hash_file(sample_h5_file, reference_file_path, {})

    # Ensure output hash file exists and matches test fixtures:
    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_file_json = json.load(file_handler)

    assert reference_file_json == sample_datatree_hashes


def test_create_nc4_hash_file(temp_dir, sample_nc4_file, sample_datatree_hashes):
    """Test netCDF4 alias for creating hash files using xarray."""
    reference_file_path = path_join(temp_dir, 'sample_output.json')
    create_nc4_hash_file(sample_nc4_file, reference_file_path, {})

    # Ensure output hash file exists and matches test fixtures:
    with open(reference_file_path, encoding='utf-8') as file_handler:
        reference_file_json = json.load(file_handler)

    assert reference_file_json == sample_datatree_hashes


def test_get_hashes_from_xarray_input(sample_nc4_file, sample_datatree_hashes):
    """Get full hash output for an input that can be parsed with xarray."""
    assert get_hashes_from_xarray_input(sample_nc4_file, {}) == sample_datatree_hashes


def test_get_hash_of_xarray_dataset(sample_datatree, group_one_hashes):
    """Get SHA256 for full xarray.Dataset (group, and all contained variables)."""
    assert (
        get_hash_of_xarray_dataset('/group_one', sample_datatree['/group_one'].ds, {})
        == group_one_hashes
    )


def test_get_xarray_object_hash_variable(sample_datatree, sample_datatree_hashes):
    """Derive SHA256 hash for variable in an xarray.DataTree."""
    assert (
        get_xarray_object_hash(sample_datatree['/group_one/science_variable'], {})
        == sample_datatree_hashes['/group_one/science_variable']
    )


def test_get_xarray_object_hash_group(sample_datatree, sample_datatree_hashes):
    """Derive SHA256 hash for group in an xarray.DataTree.

    Note - file objects are opened by earthdata-hashdiff using `xarray.open_groups`.
    This creates a dictionary with values that are `xarray.Dataset` instances,
    rather than `xarray.DataTree` instances.

    """
    assert (
        get_xarray_object_hash(sample_datatree['/group_one'].ds, {})
        == sample_datatree_hashes['/group_one']
    )


def test_get_xarray_object_hash_skipped_attributes(sample_datatree):
    """Show that skipped_metadata_attributes are ignored in the hash derivation.

    This test is coupled with `test_get_xarray_object_hash_group` as it is
    important to note that the two hashes are different.

    """
    assert (
        get_xarray_object_hash(sample_datatree['/group_one'].ds, {'group_attributes'})
        == 'e464bed8253d2029ff985060ff27963809ed960b8642c3de26ae369a4037f4ed'
    )


@pytest.mark.parametrize(
    'metadata_bytes,dimension_bytes,array_bytes,expected_output',
    [
        (
            b'metadata bytes',
            b"('lat')",
            b'(2,)\x01',
            '751ba3f1634005736d44ec01e14e8a2a9254e87d873d46e9a23d05f15cec8fe8',
        ),
        (
            b'other metadata bytes',
            b"('lat')",
            b'(2,)\x01',
            'd1fbe3bc512dc63e881c62d843dfccbb445b3e5376fc2ca8b442139969fb9404',
        ),
        (
            b'metadata bytes',
            b"('lon')",
            b'(2,)\x01',
            '0f947b2b7cc1558840c431ebb582cd0bf1f7584aa9db07991d32940f23793065',
        ),
        (
            b'metadata bytes',
            b"('lat')",
            None,
            '8cefa7bc0103fde50c8da8e4a6cbf1819c2d5dd7b3baef79b5314051206416de',
        ),
    ],
)
def test_get_hash_value(metadata_bytes, dimension_bytes, array_bytes, expected_output):
    """Demonstrate the effect of each input parameter in generating a hash value."""
    assert (
        get_hash_value(metadata_bytes, dimension_bytes, array_bytes) == expected_output
    )


@pytest.mark.parametrize(
    'group_path,expected_bytes',
    [
        ('/group_one', b"['lat', 'lon']"),
        ('/group_two', b"['lat', 'lon']"),
    ],
)
def test_get_group_dimensions_bytes(group_path, expected_bytes, sample_datatree):
    """Demonstrate that ordering of dimensions on group objects does not matter.

    - `/group_one` has dimensions of order: (lat, lon)
    - `/group_two` has dimensions of order: (lon, lat)

    `get_group_dimensions_bytes` sorts the dimensions by name before creating
    the bytes string output.

    """
    assert (
        get_group_dimensions_bytes(sample_datatree[group_path].dims) == expected_bytes
    )


@pytest.mark.parametrize(
    'variable_path,expected_bytes',
    [
        ('/group_one/science_variable', b"('lat', 'lon')"),
        ('/group_one/transpose_variable', b"('lon', 'lat')"),
        ('/group_one/lat', b"('lat',)"),
        ('/group_two/lat', b"('lat',)"),
    ],
)
def test_get_variable_dimensions_bytes(variable_path, expected_bytes, sample_datatree):
    """Demonstrate dimensionality, including ordering, matters.

    Specific tests show:

    - Different ordering of the same dimensions is important.
    - The same dimensions in different variables (different groups) gives the
    - same result.

    """
    assert (
        get_variable_dimensions_bytes(sample_datatree[variable_path].dims)
        == expected_bytes
    )


@pytest.mark.parametrize(
    'dataset_path,variable_path,expected_full_path',
    [
        ('/', 'variable', '/variable'),
        ('/group_one', 'variable', '/group_one/variable'),
        ('/group_one/group_two', 'variable', '/group_one/group_two/variable'),
    ],
)
def test_get_full_variable_path(dataset_path, variable_path, expected_full_path):
    """Ensure xarray.Dataset and xarray.Variable paths are combined correctly."""
    assert get_full_variable_path(dataset_path, variable_path) == expected_full_path


@pytest.mark.parametrize(
    'numpy_array,expected_bytes',
    [
        (
            np.array([1, 2]),
            b'(2,)\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00',
        ),
        (
            np.array([[1], [2]]),
            b'(2, 1)\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00',
        ),
        (
            np.array([2, 3]),
            b'(2,)\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00',
        ),
    ],
)
def test_get_numpy_array_bytes(numpy_array, expected_bytes):
    """Ensure numpy array creates expected bytes.

    `get_numpy_array_bytes` accounts for element values and array shape.

    """
    assert get_numpy_array_bytes(numpy_array) == expected_bytes


def test_get_metadata_bytes(latitude_metadata, latitude_metadata_bytes):
    """Ensure dictionary of metadata attributes gives expected bytes out."""
    assert get_metadata_bytes(latitude_metadata, set()) == latitude_metadata_bytes


def test_get_metadata_bytes_history(latitude_metadata, latitude_metadata_bytes):
    """Ensure history metadata attribute is ignored in output metadata bytes."""
    latitude_metadata['history'] = datetime.now().isoformat()
    assert get_metadata_bytes(latitude_metadata, set()) == latitude_metadata_bytes


def test_get_metadata_bytes_skipped(latitude_metadata, latitude_metadata_bytes):
    """Ensure skipped attributes are skipped when deriving metadata bytes."""
    latitude_metadata['to_skip'] = 'some value'
    assert (
        get_metadata_bytes(
            latitude_metadata,
            {
                'to_skip',
            },
        )
        == latitude_metadata_bytes
    )


@pytest.mark.parametrize(
    'attribute_name',
    [
        'history',
        'History',
        'HISTORY',
        'history_json',
        'HISTORY_JSON',
    ],
)
def test_is_varying_attribute_varying(attribute_name):
    """Ensure varying attributes are correctly identified."""
    assert is_varying_attribute(attribute_name)


def test_is_varying_attribute_not_varying():
    """Ensure a non-varying attribute is not incorrectly flagged."""
    assert not is_varying_attribute('non_varying_attribute')


@pytest.mark.parametrize(
    'metadata_value,cleaned_value',
    [
        (np.float64(123), float(123)),
        (np.int32(123), 123),
        (
            np.array([1, 2, 3]),
            '6992517b5759a7588f5f3779cacd94874fab975a3381d98b8c9ffca66f530478',
        ),
        ('string value', 'string value'),
    ],
)
def test_serialise_metadata_value(metadata_value, cleaned_value):
    """Ensure metadata is cast to something that can be serialised."""
    serialised_value = serialise_metadata_value(metadata_value)
    assert serialised_value == cleaned_value
    assert is_json_serialisable({'metadata_key': serialised_value})
