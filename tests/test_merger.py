"""Tests for envdiff.merger."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.merger import merge_env_files, MergeResult, MergeConflict


@pytest.fixture()
def tmp_envs(tmp_path):
    """Return a helper that writes a .env file and returns its Path."""
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


def test_requires_at_least_two_paths(tmp_envs):
    p = tmp_envs("a.env", "KEY=1\n")
    with pytest.raises(ValueError, match="at least two"):
        merge_env_files([p])


def test_merged_contains_all_keys(tmp_envs):
    a = tmp_envs("a.env", "A=1\nB=2\n")
    b = tmp_envs("b.env", "C=3\n")
    result = merge_env_files([a, b])
    assert result.merged == {"A": "1", "B": "2", "C": "3"}


def test_later_file_wins_on_conflict(tmp_envs):
    a = tmp_envs("a.env", "KEY=original\n")
    b = tmp_envs("b.env", "KEY=override\n")
    result = merge_env_files([a, b])
    assert result.merged["KEY"] == "override"


def test_conflict_recorded(tmp_envs):
    a = tmp_envs("a.env", "KEY=original\n")
    b = tmp_envs("b.env", "KEY=override\n")
    result = merge_env_files([a, b])
    assert result.has_conflicts
    assert result.conflict_count == 1
    conflict = result.conflicts[0]
    assert conflict.key == "KEY"
    assert conflict.original_value == "original"
    assert conflict.winning_value == "override"


def test_no_conflict_when_values_equal(tmp_envs):
    a = tmp_envs("a.env", "KEY=same\n")
    b = tmp_envs("b.env", "KEY=same\n")
    result = merge_env_files([a, b])
    assert not result.has_conflicts


def test_custom_labels_used_in_conflict(tmp_envs):
    a = tmp_envs("a.env", "X=1\n")
    b = tmp_envs("b.env", "X=2\n")
    result = merge_env_files([a, b], labels=["base", "override"])
    assert result.conflicts[0].original_source == "base"
    assert result.conflicts[0].winning_source == "override"


def test_sources_list_matches_labels(tmp_envs):
    a = tmp_envs("a.env", "A=1\n")
    b = tmp_envs("b.env", "B=2\n")
    result = merge_env_files([a, b], labels=["env-a", "env-b"])
    assert result.sources == ["env-a", "env-b"]


def test_three_way_merge(tmp_envs):
    a = tmp_envs("a.env", "K=1\n")
    b = tmp_envs("b.env", "K=2\n")
    c = tmp_envs("c.env", "K=3\n")
    result = merge_env_files([a, b, c])
    assert result.merged["K"] == "3"
    # two conflicts recorded (a->b and b->c)
    assert result.conflict_count == 2


def test_as_dict_structure(tmp_envs):
    a = tmp_envs("a.env", "X=old\n")
    b = tmp_envs("b.env", "X=new\n")
    result = merge_env_files([a, b], labels=["a", "b"])
    d = result.as_dict()
    assert "merged" in d
    assert "conflicts" in d
    assert "sources" in d
    assert d["conflicts"][0]["key"] == "X"
