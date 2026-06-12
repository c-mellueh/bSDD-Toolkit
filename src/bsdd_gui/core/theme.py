from __future__ import annotations

from typing import TYPE_CHECKING, Type

from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication
    from bsdd_gui import tool
    from bsdd_gui.module.theme import ui

SECTION = "theme"
MODE_OPTION = "mode"
ZOOM_OPTION = "view_zoom"
DEFAULT_MODE = "system"
DEFAULT_ZOOM = 100


def apply_initial_theme(
    app: QApplication, theme: Type[tool.Theme], appdata: Type[tool.Appdata]
) -> None:
    """Apply the saved (or system) theme right after QApplication creation."""
    from bsdd_gui.module.theme import trigger

    mode = appdata.get_string_setting(SECTION, MODE_OPTION, DEFAULT_MODE)
    theme.set_mode(mode)
    theme.set_view_zoom(appdata.get_int_setting(SECTION, ZOOM_OPTION, DEFAULT_ZOOM))
    theme.apply_theme(app, mode)
    theme.connect_color_scheme_signal(app, trigger.system_scheme_changed)
    theme.install_view_zoom_filter(app)


def change_view_zoom(
    steps: int,
    theme: Type[tool.Theme],
    appdata: Type[tool.Appdata],
    main_window: Type[tool.MainWindowWidget],
) -> None:
    from bsdd_gui.tool.theme import VIEW_ZOOM_STEP

    old_zoom = theme.get_view_zoom()
    theme.set_view_zoom(old_zoom + steps * VIEW_ZOOM_STEP)
    if theme.get_view_zoom() == old_zoom:
        return
    appdata.set_setting(SECTION, ZOOM_OPTION, theme.get_view_zoom())
    theme.apply_view_zoom(main_window.get_app())


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
    app = main_window.get_app()
    mode = widget.ui.comboBox.currentData()
    if mode != theme.get_mode():
        theme.set_mode(mode)
        appdata.set_setting(SECTION, MODE_OPTION, mode)
        theme.apply_theme(app, mode)
    zoom = widget.ui.spinBoxZoom.value()
    if zoom != theme.get_view_zoom():
        theme.set_view_zoom(zoom)
        appdata.set_setting(SECTION, ZOOM_OPTION, theme.get_view_zoom())
        theme.apply_view_zoom(app)


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
    widget.ui.spinBoxZoom.setValue(theme.get_view_zoom())
