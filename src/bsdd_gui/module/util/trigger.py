from bsdd_gui import tool
from bsdd_gui.core import util as core


def connect():
    pass


def on_new_project():
    pass


def fileselector_clicked(widget):
    core.filesector_clicked(widget, tool.Util)


def paint_file_selector(widget):
    core.update_file_selector(widget)


def main_property_selector_created(widget):
    core.fill_main_property_selector(widget, tool.Util, tool.Project)


def retranslate_ui():
    pass
