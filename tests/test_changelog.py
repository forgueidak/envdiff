"""Tests for envdiff.changelog."""
import json
from pathlib import Path

import pytest

from envdiff.changelog import (
    Changelog,
    ChangelogEntry,
    load_changelog,
    record_entry,
    save_changelog,
)
from envdiff.comparator import DiffResult


@pytest.fixture
def simple_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST"},
        missing_in_base={"NEW_KEY"},
        mismatched={"API_URL": ("http://dev", "http://prod")},
    )


def test_record_entry_captures_missing_in_target(simple_result):
    entry = record_entry(simple_result, "dev", "prod")
    assert "DB_HOST" in entry.missing_in_target


def test_record_entry_captures_missing_in_base(simple_result):
    entry = record_entry(simple_result, "dev", "prod")
    assert "NEW_KEY" in entry.missing_in_base


def test_record_entry_captures_mismatched(simple_result):
    entry = record_entry(simple_result, "dev", "prod")
    assert "API_URL" in entry.mismatched


def test_record_entry_sets_labels(simple_result):
    entry = record_entry(simple_result, "base_env", "target_env")
    assert entry.base == "base_env"
    assert entry.target == "target_env"


def test_record_entry_accepts_custom_timestamp(simple_result):
    ts = "2024-01-01T00:00:00+00:00"
    entry = record_entry(simple_result, "a", "b", timestamp=ts)
    assert entry.timestamp == ts


def test_total_issues_sums_all_categories(simple_result):
    entry = record_entry(simple_result, "a", "b")
    assert entry.total_issues == 3


def test_total_issues_zero_for_clean_result():
    result = DiffResult(missing_in_target=set(), missing_in_base=set(), mismatched={})
    entry = record_entry(result, "a", "b")
    assert entry.total_issues == 0


def test_changelog_add_increments_length(simple_result):
    cl = Changelog()
    entry = record_entry(simple_result, "a", "b")
    cl.add(entry)
    assert len(cl) == 1


def test_changelog_as_dict_contains_entries(simple_result):
    cl = Changelog()
    cl.add(record_entry(simple_result, "a", "b"))
    d = cl.as_dict()
    assert "entries" in d
    assert len(d["entries"]) == 1


def test_save_creates_file(simple_result, tmp_path):
    cl = Changelog()
    cl.add(record_entry(simple_result, "a", "b"))
    out = tmp_path / "changelog.json"
    save_changelog(cl, out)
    assert out.exists()


def test_save_file_is_valid_json(simple_result, tmp_path):
    cl = Changelog()
    cl.add(record_entry(simple_result, "a", "b"))
    out = tmp_path / "changelog.json"
    save_changelog(cl, out)
    data = json.loads(out.read_text())
    assert "entries" in data


def test_roundtrip_preserves_entry_count(simple_result, tmp_path):
    cl = Changelog()
    cl.add(record_entry(simple_result, "a", "b"))
    cl.add(record_entry(simple_result, "b", "c"))
    out = tmp_path / "changelog.json"
    save_changelog(cl, out)
    loaded = load_changelog(out)
    assert len(loaded) == 2


def test_roundtrip_preserves_labels(simple_result, tmp_path):
    cl = Changelog()
    cl.add(record_entry(simple_result, "staging", "production"))
    out = tmp_path / "changelog.json"
    save_changelog(cl, out)
    loaded = load_changelog(out)
    assert loaded.entries[0].base == "staging"
    assert loaded.entries[0].target == "production"
