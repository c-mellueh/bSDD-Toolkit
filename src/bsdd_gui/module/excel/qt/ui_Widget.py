# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from bsdd_gui.module.loin.ui import Widget
from bsdd_gui.presets.ui_presets import FileSelector


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1600, 900)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.fw_output = FileSelector(Form)
        self.fw_output.setObjectName("fw_output")

        self.gridLayout.addWidget(self.fw_output, 4, 0, 1, 1)

        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.button_layout.addItem(self.horizontalSpacer_2)

        self.pb_create = QPushButton(Form)
        self.pb_create.setObjectName("pb_create")

        self.button_layout.addWidget(self.pb_create)

        self.gridLayout.addLayout(self.button_layout, 5, 0, 1, 1)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName("label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName("splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(6)
        self.loin = Widget(self.splitter)
        self.loin.setObjectName("loin")
        self.splitter.addWidget(self.loin)
        self.settings_widget = QWidget(self.splitter)
        self.settings_widget.setObjectName("settings_widget")
        self.verticalLayout = QVBoxLayout(self.settings_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.settings_widget)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 682, 761))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.main_settings = QFrame(self.scrollAreaWidgetContents_3)
        self.main_settings.setObjectName("main_settings")
        self.main_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.main_settings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_13 = QLabel(self.main_settings)
        self.label_13.setObjectName("label_13")
        self.label_13.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 2)

        self.verticalLayout_3.addWidget(self.main_settings)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout.addWidget(self.scrollArea_2)

        self.fr_download = QFrame(self.settings_widget)
        self.fr_download.setObjectName("fr_download")
        self.fr_download.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_download.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.fr_download)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 5)
        self.horizontalSpacer = QSpacerItem(
            1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pb_import = QToolButton(self.fr_download)
        self.pb_import.setObjectName("pb_import")
        self.pb_import.setMinimumSize(QSize(30, 30))
        self.pb_import.setMaximumSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pb_import)

        self.pb_export = QToolButton(self.fr_download)
        self.pb_export.setObjectName("pb_export")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pb_export.sizePolicy().hasHeightForWidth())
        self.pb_export.setSizePolicy(sizePolicy1)
        self.pb_export.setMinimumSize(QSize(30, 30))
        self.pb_export.setMaximumSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pb_export)

        self.verticalLayout.addWidget(self.fr_download)

        self.splitter.addWidget(self.settings_widget)

        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.pb_create.setText(QCoreApplication.translate("Form", "Create", None))
        self.label_3.setText(QCoreApplication.translate("Form", "Export:", None))
        self.label_13.setText(QCoreApplication.translate("Form", "**Settings**", None))
        # if QT_CONFIG(tooltip)
        self.pb_import.setToolTip(QCoreApplication.translate("Form", "Import", None))
        # endif // QT_CONFIG(tooltip)
        self.pb_import.setText("")
        # if QT_CONFIG(tooltip)
        self.pb_export.setToolTip(QCoreApplication.translate("Form", "Export", None))
        # endif // QT_CONFIG(tooltip)
        self.pb_export.setText("")

    # retranslateUi
