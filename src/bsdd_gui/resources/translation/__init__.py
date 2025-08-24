import os

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

translator = QTranslator()


def load_language(application: QApplication, language="en"):
    global translator
    base_path = os.path.dirname(__file__)
    application.removeTranslator(translator)

    locale = QLocale(language)
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator(application)
    if translator.load(locale, "qtbase", "_", path):
        application.installTranslator(translator)

    path = os.path.join(base_path, f"translation_{language}.qm")
    translator = QTranslator(application)
    if translator.load(path):
        application.installTranslator(translator)
