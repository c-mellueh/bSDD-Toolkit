from PySide6.QtCore import Qt

CLASS_REFERENCE = Qt.ItemDataRole.UserRole + 1
UMLAUT_DICT = {ord("ä"): "ae", ord("ü"): "ue", ord("ö"): "oe", ord("ß"): "ss"}
FILETYPE = "bSDD Project (*.json);;all (*.*)"
OPEN_PATH = "open_path"
SAVE_PATH = "save_path"
