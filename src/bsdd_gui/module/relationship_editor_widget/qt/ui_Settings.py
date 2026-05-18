# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Settings.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
)
from PySide6.QtWidgets import QFormLayout, QLabel

from bsdd_gui.presets.ui_presets import ToggleSwitch


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(400, 49)
        self.formLayout = QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.label = QLabel(Form)
        self.label.setObjectName("label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.checkBox = ToggleSwitch(Form)
        self.checkBox.setObjectName("checkBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.checkBox)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.label.setText(QCoreApplication.translate("Form", "Allow Unknown URIs", None))

    # retranslateUi
