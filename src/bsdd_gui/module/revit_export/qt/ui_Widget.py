# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
        Form.resize(1509, 828)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.fw_output = FileSelector(Form)
        self.fw_output.setObjectName(u"fw_output")

        self.gridLayout.addWidget(self.fw_output, 4, 0, 1, 1)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.button_layout.addItem(self.horizontalSpacer_2)

        self.pb_create = QPushButton(Form)
        self.pb_create.setObjectName(u"pb_create")

        self.button_layout.addWidget(self.pb_create)


        self.gridLayout.addLayout(self.button_layout, 5, 0, 1, 1)

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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.loin.sizePolicy().hasHeightForWidth())
        self.loin.setSizePolicy(sizePolicy1)
        self.splitter.addWidget(self.loin)
        self.settings_widget = QWidget(self.splitter)
        self.settings_widget.setObjectName(u"settings_widget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.settings_widget.sizePolicy().hasHeightForWidth())
        self.settings_widget.setSizePolicy(sizePolicy2)
        self.settings_widget.setMinimumSize(QSize(300, 0))
        self.settings_widget.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout = QVBoxLayout(self.settings_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.settings_widget)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 296, 689))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.main_settings = QFrame(self.scrollAreaWidgetContents_3)
        self.main_settings.setObjectName(u"main_settings")
        sizePolicy1.setHeightForWidth(self.main_settings.sizePolicy().hasHeightForWidth())
        self.main_settings.setSizePolicy(sizePolicy1)
        self.main_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.main_settings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.settings_main = QFrame(self.main_settings)
        self.settings_main.setObjectName(u"settings_main")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.settings_main.sizePolicy().hasHeightForWidth())
        self.settings_main.setSizePolicy(sizePolicy3)
        self.settings_main.setFrameShape(QFrame.Shape.StyledPanel)
        self.settings_main.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_3 = QGridLayout(self.settings_main)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cb_mode = QComboBox(self.settings_main)
        self.cb_mode.addItem("")
        self.cb_mode.addItem("")
        self.cb_mode.setObjectName(u"cb_mode")

        self.gridLayout_3.addWidget(self.cb_mode, 2, 1, 1, 1)

        self.lb_settings_title = QLabel(self.settings_main)
        self.lb_settings_title.setObjectName(u"lb_settings_title")
        self.lb_settings_title.setTextFormat(Qt.TextFormat.MarkdownText)
        self.lb_settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.lb_settings_title, 0, 0, 1, 2)

        self.cb_text = QComboBox(self.settings_main)
        self.cb_text.addItem("")
        self.cb_text.addItem("")
        self.cb_text.setObjectName(u"cb_text")

        self.gridLayout_3.addWidget(self.cb_text, 3, 1, 1, 1)

        self.lb_text_or_label = QLabel(self.settings_main)
        self.lb_text_or_label.setObjectName(u"lb_text_or_label")

        self.gridLayout_3.addWidget(self.lb_text_or_label, 3, 0, 1, 1)

        self.lb_mode = QLabel(self.settings_main)
        self.lb_mode.setObjectName(u"lb_mode")

        self.gridLayout_3.addWidget(self.lb_mode, 2, 0, 1, 1)


        self.gridLayout_2.addWidget(self.settings_main, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 1, 0, 1, 1)


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
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pb_export.sizePolicy().hasHeightForWidth())
        self.pb_export.setSizePolicy(sizePolicy4)
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
        self.label_3.setText(QCoreApplication.translate("Form", u"Export:", None))
        self.pb_create.setText(QCoreApplication.translate("Form", u"Create", None))
        self.cb_mode.setItemText(0, QCoreApplication.translate("Form", u"CustomPropertySet", None))
        self.cb_mode.setItemText(1, QCoreApplication.translate("Form", u"SharedParameters", None))

        self.lb_settings_title.setText(QCoreApplication.translate("Form", u"**Settings**", None))
        self.cb_text.setItemText(0, QCoreApplication.translate("Form", u"Text", None))
        self.cb_text.setItemText(1, QCoreApplication.translate("Form", u"Label", None))

        self.lb_text_or_label.setText(QCoreApplication.translate("Form", u"Text or Label:", None))
        self.lb_mode.setText(QCoreApplication.translate("Form", u"Mode:", None))
#if QT_CONFIG(tooltip)
        self.pb_import.setToolTip(QCoreApplication.translate("Form", u"Import", None))
#endif // QT_CONFIG(tooltip)
        self.pb_import.setText("")
#if QT_CONFIG(tooltip)
        self.pb_export.setToolTip(QCoreApplication.translate("Form", u"Export", None))
#endif // QT_CONFIG(tooltip)
        self.pb_export.setText("")
    # retranslateUi

