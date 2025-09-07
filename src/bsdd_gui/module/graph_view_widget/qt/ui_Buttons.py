# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Buttons.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(186, 155)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.bt_start_stop = QPushButton(Form)
        self.bt_start_stop.setObjectName(u"bt_start_stop")

        self.gridLayout.addWidget(self.bt_start_stop, 2, 0, 1, 1)

        self.bt_clear = QPushButton(Form)
        self.bt_clear.setObjectName(u"bt_clear")

        self.gridLayout.addWidget(self.bt_clear, 1, 0, 1, 1)

        self.bt_center = QPushButton(Form)
        self.bt_center.setObjectName(u"bt_center")

        self.gridLayout.addWidget(self.bt_center, 3, 0, 1, 1)

        self.bt_load = QPushButton(Form)
        self.bt_load.setObjectName(u"bt_load")

        self.gridLayout.addWidget(self.bt_load, 1, 1, 1, 1)

        self.titleLabel = QLabel(Form)
        self.titleLabel.setObjectName(u"titleLabel")

        self.gridLayout.addWidget(self.titleLabel, 0, 0, 1, 1)

        self.bt_import = QPushButton(Form)
        self.bt_import.setObjectName(u"bt_import")

        self.gridLayout.addWidget(self.bt_import, 2, 1, 1, 1)

        self.bt_export = QPushButton(Form)
        self.bt_export.setObjectName(u"bt_export")

        self.gridLayout.addWidget(self.bt_export, 3, 1, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.bt_start_stop.setText(QCoreApplication.translate("Form", u"Stop", None))
        self.bt_clear.setText(QCoreApplication.translate("Form", u"Clear", None))
        self.bt_center.setText(QCoreApplication.translate("Form", u"Center", None))
        self.bt_load.setText(QCoreApplication.translate("Form", u"Load", None))
        self.titleLabel.setText(QCoreApplication.translate("Form", u"Actions", None))
        self.bt_import.setText(QCoreApplication.translate("Form", u"Import", None))
        self.bt_export.setText(QCoreApplication.translate("Form", u"Export", None))
    # retranslateUi

