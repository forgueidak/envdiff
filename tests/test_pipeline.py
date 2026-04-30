"""Tests for envdiff.pipeline — multi-environment pipeline runner."""

from pathlib import Path

import pytest

from envdiff.differ import DiffOptions
from envdiff.pipeline import PipelineResult, run_pipeline


@pytest.fixture()
def three_envs(tmp_path: Path):
    dev = tmp_path / ".env.dev"
    staging = tmp_path / ".env.staging"
    prod = tmp_path / ".env.prod"

    dev.write_text("APP=app\nDEBUG=true\nDEV_ONLY=yes\n")
    staging.write_text("APP=app\nDEBUG=false\n")
    prod.write_text("APP=app\nDEBUG=false\nPROD_ONLY=yes\n")

    return dev, staging, prod


def test_pipeline_requires_at_least_two_paths(tmp_path):
    with pytest.raises(ValueError, match="At least two"):
        run_pipeline([tmp_path / ".env"])


def test_pipeline_creates_correct_number_of_runs(three_envs):
    dev, staging, prod = three_envs
    result = run_pipeline([dev, staging, prod])
    assert len(result.runs) == 2


def test_pipeline_run_order(three_envs):
    dev, staging, prod = three_envs
    result = run_pipeline([dev, staging, prod])
    assert result.runs[0].base_path == dev
    assert result.runs[0].target_path == staging
    assert result.runs[1].base_path == staging
    assert result.runs[1].target_path == prod


def test_pipeline_any_issues_true_when_differences(three_envs):
    dev, staging, prod = three_envs
    result = run_pipeline([dev, staging, prod])
    assert result.any_issues is True


def test_pipeline_any_issues_false_when_identical(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    content = "KEY=value\nOTHER=123\n"
    a.write_text(content)
    b.write_text(content)
    result = run_pipeline([a, b])
    assert result.any_issues is False


def test_pipeline_issue_counts_keys(three_envs):
    dev, staging, prod = three_envs
    result = run_pipeline([dev, staging, prod])
    counts = result.issue_counts
    assert ".env.dev -> .env.staging" in counts
    assert ".env.staging -> .env.prod" in counts


def test_pipeline_as_dict_structure(three_envs):
    dev, staging, prod = three_envs
    result = run_pipeline([dev, staging, prod])
    d = result.as_dict()
    assert "any_issues" in d
    assert "runs" in d
    assert len(d["runs"]) == 2
    assert "total_issues" in d["runs"][0]


def test_pipeline_two_paths(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("X=1\n")
    b.write_text("X=2\n")
    result = run_pipeline([a, b])
    assert len(result.runs) == 1
    assert result.any_issues is True
