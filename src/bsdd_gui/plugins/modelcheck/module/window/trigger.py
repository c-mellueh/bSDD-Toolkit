from bsdd_gui.plugins.modelcheck.core import window as core


def activate():
    core.connect_to_main_window()


def deactivate():
    core.remove_main_menu_actions()


def retranslate_ui():
    core.retranslate_ui()


def on_new_project():
    core.on_new_project()
