# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PropertySelect.ui'
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
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QSizePolicy, QWidget


class Ui_Util(object):
    def setupUi(self, Util):
        if not Util.objectName():
            Util.setObjectName("Util")
        Util.resize(726, 40)
        self.horizontalLayout = QHBoxLayout(Util)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.le_pset_name = QLineEdit(Util)
        self.le_pset_name.setObjectName("le_pset_name")

        self.horizontalLayout.addWidget(self.le_pset_name)

        self.le_property_name = QLineEdit(Util)
        self.le_property_name.setObjectName("le_property_name")

        self.horizontalLayout.addWidget(self.le_property_name)

        self.retranslateUi(Util)

        QMetaObject.connectSlotsByName(Util)

    # setupUi

    def retranslateUi(self, Util):
        Util.setWindowTitle(QCoreApplication.translate("Util", "Form", None))
        self.le_pset_name.setPlaceholderText(
            QCoreApplication.translate("Util", "Ident PropertySet", None)
        )
        self.le_property_name.setPlaceholderText(
            QCoreApplication.translate("Util", "Ident Property", None)
        )

    # retranslateUi
