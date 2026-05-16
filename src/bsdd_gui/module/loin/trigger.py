from __future__ import annotations

from bsdd_gui import tool
from bsdd_gui.core import loin as core


def connect():
    pass


def retranslate_ui():
    pass


def on_new_project():
    core.reset(tool.Loin)

def import_xml(path):
    core.import_from_xml(path,tool.Loin,tool.Project)