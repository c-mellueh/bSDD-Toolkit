# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSplitter, QToolButton,
    QVBoxLayout, QWidget)

from bsdd_gui.module.loin.ui import Widget
from bsdd_gui.presets.ui_presets import FileSelector

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1600, 900)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.fw_output = FileSelector(Form)
        self.fw_output.setObjectName(u"fw_output")

        self.gridLayout.addWidget(self.fw_output, 4, 0, 1, 1)

        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.button_layout.addWidget(self.label)

        self.cb_format = QComboBox(Form)
        self.cb_format.addItem("")
        self.cb_format.addItem("")
        self.cb_format.setObjectName(u"cb_format")

        self.button_layout.addWidget(self.cb_format)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.button_layout.addItem(self.horizontalSpacer_2)

        self.pb_create = QPushButton(Form)
        self.pb_create.setObjectName(u"pb_create")

        self.button_layout.addWidget(self.pb_create)


        self.gridLayout.addLayout(self.button_layout, 5, 0, 1, 1)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(6)
        self.loin = Widget(self.splitter)
        self.loin.setObjectName(u"loin")
        self.splitter.addWidget(self.loin)
        self.settings_widget = QWidget(self.splitter)
        self.settings_widget.setObjectName(u"settings_widget")
        self.verticalLayout = QVBoxLayout(self.settings_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.settings_widget)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 682, 761))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.main_settings = QFrame(self.scrollAreaWidgetContents_3)
        self.main_settings.setObjectName(u"main_settings")
        self.main_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.main_settings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_13 = QLabel(self.main_settings)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 2)


        self.verticalLayout_3.addWidget(self.main_settings)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout.addWidget(self.scrollArea_2)

        self.fr_download = QFrame(self.settings_widget)
        self.fr_download.setObjectName(u"fr_download")
        self.fr_download.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_download.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.fr_download)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 5)
        self.horizontalSpacer = QSpacerItem(1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pb_import = QToolButton(self.fr_download)
        self.pb_import.setObjectName(u"pb_import")
        self.pb_import.setMinimumSize(QSize(30, 30))
        self.pb_import.setMaximumSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pb_import)

        self.pb_export = QToolButton(self.fr_download)
        self.pb_export.setObjectName(u"pb_export")
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
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Format:", None))
        self.cb_format.setItemText(0, QCoreApplication.translate("Form", u"ISO 23386 XML", None))
        self.cb_format.setItemText(1, QCoreApplication.translate("Form", u"ISO 7817-3 XML (LOIN)", None))

        self.pb_create.setText(QCoreApplication.translate("Form", u"Create", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Export:", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"**Settings**", None))
#if QT_CONFIG(tooltip)
        self.pb_import.setToolTip(QCoreApplication.translate("Form", u"Import", None))
#endif // QT_CONFIG(tooltip)
        self.pb_import.setText("")
#if QT_CONFIG(tooltip)
        self.pb_export.setToolTip(QCoreApplication.translate("Form", u"Export", None))
#endif // QT_CONFIG(tooltip)
        self.pb_export.setText("")
    # retranslateUi

