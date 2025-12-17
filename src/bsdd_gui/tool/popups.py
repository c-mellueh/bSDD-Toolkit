from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QInputDialog,
    QLabel,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
)
import os
import re
import bsdd_gui
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.module.popups import ui
from pydantic import ValidationError

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
    def create_info_popup(cls, text, window_title: str = None, text_title: str = None, parent=None):
        if window_title is None:
            window_title = QCoreApplication.translate("Popups", "Info")
        if text_title is None:
            text_title = QCoreApplication.translate("Popups", "Info")
        icon = get_icon()
        msg_box = QMessageBox(parent)
        msg_box.setText(text_title)
        msg_box.setWindowTitle(window_title)
        msg_box.setDetailedText(text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowIcon(icon)
        msg_box.exec()

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
            )
            path
        else:
            path = QFileDialog.getOpenFileName(
                window, title, path, f"{file_format} Files (*.{file_format})"
            )
        pure_path, end = path
        try:
            if not end:
                return pure_path
            texts = re.search(r"\(\*(\..*)\)", end).groups()
            if not texts:
                return pure_path
            ending = texts[0]
            if not pure_path.lower().endswith(ending.lower()):
                pure_path += ending
            return pure_path
        except:
            return pure_path

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

    @classmethod
    def request_sloppy_load(cls, error: ValidationError):
        window = QApplication.activeWindow()
        dialog = QDialog(window)
        dialog.setModal(True)
        dialog.setWindowTitle(QCoreApplication.translate("Project", "Project Load Warning"))
        dialog.setWindowIcon(get_icon())
        dialog.setSizeGripEnabled(True)

        layout = QVBoxLayout(dialog)

        message_label = QLabel(
            QCoreApplication.translate("Project", "The project failed validation.")
        )
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        question_label = QLabel(
            QCoreApplication.translate("Project", "Do you want to try loading it in sloppy mode?")
        )
        question_label.setWordWrap(True)
        layout.addWidget(question_label)

        detail = QPlainTextEdit(dialog)
        detail.setReadOnly(True)
        detail.setPlainText(str(error))
        detail.setMinimumHeight(120)
        layout.addWidget(detail)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
            parent=dialog,
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        no_button = button_box.button(QDialogButtonBox.StandardButton.No)
        if no_button:
            no_button.setDefault(True)
            no_button.setFocus()

        dialog.resize(420, 320)
        return dialog.exec() == QDialog.DialogCode.Accepted

    @classmethod
    def request_overwrite_lock(cls, path: str) -> bool:
        window = QApplication.activeWindow()
        dialog = QDialog(window)
        dialog.setModal(True)
        dialog.setWindowTitle(QCoreApplication.translate("Project", "Project Lock Warning"))
        dialog.setWindowIcon(get_icon())

        layout = QVBoxLayout(dialog)

        message_label = QLabel(
            QCoreApplication.translate(
                "Project",
                "The project file is already locked. Do you want to overwrite the lock?",
            )
        )
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        path_label = QLabel(path)
        path_label.setWordWrap(True)
        layout.addWidget(path_label)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
            parent=dialog,
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        no_button = button_box.button(QDialogButtonBox.StandardButton.No)
        if no_button:
            no_button.setDefault(True)
            no_button.setFocus()

        dialog.resize(400, 150)
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @classmethod
    def request_save_before_exit(cls):
        icon = get_icon()
        title = QCoreApplication.translate("Popups", "Save before exit")
        text = QCoreApplication.translate(
            "Popups", "You have some unsaved Changes!\nDo you want to save the project before leaving?"
        )
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            title,
            text,
            QMessageBox.StandardButton.Cancel
            | QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.No,
        )

        msg_box.setWindowIcon(icon)
        reply = msg_box.exec()
        if reply == msg_box.StandardButton.Save:
            return True
        elif reply == msg_box.StandardButton.No:
            return False
        return None