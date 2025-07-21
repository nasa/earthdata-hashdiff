"""Public API for earthdata-hashdiff."""

from earthdata_hashdiff.__about__ import version
from earthdata_hashdiff.compare import (
    h5_matches_reference_hash_file,
    nc4_matches_reference_hash_file,
)
from earthdata_hashdiff.generate import (
    create_h5_hash_file,
    create_nc4_hash_file,
)

__version__ = version

__all__ = [
    'create_h5_hash_file',
    'create_nc4_hash_file',
    'h5_matches_reference_hash_file',
    'nc4_matches_reference_hash_file',
]
