"""Tests for deterministic cleanup of the datasets opened for hashing."""

import json
from pathlib import Path

import pytest

from earthdata_hashdiff import generate
from earthdata_hashdiff.compare import matches_reference_hash_file_using_xarray


def observe_groups(monkeypatch):
    """Track real backend close callbacks without replacing file reads."""
    open_groups = generate.xr.open_groups
    groups = {}
    closed = []

    def open_and_observe(*args, **kwargs):
        result = open_groups(*args, **kwargs)
        groups.update(result)
        for name, dataset in result.items():
            close_backend = dataset._close

            def close(name=name, close_backend=close_backend):
                closed.append(name)
                close_backend()

            dataset.set_close(close)
        return result

    monkeypatch.setattr(generate.xr, 'open_groups', open_and_observe)
    return groups, closed


@pytest.mark.parametrize('operation', ['hash', 'reference', 'compare'])
def test_all_groups_close_after_success(
    monkeypatch, tmp_path, sample_nc4_file, sample_datatree_hashes, operation
):
    """The public hash, reference and comparison paths release every group."""
    original_bytes = Path(sample_nc4_file).read_bytes()
    groups, closed = observe_groups(monkeypatch)
    reference = tmp_path / 'reference.json'
    if operation == 'hash':
        assert (
            generate.get_hashes_from_xarray_input(sample_nc4_file)
            == sample_datatree_hashes
        )
    elif operation == 'reference':
        generate.create_xarray_reference_file(sample_nc4_file, str(reference))
        assert json.loads(reference.read_text()) == sample_datatree_hashes
    else:
        reference.write_text(json.dumps(sample_datatree_hashes))
        assert matches_reference_hash_file_using_xarray(sample_nc4_file, str(reference))

    assert len(groups) > 1
    assert sorted(closed) == sorted(groups)
    assert all(dataset._close is None for dataset in groups.values())
    assert Path(sample_nc4_file).read_bytes() == original_bytes


@pytest.mark.parametrize('failure_index', [0, 1, -1])
def test_hash_failure_closes_processed_and_unprocessed_groups(
    monkeypatch, sample_nc4_file, failure_index
):
    """A failed hash also releases groups that were not yet visited."""
    groups, closed = observe_groups(monkeypatch)
    original_hash = generate.get_hash_of_xarray_dataset
    error = ValueError('metadata cannot be serialized')
    visited = []

    def fail_during_hash(name, *args):
        # Backends must remain open until their lazy data has been hashed.
        assert not closed
        visited.append(name)
        if name == list(groups)[failure_index]:
            raise error
        return original_hash(name, *args)

    monkeypatch.setattr(generate, 'get_hash_of_xarray_dataset', fail_during_hash)
    with pytest.raises(ValueError) as raised:
        generate.get_hashes_from_xarray_input(sample_nc4_file)
    assert raised.value is error
    assert visited
    assert sorted(closed) == sorted(groups)
    assert all(dataset._close is None for dataset in groups.values())


def test_failure_before_hashing_does_not_write_a_reference(
    monkeypatch, tmp_path, sample_nc4_file
):
    """Cleanup must not turn a failed reference generation into partial output."""
    groups, closed = observe_groups(monkeypatch)
    output = tmp_path / 'existing.json'
    output.write_text('previous reference')

    def fail(*_args):
        raise TypeError('unsupported metadata')

    monkeypatch.setattr(generate, 'get_hash_of_xarray_dataset', fail)
    with pytest.raises(TypeError, match='unsupported metadata'):
        generate.create_xarray_reference_file(sample_nc4_file, str(output))
    assert output.read_text() == 'previous reference'
    assert sorted(closed) == sorted(groups)


def test_repeated_reads_release_each_set_of_groups(
    monkeypatch, sample_nc4_file, sample_datatree_hashes
):
    """Repeated comparisons should not depend on garbage collection for cleanup."""
    groups, closed = observe_groups(monkeypatch)
    for attempt in range(4):
        assert (
            generate.get_hashes_from_xarray_input(sample_nc4_file)
            == sample_datatree_hashes
        )
        assert len(closed) == (attempt + 1) * len(groups)


def test_open_failure_propagates_without_attempting_to_hash(monkeypatch):
    """Preserve the original open error when no group objects are returned."""
    error = OSError('unable to open input')

    def fail(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(generate.xr, 'open_groups', fail)
    with pytest.raises(OSError) as raised:
        generate.get_hashes_from_xarray_input('missing.nc4')
    assert raised.value is error
