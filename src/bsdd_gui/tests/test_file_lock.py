"""
Tests for the FileLock module (tool/file_lock.py).

Each test gets a fresh temp file so that lock/unlock operations are isolated.
The FileLock tool uses class-level state (bsdd_gui.FileLockProperties), so
we always call unlock_file() in teardown to keep the state clean.
"""
from __future__ import annotations

import os

import pytest
from bsdd_gui.tool import FileLock


# ---------------------------------------------------------------------------
# Fixture: temp target file + automatic unlock
# ---------------------------------------------------------------------------

@pytest.fixture()
def target_file(tmp_path):
    """A real file that can be locked."""
    f = tmp_path / "project.json"
    f.write_text("{}")
    yield str(f)
    # Ensure the lock is released even if a test fails
    FileLock.unlock_file()


# ---------------------------------------------------------------------------
# 1. build_lockpath
# ---------------------------------------------------------------------------

class TestBuildLockpath:
    def test_appends_lock_extension(self, tmp_path):
        p = str(tmp_path / "file.json")
        lock = FileLock.build_lockpath(p)
        assert lock == os.path.abspath(p) + ".lock"

    def test_returns_absolute_path(self, tmp_path):
        p = str(tmp_path / "file.json")
        lock = FileLock.build_lockpath(p)
        assert os.path.isabs(lock)


# ---------------------------------------------------------------------------
# 2. lock_file
# ---------------------------------------------------------------------------

class TestLockFile:
    def test_lock_creates_lock_file(self, target_file):
        FileLock.lock_file(target_file)
        lock_path = FileLock.build_lockpath(target_file)
        assert os.path.exists(lock_path)

    def test_lock_returns_true_on_success(self, target_file):
        assert FileLock.lock_file(target_file) is True

    def test_lock_returns_false_for_nonexistent_file(self, tmp_path):
        missing = str(tmp_path / "missing.json")
        assert FileLock.lock_file(missing) is False

    def test_lock_returns_true_when_already_held_by_us(self, target_file):
        FileLock.lock_file(target_file)
        # Calling again should succeed without double-locking
        assert FileLock.lock_file(target_file) is True

    def test_lock_stores_path(self, target_file):
        FileLock.lock_file(target_file)
        assert FileLock.get_path() == os.path.abspath(target_file)

    def test_lock_file_contains_pid(self, target_file):
        FileLock.lock_file(target_file)
        lock_path = FileLock.get_lock_path()
        with open(lock_path, "rb") as f:
            contents = f.read().decode()
        assert f"pid:{os.getpid()}" in contents


# ---------------------------------------------------------------------------
# 3. unlock_file
# ---------------------------------------------------------------------------

class TestUnlockFile:
    def test_unlock_removes_lock_file(self, target_file):
        FileLock.lock_file(target_file)
        lock_path = FileLock.get_lock_path()
        FileLock.unlock_file()
        assert not os.path.exists(lock_path)

    def test_unlock_clears_path(self, target_file):
        FileLock.lock_file(target_file)
        FileLock.unlock_file()
        assert FileLock.get_path() is None

    def test_unlock_clears_file_descriptor(self, target_file):
        FileLock.lock_file(target_file)
        FileLock.unlock_file()
        assert FileLock.get_file() is None

    def test_unlock_when_not_locked_does_not_raise(self):
        FileLock.unlock_file()  # should be a no-op


# ---------------------------------------------------------------------------
# 4. _build_lock_contents
# ---------------------------------------------------------------------------

class TestBuildLockContents:
    def test_contains_pid(self):
        contents = FileLock._build_lock_contents().decode()
        assert f"pid:{os.getpid()}" in contents

    def test_contains_locked_by_marker(self):
        contents = FileLock._build_lock_contents().decode()
        assert "locked by" in contents

    def test_contains_at_marker(self):
        contents = FileLock._build_lock_contents().decode()
        assert " at " in contents

    def test_is_bytes(self):
        assert isinstance(FileLock._build_lock_contents(), bytes)
