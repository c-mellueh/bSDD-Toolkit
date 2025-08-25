from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QListWidgetItem,
    QMessageBox,
)

import bsdd_gui
from bsdd_gui.resources.icons import get_icon

if TYPE_CHECKING:
    from bsdd_gui.module.popups.prop import PopupsProperties


class Popups:
    @classmethod
    def get_properties(cls) -> PopupsProperties:
        return bsdd_gui.PopupsProperties

    @classmethod
    def msg_unsaved(cls):
        icon = get_icon()
        msg_box = QMessageBox()
        text = QCoreApplication.translate("Popups", "Warning! All unsaved changes will be lost!")
        msg_box.setText(text)
        msg_box.setWindowTitle(" ")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        msg_box.setWindowIcon(icon)
        if msg_box.exec() == msg_box.StandardButton.Ok:
            return True
        else:
            return False

    @classmethod
    def create_warning_popup(cls, text, window_title: str = None, text_title: str = None):
        if window_title is None:
            window_title = QCoreApplication.translate("Popups", "Warning")
        if text_title is None:
            text_title = QCoreApplication.translate("Popups", "Warning")
        icon = get_icon()
        msg_box = QMessageBox()
        msg_box.setText(text_title)
        msg_box.setWindowTitle(window_title)
        msg_box.setDetailedText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowIcon(icon)
        msg_box.exec()
