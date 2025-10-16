from __future__ import annotations
from PySide6.QtCore import QCoreApplication
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from bsdd_gui import tool

def connect_to_main_window(
    ids_exporter: Type[tool.IdsExporter], main_window: Type[tool.MainWindowWidget],project:Type[tool.Project]
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action(None, "Ids Exporter", lambda: ids_exporter.build_ids(project.get()))
    ids_exporter.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    ids_exporter: Type[tool.IdsExporter], main_window: Type[tool.MainWindowWidget]
):
    action = ids_exporter.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("GraphView", "Graph View"))