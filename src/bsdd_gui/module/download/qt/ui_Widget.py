# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from bsdd_gui.presets.ui_presets import FileSelector, ToggleSwitch


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(650, 190)
        Form.setMinimumSize(QSize(600, 0))
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName("label_2")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btn_start = QPushButton(Form)
        self.btn_start.setObjectName("btn_start")

        self.horizontalLayout.addWidget(self.btn_start)

        self.btn_cancel = QPushButton(Form)
        self.btn_cancel.setObjectName("btn_cancel")

        self.horizontalLayout.addWidget(self.btn_cancel)

        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 2)

        self.le_uri = QLineEdit(Form)
        self.le_uri.setObjectName("le_uri")

        self.gridLayout.addWidget(self.le_uri, 0, 1, 1, 1)

        self.label = QLabel(Form)
        self.label.setObjectName("label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.fs_save_path = FileSelector(Form)
        self.fs_save_path.setObjectName("fs_save_path")

        self.gridLayout.addWidget(self.fs_save_path, 4, 0, 1, 2)

        self.cb_save = ToggleSwitch(Form)
        self.cb_save.setObjectName("cb_save")

        self.gridLayout.addWidget(self.cb_save, 2, 1, 1, 1)

        self.wd_progressbars = QWidget(Form)
        self.wd_progressbars.setObjectName("wd_progressbars")
        self.formLayout = QFormLayout(self.wd_progressbars)
        self.formLayout.setObjectName("formLayout")
        self.lb_classes = QLabel(self.wd_progressbars)
        self.lb_classes.setObjectName("lb_classes")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_classes)

        self.pb_classes = QProgressBar(self.wd_progressbars)
        self.pb_classes.setObjectName("pb_classes")
        self.pb_classes.setValue(24)
        self.pb_classes.setTextVisible(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.pb_classes)

        self.lb_properties = QLabel(self.wd_progressbars)
        self.lb_properties.setObjectName("lb_properties")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_properties)

        self.pb_properties = QProgressBar(self.wd_progressbars)
        self.pb_properties.setObjectName("pb_properties")
        self.pb_properties.setValue(24)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.pb_properties)

        self.gridLayout.addWidget(self.wd_progressbars, 1, 0, 1, 2)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Save to File:", None))
        self.btn_start.setText(QCoreApplication.translate("Form", "Start", None))
        self.btn_cancel.setText(QCoreApplication.translate("Form", "Cancel", None))
        self.label.setText(QCoreApplication.translate("Form", "URI:", None))
        self.cb_save.setText("")
        self.lb_classes.setText(QCoreApplication.translate("Form", "TextLabel", None))
        self.lb_properties.setText(QCoreApplication.translate("Form", "TextLabel", None))

    # retranslateUi
