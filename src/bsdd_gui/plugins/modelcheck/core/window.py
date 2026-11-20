import os

import ifcopenshell
from PySide6.QtWidgets import QMessageBox

from bsdd_gui import tool
from bsdd_gui.plugins.modelcheck.core.modelcheck import check_element
from bsdd_gui.plugins.modelcheck.core.results import create_bcf_report, create_excel_report
from bsdd_gui.plugins.modelcheck.module.window import prop, ui
from bsdd_gui.plugins.modelcheck.tool.modelcheck import Modelcheck
from bsdd_gui.plugins.modelcheck.tool.window import Window


def connect_to_main_window():
    main_win = tool.MainWindowWidget.get()
    if main_win is None:
        return
    action = tool.MainWindowWidget.add_action(None, "Modelcheck", open_window)
    Window.set_action("open_window", action)


def remove_main_menu_actions():
    action = Window.get_action("open_window")
    if action:
        tool.MainWindowWidget.remove_action(None, action)


def open_window():
    win = Window.get_window()
    dictionary = tool.Project.get()
    Window.populate_class_tree(dictionary)
    win.run_clicked.connect(run_check)
    win.show()


def on_new_project():
    win = Window.get_window()
    dictionary = tool.Project.get()
    Window.populate_class_tree(dictionary)


def retranslate_ui():
    win = Window.get_window()
    if win:
        win.retranslateUi(win)


def run_check():
    win = Window.get_window()
    ifc_path = win.ifc_input.text().strip()
    export_path = win.export_input.text().strip()
    main_pset = win.pset_input.text().strip()
    main_prop = win.prop_input.text().strip()

    if not ifc_path or not os.path.exists(ifc_path):
        QMessageBox.warning(win, "Invalid File", "Please select a valid IFC file.")
        return
    if not export_path:
        QMessageBox.warning(win, "Invalid Path", "Please specify an Excel export file path.")
        return

    win.status_label.setText("Opening IFC file...")
    win.progress_bar.setVisible(True)
    win.progress_bar.setValue(10)
    win.run_button.setEnabled(False)

    try:
        ifc_file = ifcopenshell.open(ifc_path)
    except Exception as exc:
        QMessageBox.critical(win, "Error", f"Failed to open IFC: {exc}")
        win.run_button.setEnabled(True)
        return

    dictionary = tool.Project.get()
    class_map = {}
    if dictionary and getattr(dictionary, 'Classes', None):
        for item in dictionary.Classes:
            class_map[item.Code] = item
            class_map[item.Name] = item

    entities = ifc_file.by_type("IfcElement")
    total = len(entities)
    issues = []

    win.status_label.setText(f"Checking {total} elements...")
    win.progress_bar.setValue(20)

    for idx, el in enumerate(entities):
        matched_class = None
        if main_pset and main_prop:
            psets = Modelcheck.extract_psets(el)
            ident_val = psets.get(main_pset, {}).get(main_prop)
            if ident_val and ident_val in class_map:
                matched_class = class_map[ident_val]

        if not matched_class:
            el_type = el.is_a()
            if el_type in class_map:
                matched_class = class_map[el_type]

        if matched_class:
            check_element(el, matched_class, issues)

        if total > 0 and idx % 25 == 0:
            pct = 20 + int((idx / total) * 70)
            win.progress_bar.setValue(pct)

    win.status_label.setText("Writing report...")
    win.progress_bar.setValue(95)
    export_ext = os.path.splitext(export_path)[1].lower()
    if export_ext == ".bcf":
        create_bcf_report(issues, export_path)
    else:
        create_excel_report(issues, export_path)

    win.progress_bar.setValue(100)
    win.status_label.setText(f"Done! {len(issues)} issues found.")
    msg = "Modelcheck finished!\n\nChecked " + str(total) + " elements.\nFound " + str(len(issues)) + " issues.\nReport saved to: " + export_path
    QMessageBox.information(win, "Modelcheck Complete", msg)
    win.run_button.setEnabled(True)
