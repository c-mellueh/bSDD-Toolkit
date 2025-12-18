from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClassProperty, BsddProperty
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor
import uuid
from bsdd_gui.module.download import constants
from bsdd_json.utils import dictionary_utils

if TYPE_CHECKING:
    from bsdd_gui import tool as tool
    from bsdd_gui.module.download import ui


def connect_signals(download_widget: Type[tool.Download]):
    download_widget.connect_internal_signals()


def connect_to_main_window(
    download_widget: Type[tool.Download],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
) -> None:
    action = main_window.add_action(
        "menuData",
        "Download bSDD",
        lambda: download_widget.request_widget(str(uuid.uuid4()), main_window.get()),
    )
    download_widget.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    download_widget: Type[tool.Download],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    """Retranslates the UI elements of dictionary Editor. and the Actions."""
    action = download_widget.get_action(main_window.get(), "open_window")
    if not action:
        return
    text = QCoreApplication.translate("Download", "Download bSDD")
    action.setText(text)
    title = util.get_window_title(QCoreApplication.translate("Download", "Download bSDD"))
    for widget in download_widget.get_widgets():
        widget.setWindowTitle(title)


def create_widget(data, parent, download_widget: Type[tool.Download]):
    download_widget.show_widget(None, parent)


def register_widget(widget: ui.DownloadWidget, download_widget: Type[tool.Download]):
    download_widget.register_widget(widget)


def register_fields(
    widget: ui.DownloadWidget, download_widget: Type[tool.Download], appdata: Type[tool.Appdata]
):
    le_widget = widget.le_uri
    download_widget.register_field_getter(
        widget,
        le_widget,
        lambda _: appdata.get_string_setting(constants.DOWNLAOD_APPDATA, constants.URI),
    )
    download_widget.register_field_setter(
        widget,
        le_widget,
        lambda _, v: appdata.set_setting(constants.DOWNLAOD_APPDATA, constants.URI, v),
    )
    download_widget.register_field_listener(widget, le_widget)
    
    le_path = widget.fs_save_path.line_edit
    download_widget.register_field_getter(
        widget,
        le_path,
        lambda _: appdata.get_string_setting(constants.DOWNLAOD_APPDATA, constants.SAVE_PATH),
    )
    download_widget.register_field_setter(
        widget,
        le_path,
        lambda _, v: appdata.set_setting(constants.DOWNLAOD_APPDATA, constants.SAVE_PATH, v),
    )
    download_widget.register_field_listener(widget, le_path)
    download_widget.sync_from_model(widget, None)


def register_validators(
    widget: ui.DownloadWidget, download_widget: Type[tool.Download], util: Type[tool.Util]
):
    download_widget.add_validator(
        widget,
        widget.le_uri,
        lambda v, w,: dictionary_utils.is_uri(v),
        lambda w, v: util.set_invalid(w, not v),
    )


def connect_widget(widget: ui.DownloadWidget, download_widget: Type[tool.Download]):
    download_widget.connect_widget_signals(widget)


def download_dictionary(widget: ui.DownloadWidget, download_widget: Type[tool.Download]):
    download_widget.sync_to_model(widget,None)
    bsdd_uri = widget.le_uri.text()
    save_path = widget.fs_save_path.get_path()
    download_widget.reset_done_count()
    bsdd_dictionary = download_widget.import_dictionary(bsdd_uri)
    download_widget.set_bsdd_dictionary(bsdd_dictionary)

    download_widget.get_all_classes(widget, bsdd_uri, bsdd_dictionary)
    download_widget.get_all_properties(widget, bsdd_uri)
