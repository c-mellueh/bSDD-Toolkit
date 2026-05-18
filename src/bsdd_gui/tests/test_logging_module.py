"""
Tests for the Logging module (tool/logging.py).

Covers CustomFormatter (pure Python) and the level-management helpers that
delegate to Appdata (also pure Python).
"""
from __future__ import annotations

import logging
import os

from bsdd_gui.tool.logging import CustomFormatter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_record(
    pathname: str = os.path.join("some", "package", "module.py"),
    func: str = "my_function",
    msg: str = "test message",
    level: int = logging.INFO,
) -> logging.LogRecord:
    return logging.LogRecord(
        name="test",
        level=level,
        pathname=pathname,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
        func=func,
    )


# ---------------------------------------------------------------------------
# 1. CustomFormatter.format
# ---------------------------------------------------------------------------

class TestCustomFormatter:
    def test_format_adds_module_func_attribute(self):
        fmt = CustomFormatter()
        record = _make_record()
        fmt.format(record)
        assert hasattr(record, "module_func")

    def test_module_func_contains_function_name(self):
        fmt = CustomFormatter()
        record = _make_record(func="do_something")
        fmt.format(record)
        assert "do_something" in record.module_func

    def test_module_func_max_length_is_50(self):
        fmt = CustomFormatter()
        long_func = "a" * 60
        record = _make_record(func=long_func)
        fmt.format(record)
        assert len(record.module_func) == 50

    def test_short_module_func_is_padded_to_50(self):
        fmt = CustomFormatter()
        record = _make_record(func="f")
        fmt.format(record)
        assert len(record.module_func) == 50

    def test_long_module_func_ends_with_ellipsis(self):
        fmt = CustomFormatter()
        long_func = "x" * 60
        record = _make_record(func=long_func)
        fmt.format(record)
        assert record.module_func.endswith("...")

    def test_format_returns_string(self):
        fmt = CustomFormatter("%(message)s")
        record = _make_record(msg="hello")
        result = fmt.format(record)
        assert "hello" in result

    def test_module_func_includes_parent_folder(self):
        fmt = CustomFormatter()
        pathname = os.path.join("root", "mypackage", "mymodule.py")
        record = _make_record(pathname=pathname)
        fmt.format(record)
        # Second-to-last path component should appear
        assert "mypackage" in record.module_func
