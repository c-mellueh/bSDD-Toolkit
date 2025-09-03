from __future__ import annotations

from typing import TYPE_CHECKING, Type

from PySide6.QtCore import Qt

from bsdd_gui.module.project.constants import UMLAUT_DICT
from bsdd_gui.module.search_widget.constants import SEARCH_SECTION, STRICT_SETTING

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.search_widget.ui import SearchDialog


def connect_signals(search: Type[tool.Search]):
    search.connect_signals()


def set_strict_state(state: bool, appdata: Type[tool.Appdata]):
    appdata.set_setting(SEARCH_SECTION, STRICT_SETTING, state)


def update_filter_table(dialog: SearchDialog, search: Type[tool.Search]):
    """
    filters output Table to search_text
    :param search: Tool
    :param dialog: search Dialog
    :return:
    """
    threshold = search.get_threshold()
    table_widget = search.get_table(dialog)
    search_text = search.get_search_text(dialog)
    search_mode = search.get_search_mode(dialog)

    search_text = search_text.translate(UMLAUT_DICT)  # Tanslate Umlauts (ä->ae, ö->oe etc..)
    table_widget.setSortingEnabled(False)  # disable sorting
    # Hide match score column
    last_column_index = table_widget.columnCount() - 1
    table_widget.hideColumn(last_column_index)

    # Hide all Rows which match-score < threshold
    for row in range(table_widget.rowCount()):
        match_score = search.get_row_matchscore(dialog, search_text, row, last_column_index)
        if match_score > threshold:
            table_widget.showRow(row)
        else:
            table_widget.hideRow(row)

    # sort by match score
    table_widget.setSortingEnabled(True)
    table_widget.sortByColumn(last_column_index, Qt.SortOrder.DescendingOrder)
    table_widget.resizeColumnsToContents()


def save_selected_element(dialog: SearchDialog, search: Type[tool.Search]):
    item = search.get_selected_item(dialog)
    dialog.return_value = search.get_info_from_item(item)
    dialog.accept()


def retranslate_ui(search: Type[tool.Search]):
    """
    Retranslate the Search Widget
    :return:
    """
    for dialog in search.get_widgets():
        dialog.ui.retranslateUi(dialog)
        update_filter_table(dialog, search)
        search.retranslate_title(dialog, search.get_search_mode(dialog))
