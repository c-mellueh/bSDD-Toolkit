# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
)
from PySide6.QtWidgets import QComboBox, QFormLayout, QLabel


class Ui_Settings(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName("Settings")
        Settings.resize(640, 40)
        self.formLayout = QFormLayout(Settings)
        self.formLayout.setObjectName("formLayout")
        self.label = QLabel(Settings)
        self.label.setObjectName("label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.comboBox = QComboBox(Settings)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName("comboBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox)

        self.retranslateUi(Settings)

        QMetaObject.connectSlotsByName(Settings)

    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", "Form", None))
        self.label.setText(QCoreApplication.translate("Settings", "Language", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Settings", "German", "de"))
        self.comboBox.setItemText(1, QCoreApplication.translate("Settings", "English", "en"))

    # retranslateUi
