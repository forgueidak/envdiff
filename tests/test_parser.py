"""Tests for the envdiff parser module."""

import os
import tempfile
import pytest

from envdiff.parser import parse_env_file, parse_env_files, _strip_quotes


def write_temp_env(content: str) -> str:
    """Helper to write content to a temporary .env file and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


class TestStripQuotes:
    def test_double_quotes(self):
        assert _strip_quotes('"hello world"') == 'hello world'

    def test_single_quotes(self):
        assert _strip_quotes("'hello world'") == 'hello world'

    def test_no_quotes(self):
        assert _strip_quotes('hello') == 'hello'

    def test_mismatched_quotes(self):
        assert _strip_quotes('"hello\'') == '"hello\''

    def test_empty_string(self):
        assert _strip_quotes('') == ''


class TestParseEnvFile:
    def test_basic_key_value(self):
        path = write_temp_env('KEY=value\n')
        try:
            result = parse_env_file(path)
            assert result == {'KEY': 'value'}
        finally:
            os.unlink(path)

    def test_quoted_values(self):
        path = write_temp_env('SECRET="my secret"\nTOKEN=\'abc123\'\n')
        try:
            result = parse_env_file(path)
            assert result['SECRET'] == 'my secret'
            assert result['TOKEN'] == 'abc123'
        finally:
            os.unlink(path)

    def test_comments_and_blank_lines_skipped(self):
        content = '# This is a comment\n\nDB_HOST=localhost\n'
        path = write_temp_env(content)
        try:
            result = parse_env_file(path)
            assert result == {'DB_HOST': 'localhost'}
        finally:
            os.unlink(path)

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_env_file('/nonexistent/path/.env')

    def test_invalid_syntax_raises(self):
        path = write_temp_env('INVALID LINE WITHOUT EQUALS\n')
        try:
            with pytest.raises(ValueError, match='Invalid syntax'):
                parse_env_file(path)
        finally:
            os.unlink(path)

    def test_empty_value(self):
        path = write_temp_env('EMPTY=\n')
        try:
            result = parse_env_file(path)
            assert result == {'EMPTY': ''}
        finally:
            os.unlink(path)


class TestParseEnvFiles:
    def test_multiple_files(self):
        path1 = write_temp_env('A=1\nB=2\n')
        path2 = write_temp_env('A=1\nC=3\n')
        try:
            result = parse_env_files(path1, path2)
            assert result[path1] == {'A': '1', 'B': '2'}
            assert result[path2] == {'A': '1', 'C': '3'}
        finally:
            os.unlink(path1)
            os.unlink(path2)
