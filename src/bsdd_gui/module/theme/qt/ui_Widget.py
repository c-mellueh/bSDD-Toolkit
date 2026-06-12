# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import QComboBox, QFormLayout, QLabel, QSpinBox


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

        self.labelZoom = QLabel(ThemeSettings)
        self.labelZoom.setObjectName("labelZoom")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelZoom)

        self.spinBoxZoom = QSpinBox(ThemeSettings)
        self.spinBoxZoom.setObjectName("spinBoxZoom")
        self.spinBoxZoom.setMinimum(50)
        self.spinBoxZoom.setMaximum(300)
        self.spinBoxZoom.setSingleStep(10)
        self.spinBoxZoom.setValue(100)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinBoxZoom)

        self.retranslateUi(ThemeSettings)

        QMetaObject.connectSlotsByName(ThemeSettings)

    # setupUi

    def retranslateUi(self, ThemeSettings):
        ThemeSettings.setWindowTitle(QCoreApplication.translate("ThemeSettings", "Form", None))
        self.label.setText(QCoreApplication.translate("ThemeSettings", "Color theme", None))
        self.labelZoom.setText(QCoreApplication.translate("ThemeSettings", "View zoom", None))
        self.spinBoxZoom.setSuffix(QCoreApplication.translate("ThemeSettings", " %", None))
        # if QT_CONFIG(tooltip)
        self.spinBoxZoom.setToolTip(
            QCoreApplication.translate(
                "ThemeSettings",
                "Text size of trees and tables. Ctrl + mouse wheel over a view also zooms.",
                None,
            )
        )


# endif // QT_CONFIG(tooltip)
# retranslateUi
