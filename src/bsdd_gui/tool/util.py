from __future__ import annotations

import logging
import os
import re
import tempfile
from typing import Callable, TYPE_CHECKING
import datetime
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QPalette, QBrush
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLineEdit,
    QMenu,
    QMenuBar,
    QWidget,
    QListWidget,
    QCompleter,
    QApplication,
)

import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.module.util import ui
from bsdd_gui.module.util.constants import OPTION_SEPERATOR
from bsdd_gui.presets.ui_presets.waiting import start_waiting_widget, stop_waiting_widget
from bsdd_gui.presets.ui_presets import ComboBoxWithToggleSwitch
from bsdd_gui.presets.tool_presets import FieldTool


if TYPE_CHECKING:
    from bsdd_gui.module.util.prop import MenuDict, UtilProperties


class Util:
    @classmethod
    def get_properties(cls) -> UtilProperties:
        return bsdd_gui.UtilProperties

    @classmethod
    def create_progressbar(cls, *args, **kwargs) -> ui.Progressbar:
        return ui.Progressbar(*args, **kwargs)

    @classmethod
    def set_progress(cls, progress_bar: ui.Progressbar, value):
        progress_bar.ui.progressBar.setValue(value)

    @classmethod
    def set_status(cls, progress_bar: ui.Progressbar, value):
        progress_bar.ui.label.setText(value)

    @classmethod
    def menu_bar_add_menu(cls, menu_bar: QMenuBar, menu_dict: MenuDict, menu_path: str) -> MenuDict:
        menu_steps = menu_path.split("/")
        focus_dict = menu_dict
        parent = menu_bar
        for index, menu_name in enumerate(menu_steps):
            if not menu_name in {menu["name"] for menu in focus_dict["submenu"]}:
                menu = QMenu(parent)
                menu.setTitle(menu.tr(menu_name))
                d = {
                    "name": menu_name,
                    "submenu": list(),
                    "actions": list(),
                    "menu": menu,
                }
                focus_dict["submenu"].append(d)
            sub_menus = {menu["name"]: menu for menu in focus_dict["submenu"]}
            focus_dict = sub_menus[menu_name]
            parent = focus_dict["menu"]
        return focus_dict

    @classmethod
    def menu_bar_add_action(
        cls, menu_bar: QMenuBar, menu_dict: MenuDict, menu_path: str, function: Callable
    ):
        menu_steps = menu_path.split("/")
        if len(menu_steps) != 1:
            menu_dict = cls.menu_bar_add_menu(menu_bar, menu_dict, "/".join(menu_steps[:-1]))
            action = QAction(menu_dict["menu"])
            action.setText(action.tr(menu_steps[-1]))
            action.triggered.connect(function)
            menu_dict["actions"].append(action)
        else:
            action = QAction(menu_steps[0])
            menu_dict["actions"].append(action)
            action.triggered.connect(function)

    @classmethod
    def menu_bar_create_actions(cls, menu_dict: MenuDict, parent: QMenu | QMenuBar | None):
        menu = menu_dict["menu"]
        if parent is not None:
            parent.addMenu(menu)
        for sd in menu_dict["submenu"]:
            cls.menu_bar_create_actions(sd, menu)
        for action in menu_dict["actions"]:
            menu.addAction(action)

    @classmethod
    def add_shortcut(
        cls,
        sequence: str,
        window: QWidget,
        function: Callable,
        context=Qt.ShortcutContext.WidgetShortcut,
    ):
        prop = cls.get_properties()
        shortcut = QShortcut(QKeySequence(sequence), window)
        shortcut.setContext(context)
        prop.shortcuts.append(shortcut)
        shortcut.activated.connect(function)

    @classmethod
    def create_context_menu(cls, menu_list: list[list[str, Callable]]) -> QMenu:
        """
        Create a context menu from a menu list.
        The Menu List contains of tuples containing the displayname of action and the callable function itself
        If the displayname contains '/' submenus will be created
        """

        menu_dict = dict()
        menu = QMenu()
        menu_dict[""] = menu
        for text, function in menu_list:
            cls.context_menu_create_action(menu_dict, text, function, False)
        return menu

    @classmethod
    def context_menu_create_action(
        cls,
        menu_dict: dict[str, QAction | QMenu],
        name: str,
        action_func: None | Callable,
        is_sub_menu: bool,
    ):
        parent_structure = "/".join(name.split("/")[:-1])
        if parent_structure not in menu_dict:
            parent: QMenu = cls.context_menu_create_action(menu_dict, parent_structure, None, True)
        else:
            parent: QMenu = menu_dict[parent_structure]

        if is_sub_menu:
            menu = parent.addMenu(name.split("/")[-1])
            menu_dict[name] = menu
            return menu

        action = parent.addAction(name.split("/")[-1])
        if action_func is not None:
            action.triggered.connect(action_func)
        menu_dict[name] = action
        return action

    @classmethod
    def create_tempfile(cls, suffix: str | None = None, add_timestamp=False) -> str:
        suffix = ".tmp" if suffix is None else suffix
        prefix = ""
        if add_timestamp:
            prefix = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S_")
        return os.path.abspath(tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix).name)

    @classmethod
    def transform_guid(cls, guid: str, add_zero_width: bool):
        """Fügt Zero Width Character ein weil PowerBI (WARUM AUCH IMMER FÜR EIN BI PROGRAMM?????) Case Insensitive ist"""
        if add_zero_width:
            return re.sub(r"([A-Z])", lambda m: m.group(0) + "\u200b", guid)
        else:
            return guid

    @classmethod
    def get_combobox_values(cls, combo_box: QComboBox):
        count = combo_box.count()
        return [combo_box.itemText(i) for i in range(count)]

    @classmethod
    def checkstate_to_bool(cls, checkstate: Qt.CheckState) -> bool:
        return False if checkstate == Qt.CheckState.Unchecked else True

    @classmethod
    def bool_to_checkstate(cls, checkstate: bool) -> Qt.CheckState:
        return Qt.CheckState.Checked if checkstate else Qt.CheckState.Unchecked

    @classmethod
    def create_directory(cls, path: os.PathLike):
        cur_path = list()
        split_path = str(path).split(os.sep)
        for path in split_path:
            if path == "":
                path = "/"
            cur_path.append(path)
            p = "/".join(cur_path)
            if not os.path.exists(p):
                os.mkdir(p)

    @classmethod
    def get_unique_name(cls, base_name: str, existing_names: list[str]) -> str:
        if base_name not in existing_names:
            return base_name
        index = 2
        while True:
            new_name = f"{base_name}-{index}"
            if new_name not in existing_names:
                return new_name
            index += 1

    @classmethod
    def get_text_from_combobox(cls, combobox: QComboBox) -> dict[str, QModelIndex]:
        model = combobox.mod()
        indexes = [model.index(r, 0) for r in range(model.rowCount())]
        return {model.data(index, Qt.ItemDataRole.DisplayRole): index for index in indexes}

    @classmethod
    def get_window_title(cls, window_name: str):
        proj = tool.Project.get()
        if not proj:
            status_text = ""
        else:
            status_text = f"{proj.DictionaryName} v{proj.DictionaryVersion}"

        return f"{window_name} | {status_text}"

    @classmethod
    def create_file_selector(
        cls,
        name: str,
        file_extension: str,
        appdata_text: str,
        request_folder=False,
        request_save=False,
        single_request=False,
    ) -> ui.FileSelector:
        """
        name: text that should be written in first row
        file_extension: file extension(s) that are allowed to search
        appdata_text: Appdata variable in which path(s) should be saved
        parent_widget: Widget that functions as parent (used for displaying QFileDialog)
        request_folder: True if Folder is requested else File is Requested
        request_save: True if Save is Requestes else Open is Requested
        single_request: True if want to open single file else multifile is allowed
        """
        selector = ui.FileSelector()
        cls.fill_file_selector(
            selector,
            name,
            file_extension,
            appdata_text,
            request_folder,
            request_save,
            single_request,
        )
        return selector

    @classmethod
    def fill_file_selector(
        cls,
        widget: ui.FileSelector,
        name: str,
        file_extension: str,
        appdata_text: str,
        request_folder=False,
        request_save=False,
        single_request=False,
        update_appdata=True,
    ):
        """
        if file selector is created as placeholder in QtDesiger it can befilled after creation
                name: text that should be written in first row
        file_extension: file extension(s) that are allowed to search
        appdata_text: Appdata variable in which path(s) should be saved
        parent_widget: Widget that functions as parent (used for displaying QFileDialog)
        request_folder: True if Folder is requested else File is Requested
        request_save: True if Save is Requestes else Open is Requested
        single_request: True if want to open single file else multifile is allowed
        """
        widget.name = name
        widget.extension = file_extension
        widget.appdata_text = appdata_text
        widget.request_folder = request_folder
        widget.request_save = request_save
        widget.single_request = single_request
        widget.update_appdata = update_appdata
        widget.ui.label.setText(name)

        if appdata_text:
            cls.autofill_path(widget.ui.lineEdit, appdata_text)

    @classmethod
    def get_path_from_fileselector(cls, file_selector: ui.FileSelector) -> list[str]:
        return file_selector.ui.lineEdit.text().split(OPTION_SEPERATOR)

    @classmethod
    def request_path(cls, widget: ui.FileSelector):
        if widget is None:
            logging.debug(f"Widget is not defined")
            return []
        path, paths = None, []
        if widget.appdata_text:
            start_path = tool.Appdata.get_path(widget.appdata_text)
        else:
            start_path = ""
        if isinstance(start_path, list):
            start_path = start_path[0]

        if widget.request_folder:
            path = QFileDialog.getExistingDirectory(widget, widget.name, start_path)

        elif widget.request_save:
            path = QFileDialog.getSaveFileName(widget, widget.name, start_path, widget.extension)[0]

        elif widget.single_request:
            path = QFileDialog.getOpenFileName(widget, widget.name, start_path, widget.extension)[0]

        elif all([widget, widget.name, widget.extension]):
            paths, _ = QFileDialog.getOpenFileNames(
                widget, widget.name, start_path, widget.extension
            )
        else:
            logging.warning(f"inputs are missing. no path requestable")
            return []

        if path is not None:
            paths = [path]

        if widget.appdata_text and widget.update_appdata:
            tool.Appdata.set_path(widget.appdata_text, paths)
        return paths

    @classmethod
    def autofill_path(cls, line_edit: QLineEdit, appdata: str):
        path = tool.Appdata.get_path(appdata)
        if path:
            if isinstance(path, list):
                path = OPTION_SEPERATOR.join(path)
            line_edit.setText(path)

    @classmethod
    def fill_main_property(
        cls,
        widget: ui.PropertySelector,
        pset_name: str,
        property_name: str,
        pset_placeholder: str = None,
        property_placeholder: str = None,
    ):
        widget.ui.le_pset_name.setText(pset_name)
        widget.ui.le_property_name.setText(property_name)
        if pset_placeholder is not None:
            widget.ui.le_pset_name.setPlaceholderText(pset_placeholder)
        if property_placeholder is not None:
            widget.ui.le_property_name.setPlaceholderText(property_placeholder)

    @classmethod
    def get_property(cls, widget: ui.PropertySelector):
        return widget.ui.le_pset_name.text(), widget.ui.le_property_name.text()

    @classmethod
    def fill_list_widget_with_checkstate(
        cls, list_widget: QListWidget, allowed_labels: list[str], all_labels: list[str]
    ):
        """
        Populate a QListWidget with items and set their check state based on allowed labels.

        :param list_widget: The QListWidget to be populated.
        :type list_widget: QListWidget
        :param allowed_labels: List of labels that should be checked.
        :type allowed_labels: list[str]
        :param all_labels: List of all labels to be added to the widget.
        :type all_labels: list[str]
        :return: None
        :rtype: None
        """
        list_widget.clear()
        list_widget.insertItems(0, sorted(all_labels))

        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if item.text() in allowed_labels:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

    @classmethod
    def create_completer(cls, texts, widget: QLineEdit | QComboBox | None = None):
        completer = QCompleter(set(texts))
        if widget is not None:
            widget.setCompleter(completer)
        return completer

    @classmethod
    def user_is_using_darkmode(cls):
        palette = QApplication.palette()
        return palette.color(QPalette.Window).lightness() < 128

    @classmethod
    def get_greyed_out_brush(cls):
        palette = QApplication.palette()
        return QBrush(palette.color(QPalette.ColorRole.PlaceholderText))
        if cls.user_is_using_darkmode():
            return QBrush(Qt.GlobalColor.lightGray)
        else:  # Light mode
            return QBrush(Qt.GlobalColor.darkGray)

    @classmethod
    def get_standard_text_brush(cls):
        palette = QApplication.palette()
        return QBrush(palette.color(QPalette.ColorRole.Text))

    @classmethod
    def insert_tab_order(cls, previous_widget: QWidget, inserted_widget: QWidget):
        old_element = previous_widget.nextInFocusChain()
        window = previous_widget.window()
        window.setTabOrder(previous_widget, inserted_widget)
        window.setTabOrder(inserted_widget, old_element)

    @classmethod
    def set_invalid(cls, widget: QWidget, invalid: bool) -> None:
        """
        invalidates style of widget (see install_validation_styles in main_window_widget.py)
        """
        widget.setProperty("invalid", invalid)
        cls._repolish_widget(widget)

        # Composite inputs like TagInput host the actual editor in `_edit`.
        # Propagate the flag so the QLineEdit gets the same invalid styling.
        embedded = getattr(widget, "_edit", None)
        if isinstance(embedded, QWidget):
            embedded.setProperty("invalid", invalid)
            cls._repolish_widget(embedded)

    @classmethod
    def _repolish_widget(cls, widget: QWidget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    @classmethod
    def set_valid(cls, widget: QWidget, valid: bool):
        cls.set_invalid(widget, not valid)

    @classmethod
    def get_clipboard_content(cls, seperator: str = None):
        def _data_to_text(d):
            raw = bytes(d)
            raw = raw.rstrip(b"\x00")

            for encoding in ("utf-8", "cp1252", "latin-1"):
                try:
                    return raw.decode(encoding)
                except UnicodeDecodeError:
                    pass

            # last resort: replace invalid characters
            return raw.decode("utf-8", errors="replace")

        def csv_to_list(data):
            csv_text = _data_to_text(data)
            return [line.split(";") for line in csv_text.splitlines()]

        content = QApplication.clipboard()
        md = content.mimeData()
        if md.hasFormat("csv"):
            return csv_to_list(md.data("csv"))

        plain_text = content.text()
        if seperator is None:
            return [plain_text]
        return plain_text.split(seperator)

    @classmethod
    def create_waiting_widget(cls, title="Waiting", parent_widget=None):
        waiting_worker, waiting_thread, waiting_widget = start_waiting_widget(
            parent_widget, title, ""
        )
        cls.get_properties().waiting_worker = waiting_worker
        cls.get_properties().waiting_thread = waiting_thread
        cls.get_properties().waiting_widget = waiting_widget
        return waiting_worker, waiting_thread, waiting_widget
