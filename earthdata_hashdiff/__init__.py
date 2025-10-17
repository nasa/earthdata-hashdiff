"""Public API for earthdata-hashdiff."""

from earthdata_hashdiff.__about__ import version
from earthdata_hashdiff.compare import (
    geotiff_matches_reference_hash_file,
    h5_matches_reference_hash_file,
    matches_reference_hash_file,
    nc4_matches_reference_hash_file,
)
from earthdata_hashdiff.generate import (
    create_geotiff_hash_file,
    create_h5_hash_file,
    create_nc4_hash_file,
    get_hash_from_geotiff_file,
    get_hashes_from_h5_file,
    get_hashes_from_nc4_file,
)

__version__ = version

__all__ = [
    'create_geotiff_hash_file',
    'create_h5_hash_file',
    'create_nc4_hash_file',
    'get_hash_from_geotiff_file',
    'get_hashes_from_h5_file',
    'get_hashes_from_nc4_file',
    'geotiff_matches_reference_hash_file',
    'h5_matches_reference_hash_file',
    'matches_reference_hash_file',
    'nc4_matches_reference_hash_file',
]
