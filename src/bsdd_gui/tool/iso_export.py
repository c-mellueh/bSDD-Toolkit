from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict
import logging
from PySide6.QtCore import Signal, QCoreApplication,QObject,QThread,Qt
from openpyxl import styles
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from bsdd_json.utils import class_utils, property_utils, dictionary_utils
from openpyxl.utils import get_column_letter
import openpyxl

from bsdd_json import BsddClass, BsddDictionary, BsddClassProperty
import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool, FieldSignals
from bsdd_gui.module.iso_export import ui, trigger,constants
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
    from bsdd_gui.module.iso_export.prop import IsoExportProperties


class Signals(FieldSignals):
    pass


class IsoExport(ActionTool, FieldTool):
    signals = Signals()
    @classmethod
    def get_properties(cls) -> IsoExportProperties:
        return bsdd_gui.IsoExportProperties

    @classmethod
    def _get_widget_class(cls) -> type[ui.Widget]:
        return ui.Widget

    @classmethod
    def request_widget(cls, *args, **kwargs):
        return super().request_widget(*args, **kwargs)

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
    def draw_class(
        cls,
        bsdd_class: BsddClass,
        start_row: int,
        start_column: int,
        sheet: Worksheet,
        property_filter: dict[str,PsetDict],
        bsdd_dictionary: BsddDictionary,
    ):
        sheet.cell(start_row, start_column, QCoreApplication.translate("IsoExport", "Name"))
        sheet.cell(start_row, start_column + 1, bsdd_class.Name)
        sheet.cell(start_row, start_column + 2, QCoreApplication.translate("IsoExport", "Parent Code"))
        sheet.cell(start_row, start_column + 3, bsdd_class.ParentClassCode or "")

        sheet.cell(start_row + 1, start_column, QCoreApplication.translate("IsoExport", "Identifier"))
        sheet.cell(start_row + 1, start_column + 1, bsdd_class.Code)

        sheet.cell(start_row + 2, start_column, QCoreApplication.translate("IsoExport", "Definition"))
        sheet.cell(start_row + 2, start_column + 1, bsdd_class.Definition)
        sheet.cell(start_row + 2, start_column + 5, " ")

        sheet.cell(start_row + 3, start_column, QCoreApplication.translate("IsoExport", "Property"))
        sheet.cell(
            start_row + 3, start_column + 1, QCoreApplication.translate("IsoExport", "PropertySet")
        )
        sheet.cell(
            start_row + 3, start_column + 2, QCoreApplication.translate("IsoExport", "Definition")
        )
        sheet.cell(start_row + 3, start_column + 3, QCoreApplication.translate("IsoExport", "Datatype"))
        sheet.cell(start_row + 3, start_column + 4, QCoreApplication.translate("IsoExport", "Values"))

        cls.draw_border(sheet, (start_row, start_row + 2), (start_column, start_column + 4))
        cls.fill_grey(sheet, (start_row, start_row + 2), (start_column, start_column + 4))

        start_row += 3
        row = 0

        def is_active(bsdd_property:BsddClassProperty):
            pset_data = property_filter.get(bsdd_property.PropertySet)
            if not pset_data:
                return True
            if not pset_data.get("checked",True):
                return False
            return pset_data.get("properties",{}).get(bsdd_property.Code,True)

        bsdd_properties = sorted([p for p in bsdd_class.ClassProperties if is_active(p)],key=lambda p:p.PropertySet)

        for row, bsdd_property in enumerate(bsdd_properties, start=1):
            name = property_utils.get_name(bsdd_property, bsdd_dictionary)
            definition = property_utils.get_definition(bsdd_property, bsdd_dictionary)
            data_type = property_utils.get_data_type(bsdd_property) or "IFCLABEL"
            values = [v.Code for v in property_utils.get_values(bsdd_property)]

            sheet.cell(start_row + row, start_column, name)
            sheet.cell(start_row + row, start_column + 1, bsdd_property.PropertySet)
            sheet.cell(start_row + row, start_column + 2, definition)
            sheet.cell(start_row + row, start_column + 3, data_type)
            sheet.cell(start_row + row, start_column + 4, "; ".join(values))
            sheet.cell(start_row + row, start_column + 5, " ")

        cls.create_table(
            (start_row, start_row + row), (start_column, start_column + 4), sheet, bsdd_class.Name
        )
        return start_row + row

    @classmethod
    def get_all_children(
        cls, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary
    ) -> list[BsddClass]:
        result = []
        queue = class_utils.get_children(bsdd_class, bsdd_dictionary)
        while queue:
            child = queue.pop(0)
            result.append(child)
            queue.extend(class_utils.get_children(child, bsdd_dictionary))
        return result

    @classmethod
    def get_settings(cls, widget: ui.Widget) -> BasicSettingsDict:

        settings_dict = {
            # "inherit": widget.cb_inh.isChecked(),
            # "classification": widget.cb_clsf.isChecked(),
            # "type_objects": widget.cb_type_objects.isChecked(),
            # "main_pset": widget.cb_pset.currentText(),
            # "main_property": widget.cb_prop.currentText(),
            # "datatype": widget.cb_datatype.currentText(),
            # "datatype_mapping": cls.get_datatype_mapping(widget),
        }
        return settings_dict

    @classmethod
    def set_settings(cls, widget: ui.Widget, settings_dict: BasicSettingsDict):
        pass


    @classmethod
    def draw_border(
        cls, sheet: Worksheet, row_range: tuple[int, int], column_range: tuple[int, int]
    ):
        for row in range(row_range[0], row_range[1] + 1):
            for column in range(column_range[0], column_range[1] + 1):
                left_side = styles.Side(border_style="none", color="FF000000")
                right_side = styles.Side(border_style="none", color="FF000000")
                top_side = styles.Side(border_style="none", color="FF000000")
                bottom_side = styles.Side(border_style="none", color="FF000000")
                if column == column_range[0]:
                    left_side = styles.Side(border_style="thick", color="FF000000")

                if column == column_range[1]:
                    right_side = styles.Side(border_style="thick", color="FF000000")

                if row == row_range[0]:
                    top_side = styles.Side(border_style="thick", color="FF000000")
                if row == row_range[1]:
                    bottom_side = styles.Side(border_style="thick", color="FF000000")
                sheet.cell(row, column).border = styles.Border(
                    left=left_side, right=right_side, top=top_side, bottom=bottom_side
                )

    @classmethod
    def fill_grey(cls, sheet: Worksheet, row_range: tuple[int, int], column_range: tuple[int, int]):
        fill = styles.PatternFill(fill_type="solid", start_color="d9d9d9")
        for row in range(row_range[0], row_range[1] + 1):
            for column in range(column_range[0], column_range[1] + 1):
                sheet.cell(row, column).fill = fill

    @classmethod
    def autoadjust_column_widths(cls, sheet: Worksheet, extra_width=0) -> None:
        for i in range(len(list(sheet.columns))):
            column_letter = get_column_letter(i + 1)
            column = sheet[column_letter]
            width = (
                max(
                    [len(cell.value) for cell in column if cell.value is not None],
                    default=2,
                )
                + extra_width
            )
            sheet.column_dimensions[column_letter].width = width

    @classmethod
    def create_table(
        cls, row_range: tuple[int, int], column_range: tuple[int, int], sheet: Worksheet, name
    ):
        name = dictionary_utils.slugify(name,delimiter="_")
        table_range = f"{sheet.cell(row_range[0], column_range[0]).coordinate}:{sheet.cell(row_range[1], column_range[1]).coordinate}"
        table = Table(displayName=name, ref=table_range)
        style = TableStyleInfo(
            name=constants.TABLE_STYLE,
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        table.tableStyleInfo = style
        sheet.add_table(table)
        # cls.autoadjust_column_widths(sheet, 5)

    @classmethod
    def create_class_sheet(cls,root_class:BsddClass,bsdd_dict:BsddDictionary,workbook:Workbook,class_settings:dict,property_settings:dict):
        classes = [root_class]
        property_dict = property_settings.get(root_class.Code,{})
        class_sheet = workbook.create_sheet(root_class.Name)
        row, column = 1,1
        max_row = 0
        max_row = cls.draw_class(root_class,row,column,class_sheet,property_dict,bsdd_dict)
        items_in_row = 1
        column +=constants.COLUMN_COUNT

        for child in cls.get_all_children(root_class,bsdd_dict):
            if not class_settings.get(child.Code,True):
                continue

            classes.append(child)
            property_dict = property_settings.get(child.Code,{})

            bottom_row = cls.draw_class(child,row,column,class_sheet,property_dict,bsdd_dict)
            column +=constants.COLUMN_COUNT
            max_row = bottom_row if bottom_row > max_row else max_row
            items_in_row +=1

            if items_in_row > constants.MAX_ENTRIES:
                column = 1
                row = max_row+2
                items_in_row = 0
        return classes
    
    @classmethod
    def create_overview_sheet(cls,classes:list[BsddClass],sheet:Worksheet):
        sheet.title = QCoreApplication.translate("IsoExport","Overview")
        sheet.cell(1,1,"Code")
        sheet.cell(1,2,"Name")
        sheet.cell(1,3,"Definition")
        row = 2
        for row,bsdd_class in enumerate(classes,start=2):
            sheet.cell(row,1,bsdd_class.Code)
            sheet.cell(row,2,bsdd_class.Name)
            sheet.cell(row,3,bsdd_class.Definition)
        cls.create_table((1,row),(1,3),sheet,sheet.title)

    @classmethod
    def create_build_thread(
        cls,
        bsdd_dict: BsddDictionary,
        class_settings: dict[str, bool],
        property_settings: PsetDict,
        out_path:str
    ):
        class _BuildWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                   #TODO: Add Functions
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