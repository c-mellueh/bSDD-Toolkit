from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict
from PySide6.QtCore import Signal, QCoreApplication, QObject, QThread, Qt
from openpyxl import styles
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from bsdd_json.utils import class_utils, property_utils, dictionary_utils
from openpyxl.utils import get_column_letter
import openpyxl

from bsdd_json import BsddClass, BsddDictionary, BsddClassProperty
import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool, FieldSignals
from bsdd_gui.module.excel import ui, trigger, constants
from openpyxl.worksheet.table import Table, TableStyleInfo


class PsetDict(TypedDict):
    checked: bool
    properties: dict[str, bool]


class BasicSettingsDict(TypedDict):
    inherit: bool
    classification: bool
    type_objects: bool
    main_pset: str
    main_property: str


class SettingsDict(TypedDict):
    class_settings: dict[str, bool]
    property_settings: dict[str, dict[str, PsetDict]]
    settings: BasicSettingsDict


if TYPE_CHECKING:
    from bsdd_gui.module.revit_export.prop import RevitExportProperties


class Signals(FieldSignals):
    pass


class RevitExport(ActionTool, FieldTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> RevitExportProperties:
        return bsdd_gui.RevitExportProperties

    @classmethod
    def _get_widget_class(cls) -> type[ui.Widget]:
        return ui.Widget

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def create_widget(cls, *args, **kwargs) -> ui.Widget:
        widget = cls._get_widget_class()(*args, **kwargs)
        cls.add_plugins_to_widget(widget)
        return widget

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.Widget):
        widget.pb_import.clicked.connect(lambda: trigger.import_settings(widget))
        widget.pb_export.clicked.connect(lambda: trigger.export_settings(widget))
        widget.pb_create.clicked.connect(lambda _, w=widget: trigger.export(w))
        super().connect_widget_signals(widget)

    @classmethod
    def create_build_thread(
        cls,
        bsdd_dict: BsddDictionary,
        checked_classes: dict[str, bool],
        checked_properties: PsetDict,
        out_path: str,
    ):
        class _BuildWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                    bsdd_classes = [c for c in checked_classes if c.ClassType == "Class"]
                    root_classes = [c for c in bsdd_classes if not c.ParentClassCode]
                    pass

                except Exception as exc:  # pragma: no cover - pass through
                    self.error.emit(exc)

        build_worker = _BuildWorker()
        cls.get_properties().build_worker = build_worker
        build_thread = QThread()

        cls.get_properties().build_thread = build_thread

        build_worker.moveToThread(build_thread)
        build_worker.finished.connect(build_thread.quit)
        build_worker.finished.connect(build_worker.deleteLater)
        build_worker.error.connect(build_thread.quit)
        build_worker.error.connect(build_worker.deleteLater)
        build_thread.finished.connect(build_thread.deleteLater)
        build_thread.started.connect(build_worker.run, Qt.ConnectionType.QueuedConnection)
        return build_worker, build_thread
