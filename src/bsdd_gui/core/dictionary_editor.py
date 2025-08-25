from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QCloseEvent

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.dictionary_editor import ui


def connect_widget(widget: ui.DictionaryEditor, dictionary_editor: Type[tool.DictionaryEditor]):
    dictionary_editor.register_widget(widget)
    dictionary_editor.fill_dictionary_widget(widget)
    dictionary_editor.color_required_fields(widget)


def create_main_menu_actions(
    dictionary_editor: Type[tool.DictionaryEditor],
    main_window: Type[tool.MainWindow],
) -> None:
    action = main_window.add_action(
        "menuEdit", "Dictionary Settings", dictionary_editor.signaller.window_requested.emit
    )
    dictionary_editor.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    dictionary_editor: Type[tool.DictionaryEditor],
    main_window: Type[tool.MainWindow],
    util: Type[tool.Util],
):
    """Retranslates the UI elements of dictionary Editor. and the Actions."""
    action = dictionary_editor.get_action(main_window.get(), "open_window")
    text = QCoreApplication.translate("DictionaryEditor", "Dictionary Settings")
    action.setText(text)
    title = util.get_window_title(
        QCoreApplication.translate("DictionaryEditor", " bSDD-Dictionary")
    )
    for widget in dictionary_editor.get_widgets():
        widget.setWindowTitle(title)


def connect_signals(
    dictionary_editor: Type[tool.DictionaryEditor],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindow],
    util: Type[tool.Util],
):
    def create_window():
        if dictionary_editor.get_widgets():
            widget = list(dictionary_editor.get_widgets())[0]
        else:
            widget = dictionary_editor.create_widget()
            dictionary_editor.register_widget(widget)
            bsdd_dictionary = project.get()
            dictionary_editor.set_dictionary_values(widget, bsdd_dictionary.model_dump())
            widget.value_changed.connect(
                lambda n, v: dictionary_editor.update_dictionary_value(bsdd_dictionary, n, v)
            )
            dictionary_editor.register_widget(widget)
            widget.setParent(main_window.get())
            widget.setWindowFlags(Qt.Tool)
            retranslate_ui(dictionary_editor, main_window, util)

        widget.show()
        widget.raise_()
        widget.activateWindow()
        widget.setFocus()

    dictionary_editor.signaller.window_requested.connect(create_window)


def remove_widget(
    widget: ui.DictionaryEditor,
    event: QCloseEvent,
    dictionary_editor: Type[tool.DictionaryEditor],
    popups: Type[tool.Popups],
):
    if not dictionary_editor.all_inputs_are_valid(widget):
        event.ignore()
        text = QCoreApplication.translate("Project", "Required Inputs are missing!")
        missing_text = QCoreApplication.translate("Project", "is mssing")
        missing_inputs = dictionary_editor.get_missing_inputs(widget)
        popups.create_warning_popup(
            f" {missing_text}\n".join(missing_inputs) + f" {missing_text}", None, text
        )
    else:
        dictionary_editor.unregister_widget(widget)
        event.accept()
