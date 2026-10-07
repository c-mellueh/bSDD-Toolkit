def register():
    pass


def activate():
    from bsdd_gui.plugins.modelcheck.core import window as core

    core.connect_to_main_window()


def deactivate():
    from bsdd_gui.plugins.modelcheck.core import window as core

    core.remove_main_menu_actions()


def retranslate_ui():
    from bsdd_gui.plugins.modelcheck.core import window as core

    core.retranslate_ui()


def on_new_project():
    from bsdd_gui.plugins.modelcheck.core import window as core

    core.on_new_project()
