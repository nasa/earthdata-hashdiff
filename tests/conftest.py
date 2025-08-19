import json
from os.path import join as path_join

import numpy as np
import xarray as xr
from pytest import fixture
from tifffile import imwrite


def is_json_serialisable(input_object) -> bool:
    """Return if object can be serialised to a JSON object."""
    try:
        json.dumps(input_object)
        return True
    except (TypeError, OverflowError):
        return False


@fixture(scope='function')
def latitude_metadata():
    """Sample metadata dictionary."""
    return {
        'standard_name': 'latitude',
        'units': 'degrees_north',
    }


@fixture()
def latitude_metadata_bytes():
    """Bytes value of latitude metadata dictionary."""
    return b'{"standard_name": "latitude", "units": "degrees_north"}'


@fixture()
def group_one_hashes():
    """Hashed values for group_one in sample_datatree."""
    return {
        '/group_one': (
            '5f54ee382e9afdb41c15107d46cb10e3011fa12fd02f1890b91d2b0d7a729bea'
        ),
        '/group_one/science_variable': (
            'b0777a5ad3b5763b7c0170f2e21dfd7ceb37f9e974275e97b70d0e72140bf809'
        ),
        '/group_one/transpose_variable': (
            'c085b0a064fa61b9ffef1cd638c0f6ed65f93095f17d79661b8cbf8e6e8a808a'
        ),
        '/group_one/different_attributes_variable': (
            'b37c8755cf6f2b4ceae42c4c0ff158920278a8d48c7d654df24b6b2fbe86b595'
        ),
        '/group_one/different_element_variable': (
            'b6decc7257988c18958811fbb09269f4f2aeee5f8aa43cdb000de24d850e096d'
        ),
        '/group_one/identical_variable': (
            'b0777a5ad3b5763b7c0170f2e21dfd7ceb37f9e974275e97b70d0e72140bf809'
        ),
        '/group_one/lat': (
            'da9f1b6a68e46c8a4f0c19efdb136e70cfdcb84b38668a9cad36766ab6137d6d'
        ),
        '/group_one/lon': (
            'b1a2d2ef250d759a33bf3948ca1c5c6dbe63c875f7e13bad3b4c611f7521661b'
        ),
    }


@fixture
def group_two_hashes():
    """Hashed values for group_two in sample_datatree."""
    return {
        '/group_two': (
            '5f54ee382e9afdb41c15107d46cb10e3011fa12fd02f1890b91d2b0d7a729bea'
        ),
        '/group_two/science_variable': (
            'b0777a5ad3b5763b7c0170f2e21dfd7ceb37f9e974275e97b70d0e72140bf809'
        ),
        '/group_two/lon': (
            'b1a2d2ef250d759a33bf3948ca1c5c6dbe63c875f7e13bad3b4c611f7521661b'
        ),
        '/group_two/lat': (
            'da9f1b6a68e46c8a4f0c19efdb136e70cfdcb84b38668a9cad36766ab6137d6d'
        ),
    }


@fixture()
def sample_datatree_hashes(group_one_hashes, group_two_hashes):
    """Hashed values for all of sample_datatree."""
    return {
        '/': '7b7a2f342b4a9bebe67c025f7e5efa95710ae31bd98cbe7c1728ffeaad3ff742',
        **group_one_hashes,
        **group_two_hashes,
    }


@fixture()
def sample_hash_file(tmpdir, sample_datatree_hashes):
    """Output JSON file containing reference hashes."""
    hash_file_path = path_join(tmpdir, 'hashed_reference_file.json')

    with open(hash_file_path, 'w', encoding='utf-8') as file_handler:
        json.dump(sample_datatree_hashes, file_handler, indent=2)

    return hash_file_path


@fixture(scope='function')
def sample_datatree():
    """xarray.DataTree object to be used for tests."""
    longitude_data = np.array([10, 15, 20])
    latitude_data = np.array([25, 30])

    variable_data = np.array([[1, 2, 3], [4, 5, 6]])
    transpose_variable_data = np.array([[1, 4], [2, 5], [3, 6]])
    alternative_variable_data = np.array([[1, 2, 3], [4, 5, 7]])

    variable_attributes = {'unit': 'amazing science unit'}
    alternative_variable_attributes = {'unit': 'different science unit'}

    sample_datatree = xr.DataTree()

    # Create a group with:
    # - A science variable
    # - A science variable that is the transpose of the first
    # - A science variable that has different attribute values to the first
    # - A science variable that has a different array element to the first
    # - A science variable that is identical to the first
    sample_datatree['/group_one'] = xr.Dataset(
        {
            'science_variable': (
                ('lat', 'lon'),
                variable_data,
                variable_attributes,
            ),
            'transpose_variable': (
                ('lon', 'lat'),
                transpose_variable_data,
                variable_attributes,
            ),
            'different_attributes_variable': (
                ('lat', 'lon'),
                variable_data,
                alternative_variable_attributes,
            ),
            'different_element_variable': (
                ('lat', 'lon'),
                alternative_variable_data,
                variable_attributes,
            ),
            'identical_variable': (
                ('lat', 'lon'),
                variable_data,
                variable_attributes,
            ),
        },
        coords={
            'lat': latitude_data,
            'lon': longitude_data,
        },
        attrs={'group_attributes': 'attribute_value'},
    )

    # Create a group with the same dimensions as the first, but in the
    # opposite order.
    sample_datatree['/group_two'] = xr.Dataset(
        {
            'science_variable': (
                ('lat', 'lon'),
                variable_data,
                variable_attributes,
            ),
        },
        coords={
            'lon': longitude_data,
            'lat': latitude_data,
        },
        attrs={'group_attributes': 'attribute_value'},
    )

    return sample_datatree


@fixture(scope='function')
def sample_h5_file(sample_datatree, tmpdir):
    """xarray.DataTree object written out to disk as HDF-5 for testing.

    Strictly speaking, the output is using `xarray.DataTree.to_netcdf`.

    """
    sample_file_path = path_join(tmpdir, 'sample_file.h5')
    sample_datatree.to_netcdf(sample_file_path)
    return sample_file_path


@fixture(scope='function')
def sample_nc4_file(sample_datatree, tmpdir):
    """xarray.DataTree object written out to disk as netCDF4 for testing."""
    sample_file_path = path_join(tmpdir, 'sample_file.nc4')
    sample_datatree.to_netcdf(sample_file_path)
    return sample_file_path


@fixture(scope='function')
def sample_geotiff_tags():
    """Tags for the sample GeoTIFF file."""
    return [
        (
            34735,
            3,
            32,
            (
                1,
                1,
                0,
                7,
                1024,
                0,
                1,
                1,
                1025,
                0,
                1,
                1,
                1026,
                34737,
                36,
                0,
                2049,
                34737,
                7,
                36,
                2054,
                0,
                1,
                9102,
                3072,
                0,
                1,
                6933,
                3076,
                0,
                1,
                9001,
            ),
            True,
        ),
        (33550, 12, 3, (36032.22084058401, 36032.220840584, 0.0), True),
        (33922, 12, 6, (0.0, 0.0, 0.0, -17367530.4451615, 7314540.8306386, 0.0), True),
        (34737, 2, 44, 'WGS 84 / NSIDC EASE-Grid 2.0 Global|WGS 84|', True),
        (
            42112,
            2,
            845,
            (
                '<GDALMetadata>\n'
                '  <Item name="long_name">The fraction of the grid cell that '
                '  contains the most common land cover in that area based on '
                '  the IGBP landcover map.</Item>\n'
                '  <Item name="OVR_RESAMPLING_ALG">NEAREST</Item>'
                '  <Item name="valid_max">1.0</Item>'
                '  <Item name="valid_min">0.0</Item>'
                '  <Item name="DESCRIPTION" sample="0" role="description">'
                '  The fraction of the grid cell that contains the most '
                '  common land cover in that area based on the IGBP '
                '  landcover map.</Item>'
                '  <Item name="DESCRIPTION" sample="1" role="description">'
                '  The fraction of the grid cell that contains the most '
                '  common land cover in that area based on the IGBP '
                '  landcover map.</Item>'
                '  <Item name="DESCRIPTION" sample="2" role="description">'
                '  The fraction of the grid cell that contains the most '
                '  common land cover in that area based on the IGBP '
                '  landcover map.</Item>'
                '</GDALMetadata>'
            ),
            True,
        ),
        (42113, 2, 6, '-9999', True),
    ]


@fixture(scope='function')
def sample_geotiff_file(tmpdir, sample_geotiff_tags):
    """GeoTIFF object written out to disk.

    Values copied from a PREFIRE GeoTIFF.

    """
    geotiff_path = path_join(tmpdir, 'sample_file.tif')
    imwrite(
        geotiff_path,
        np.array([[1, 2], [3, 4]]),
        extratags=sample_geotiff_tags,
    )
    return geotiff_path


@fixture()
def sample_geotiff_hash():
    """Hashed value for sample GeoTIFF file."""
    return {
        'geotiff_hash': (
            '450c6cdad0419431dc9d2dc80ad374f8627632302ae5fd0b7354aae160ff528e'
        )
    }


@fixture()
def sample_geotiff_hash_file(sample_geotiff_hash, tmpdir):
    """Output JSON file containing reference hash for GeoTIFF sample file."""
    hash_file_path = path_join(tmpdir, 'hashed_reference_file.json')

    with open(hash_file_path, 'w', encoding='utf-8') as file_handler:
        json.dump(sample_geotiff_hash, file_handler, indent=2)

    return hash_file_path
