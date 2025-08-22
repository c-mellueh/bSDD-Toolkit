from __future__ import annotations
from PySide6.QtWidgets import QApplication
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui import tool


import logging

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_project(project: Type[tool.Project]):
    logging.debug(f"Create Project")
    project.create_project()


def open_project(path, project: Type[tool.Project]):
    proj = project.load_project(path)
