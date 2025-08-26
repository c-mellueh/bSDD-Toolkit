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
import os
import bsdd_gui
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.module.popups import ui

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

    @classmethod
    def get_open_path(cls, file_format: str, window, path=None, title=None) -> str:
        return cls._get_path(file_format, window, path, False, title)

    @classmethod
    def get_save_path(cls, file_format: str, window, path=None, title=None) -> str:
        return cls._get_path(file_format, window, path, True, title)

    @classmethod
    def _get_path(cls, file_format: str, window, path=None, save: bool = False, title=None) -> str:
        """File Open Dialog with modifiable file_format"""
        if path:
            basename = os.path.basename(path)
            split = os.path.splitext(basename)[0]
            filename_without_extension = os.path.splitext(split)[0]
            dirname = os.path.dirname(path)
            path = os.path.join(dirname, filename_without_extension)
        if title is None:
            title = f"Save {file_format}" if save else f"Open {file_format}"

        if save:
            path = QFileDialog.getSaveFileName(
                window, title, path, f"{file_format} Files (*.{file_format})"
            )[0]
        else:
            path = QFileDialog.getOpenFileName(
                window, title, path, f"{file_format} Files (*.{file_format})"
            )[0]
        return path

    @classmethod
    def get_folder(cls, window, path: str) -> str:
        """Folder Open Dialog"""
        if path:
            path = os.path.basename(path)
        path = QFileDialog.getExistingDirectory(parent=window, dir=path)
        return path

    @classmethod
    def req_delete_items(cls, string_list, item_type=1) -> tuple[bool, bool]:
        """
        item_type 1= Class,2= Node, 3 = PropertySet, 4 = Property
        """
        dialog = ui.DeleteRequestDialog()
        if len(string_list) <= 1:
            if item_type == 1:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete Class?"))
            if item_type == 2:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete Node?"))
            if item_type == 3:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete PropertySet?"))
            if item_type == 4:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete Property?"))
        else:
            if item_type == 1:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete Classes?"))
            if item_type == 2:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete Nodes?"))
            if item_type == 3:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete PropertySets?"))
            if item_type == 4:
                dialog.label.setText(QCoreApplication.translate("Popups", "Delete Properties?"))
        for text in string_list:
            dialog.listWidget.addItem(QListWidgetItem(text))
        result = dialog.exec()
        check_box_state = (
            True if dialog.check_box_recursion.checkState() == Qt.CheckState.Checked else False
        )
        return bool(result), check_box_state
