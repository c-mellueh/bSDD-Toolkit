# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QComboBox, QFormLayout, QLabel


class Ui_ThemeSettings(object):
    def setupUi(self, ThemeSettings):
        if not ThemeSettings.objectName():
            ThemeSettings.setObjectName("ThemeSettings")
        ThemeSettings.resize(640, 40)
        self.formLayout = QFormLayout(ThemeSettings)
        self.formLayout.setObjectName("formLayout")
        self.label = QLabel(ThemeSettings)
        self.label.setObjectName("label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.comboBox = QComboBox(ThemeSettings)
        self.comboBox.setObjectName("comboBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)

        self.retranslateUi(ThemeSettings)

        QMetaObject.connectSlotsByName(ThemeSettings)

    # setupUi

    def retranslateUi(self, ThemeSettings):
        ThemeSettings.setWindowTitle(QCoreApplication.translate("ThemeSettings", "Form", None))
        self.label.setText(QCoreApplication.translate("ThemeSettings", "Color theme", None))

    # retranslateUi
