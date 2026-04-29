"""Tests for envdiff.sorter."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiff, group_by_label, merge_groups, sort_keys


@pytest.fixture()
def unsorted_result() -> DiffResult:
    return DiffResult(
        missing_in_target=["ZEBRA", "ALPHA", "MANGO"],
        missing_in_base=["OMEGA", "BETA"],
        mismatched={
            "PORT": {"base": "8080", "target": "9090"},
            "HOST": {"base": "localhost", "target": "0.0.0.0"},
        },
    )


def test_sort_keys_missing_in_target(unsorted_result):
    result = sort_keys(unsorted_result)
    assert result.missing_in_target == ["ALPHA", "MANGO", "ZEBRA"]


def test_sort_keys_missing_in_base(unsorted_result):
    result = sort_keys(unsorted_result)
    assert result.missing_in_base == ["BETA", "OMEGA"]


def test_sort_keys_mismatched(unsorted_result):
    result = sort_keys(unsorted_result)
    assert list(result.mismatched.keys()) == ["HOST", "PORT"]


def test_sort_keys_preserves_values(unsorted_result):
    result = sort_keys(unsorted_result)
    assert result.mismatched["PORT"] == {"base": "8080", "target": "9090"}


def test_group_by_label_sets_label(unsorted_result):
    group = group_by_label("staging", unsorted_result)
    assert group.label == "staging"


def test_group_by_label_sorts_keys(unsorted_result):
    group = group_by_label("staging", unsorted_result)
    assert group.missing_in_target == ["ALPHA", "MANGO", "ZEBRA"]
    assert group.missing_in_base == ["BETA", "OMEGA"]
    assert list(group.mismatched.keys()) == ["HOST", "PORT"]


def test_total_issues(unsorted_result):
    group = group_by_label("prod", unsorted_result)
    assert group.total_issues == 3 + 2 + 2


def test_total_issues_empty():
    group = GroupedDiff(label="empty")
    assert group.total_issues == 0


def test_merge_groups_indexes_by_label(unsorted_result):
    g1 = group_by_label("staging", unsorted_result)
    g2 = group_by_label("prod", unsorted_result)
    merged = merge_groups([g1, g2])
    assert set(merged.keys()) == {"staging", "prod"}
    assert merged["staging"].label == "staging"


def test_merge_groups_empty():
    assert merge_groups([]) == {}
