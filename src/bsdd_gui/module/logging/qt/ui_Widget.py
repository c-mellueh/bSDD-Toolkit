# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import QApplication, QComboBox, QFormLayout, QLabel, QSizePolicy, QWidget

from bsdd_gui.module.util.ui import FileSelector


class Ui_Logging(object):
    def setupUi(self, Logging):
        if not Logging.objectName():
            Logging.setObjectName("Logging")
        Logging.resize(640, 102)
        self.formLayout = QFormLayout(Logging)
        self.formLayout.setObjectName("formLayout")
        self.label = QLabel(Logging)
        self.label.setObjectName("label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.comboBox = QComboBox(Logging)
        self.comboBox.setObjectName("comboBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)

        self.widget_export = FileSelector(Logging)
        self.widget_export.setObjectName("widget_export")
        self.widget_export.setMinimumSize(QSize(0, 50))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.widget_export)

        self.retranslateUi(Logging)

        QMetaObject.connectSlotsByName(Logging)

    # setupUi

    def retranslateUi(self, Logging):
        Logging.setWindowTitle(QCoreApplication.translate("Logging", "Form", None))
        self.label.setText(QCoreApplication.translate("Logging", "Log Level:", None))

    # retranslateUi
