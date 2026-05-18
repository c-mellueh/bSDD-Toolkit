"""
Pytest configuration for bsdd_gui tests.

A QApplication must exist before any bsdd_gui module is imported, because
tool classes define Qt signals as class-level attributes (QObject subclasses).
We create the application at module-import time so it is present when pytest
collects the test files.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

# Create exactly one QApplication for the entire test session.
_qapp = QApplication.instance() or QApplication(sys.argv[:1])

import bsdd_gui  # noqa: E402

bsdd_gui.register()

import pytest  # noqa: E402
from bsdd_json.models import BsddDictionary  # noqa: E402
from bsdd_gui.tool import ClassTreeView  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication (satisfies pytest-qt expectations)."""
    return _qapp


@pytest.fixture()
def dictionary() -> BsddDictionary:
    """A fresh, empty BsddDictionary for each test."""
    return BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="TEST_DICT",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
    )


@pytest.fixture()
def model_fixture(dictionary: BsddDictionary):
    """
    Creates a ClassTreeModel backed by *dictionary* and tears it down afterwards.

    Yields (proxy_model, source_model, dictionary).
    """
    proxy, model = ClassTreeView.create_model(dictionary)
    ClassTreeView.add_column_to_table(model, "Name", lambda a: a.Name)
    ClassTreeView.add_column_to_table(model, "Code", lambda a: a.Code)
    ClassTreeView.add_column_to_table(model, "Status", lambda a: a.Status)

    yield proxy, model, dictionary

    ClassTreeView.remove_model(model)
    ClassTreeView.get_properties().columns.pop(model, None)
