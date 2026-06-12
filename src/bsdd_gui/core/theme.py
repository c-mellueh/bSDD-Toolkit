from __future__ import annotations

from typing import TYPE_CHECKING, Type

from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication
    from bsdd_gui import tool
    from bsdd_gui.module.theme import ui

SECTION = "theme"
MODE_OPTION = "mode"
DEFAULT_MODE = "system"


def apply_initial_theme(
    app: QApplication, theme: Type[tool.Theme], appdata: Type[tool.Appdata]
) -> None:
    """Apply the saved (or system) theme right after QApplication creation."""
    from bsdd_gui.module.theme import trigger

    mode = appdata.get_string_setting(SECTION, MODE_OPTION, DEFAULT_MODE)
    theme.set_mode(mode)
    theme.apply_theme(app, mode)
    theme.connect_color_scheme_signal(app, trigger.system_scheme_changed)


def system_scheme_changed(
    theme: Type[tool.Theme], main_window: Type[tool.MainWindowWidget]
) -> None:
    """Re-apply when the OS scheme flips and the user follows the system."""
    if theme.get_mode() != "system":
        return
    theme.apply_theme(main_window.get_app(), "system")


def settings_widget_created(widget: ui.SettingsWidget, theme: Type[tool.Theme]) -> None:
    theme.set_widget(widget)
    retranslate_ui(theme)


def settings_accepted(
    theme: Type[tool.Theme],
    appdata: Type[tool.Appdata],
    main_window: Type[tool.MainWindowWidget],
) -> None:
    widget = theme.get_widget()
    if widget is None:
        return
    mode = widget.ui.comboBox.currentData()
    if mode == theme.get_mode():
        return
    theme.set_mode(mode)
    appdata.set_setting(SECTION, MODE_OPTION, mode)
    theme.apply_theme(main_window.get_app(), mode)


def retranslate_ui(theme: Type[tool.Theme]) -> None:
    widget = theme.get_widget()
    if not widget:
        return
    widget.ui.retranslateUi(widget)
    combobox = widget.ui.comboBox
    combobox.clear()
    combobox.addItem(QCoreApplication.translate("Settings", "System default"), "system")
    combobox.addItem(QCoreApplication.translate("Settings", "Light"), "light")
    combobox.addItem(QCoreApplication.translate("Settings", "Dark"), "dark")
    current_mode = theme.get_mode()
    for index in range(combobox.count()):
        if combobox.itemData(index) == current_mode:
            combobox.setCurrentIndex(index)
