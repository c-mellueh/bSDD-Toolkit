import os

from PySide6.QtGui import QIcon


def get_switch_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["switch"])
    return QIcon(icon_path)


def get_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["icon"])
    return QIcon(icon_path)


def get_settings_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["settings"])
    return QIcon(icon_path)


def get_link_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["link"])
    return QIcon(icon_path)


def get_reload_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["reload"])
    return QIcon(icon_path)


def get_add_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["add"])
    return QIcon(icon_path)


def get_search_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["search"])
    return QIcon(icon_path)


def get_download_icon() -> QIcon:
    icon_path = os.path.join(ICON_PATH, ICON_DICT["download"])
    return QIcon(icon_path)


ICON_PATH = os.path.dirname(__file__)
ICON_DICT = {
    "icon": "icon.ico",
    "link": "link.png",
    "reload": "reload.svg",
    "search": "search.png",
    "settings": "setting.png",
    "add": "add.png",
    "switch": "switch.png",
    "download": "download.png",
}
