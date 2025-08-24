from __future__ import annotations

import datetime
import logging
import os
import sys
import traceback
from typing import TYPE_CHECKING

import appdirs
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QCheckBox, QMessageBox

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.logging.prop import LoggingProperties
    from bsdd_gui.module.logging import ui

from bsdd_gui.resources.icons import get_icon
from bsdd_gui import tool
from bsdd_gui.module.logging.constants import LOG_PATH, LOG_SECTION, LOG_LEVEL


class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)

    def format(self, record: logging.LogRecord):
        # Combine module and function name
        path_name = record.pathname.split("\\")[-2]
        module_func = f"{path_name}.{record.module}.{record.funcName}"
        # Ensure the combined string is 50 characters long
        if len(module_func) > 50:
            module_func = module_func[:47] + "..."
        else:
            module_func = module_func.ljust(50)

        # Set the custom property
        record.module_func = module_func

        return super().format(record)


class Signaller(QObject):
    error = Signal(logging.LogRecord, str)


class PopupHandler(logging.Handler):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.signaller = tool.Logging.get_signaller()

    def emit(self, record):
        if record.levelno >= logging.WARNING:
            msg = self.format(record)
            self.signaller.error.emit(record, msg)


class Logging:
    @classmethod
    def get_properties(cls) -> LoggingProperties:
        return bsdd_gui.LoggingProperties

    @classmethod
    def show_popup(cls, record: logging.LogRecord, message):
        level_no = record.levelno
        # find path of error
        identifier = f"{record.pathname}.{record.module}.{record.funcName}.{record.lineno}"
        # if this error was set to be ignored, don't show popup
        if identifier in cls.get_properties().ignore_texts:
            return
        msg_box = QMessageBox()
        states = [
            (QMessageBox.Icon.Information, "Information"),
            (QMessageBox.Icon.Warning, "Warning"),
            (QMessageBox.Icon.Critical, "Error"),
        ]
        icon, level = (
            states[0]
            if level_no < logging.WARNING
            else states[1] if level_no < logging.ERROR else states[2]
        )
        msg_box.setIcon(icon)
        cb = QCheckBox("nicht erneut anzeigen")
        msg_box.setCheckBox(cb)
        msg_box.setWindowIcon(get_icon())
        title = tool.Util.get_window_title(str(level))
        msg_box.setWindowTitle(title)
        msg_box.setText(f"An {level} occurred:")
        msg_box.setDetailedText(message)
        if msg_box.exec_() and cb.isChecked():
            cls.get_properties().ignore_texts.append(identifier)

    @classmethod
    def get_signaller(cls):
        if cls.get_properties().signaller is None:
            cls.get_properties().signaller = Signaller()
            cls.get_properties().signaller.error.connect(cls.show_popup)
        return cls.get_properties().signaller

    @classmethod
    def get_log_level(cls):
        return tool.Appdata.get_int_setting(LOG_SECTION, LOG_LEVEL, logging.WARNING)

    @classmethod
    def set_log_level(cls, log_level: int):
        tool.Appdata.set_setting(LOG_SECTION, LOG_LEVEL, log_level)

        cls.get_logger().setLevel(log_level)
        for handler in cls.get_logger().handlers:
            handler.setLevel(log_level)
        logging.info(f"Set Loglevel {log_level}")

    @classmethod
    def get_logger(cls):
        return logging.getLogger()

    @classmethod
    def set_logging_directory(cls, path: str, check_if_identical=True):
        if check_if_identical:
            if path == cls.get_logging_directory():
                return
        if not os.path.exists(path):
            tool.Util.create_directory(path)

        tool.Appdata.set_path(LOG_PATH, path)
        for handler in cls.get_logger().handlers:
            if isinstance(handler, logging.FileHandler):
                cls.get_logger().removeHandler(handler)
                handler.close()

        cls.get_logger().addHandler(cls.create_file_handler(cls.get_logging_filename()))

    @classmethod
    def get_logging_directory(cls):
        path = tool.Appdata.get_path(LOG_PATH)
        if not path:
            appdata_path = appdirs.user_log_dir(bsdd_gui.__name__)
            cls.set_logging_directory(appdata_path, check_if_identical=False)
        return tool.Appdata.get_path(LOG_PATH)

    @classmethod
    def get_logging_filename(cls):
        if cls.get_properties().log_path is None:
            dir_path = cls.get_logging_directory()
            file_name = f"{datetime.datetime.now(datetime.timezone.utc)}.log"
            file_name = file_name.replace(":", "_")
            file_name = file_name.replace(" ", "_")
            logpath = os.path.join(dir_path, file_name)

            cls.get_properties().log_path = logpath
        return cls.get_properties().log_path

    @classmethod
    def create_console_handler(cls):
        console_handler = logging.StreamHandler()
        log_level = cls.get_log_level()
        if log_level != logging.INFO:
            log_level -= 10
        console_handler.setLevel(log_level)
        console_handler.setFormatter(cls.get_custom_formatter())
        return console_handler

    @classmethod
    def create_file_handler(cls, path: str | os.PathLike) -> logging.FileHandler:
        path = path.replace("\\", "/")
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(cls.get_log_level())
        file_handler.setFormatter(cls.get_custom_formatter())
        return file_handler

    @classmethod
    def get_custom_formatter(cls) -> CustomFormatter:
        if cls.get_properties().custom_formatter is None:
            log_format = cls.get_properties().log_format
            cls.get_properties().custom_formatter = CustomFormatter(log_format)
        return cls.get_properties().custom_formatter

    @classmethod
    def create_popup_handler(cls, main_window):
        popup_handler = PopupHandler(main_window)
        popup_handler.setLevel(cls.get_log_level())
        popup_handler.setFormatter(cls.get_custom_formatter())
        return popup_handler

    @classmethod
    def create_error_popup(cls):
        sys.excepthook = cls.show_exception_popup

    @classmethod
    def show_exception_popup(cls, exctype, value, tb):
        error_message = "".join(traceback.format_exception(exctype, value, tb))
        logging.error(error_message)

    @classmethod
    def get_settings_widget(cls) -> ui.SettingsWidget:
        return cls.get_properties().settings_widget

    @classmethod
    def set_settings_widget(cls, widget: ui.SettingsWidget):
        cls.get_properties().settings_widget = widget
