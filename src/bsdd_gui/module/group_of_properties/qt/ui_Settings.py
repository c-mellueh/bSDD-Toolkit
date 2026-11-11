# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Settings.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QLineEdit,
    QSizePolicy, QWidget)

from bsdd_gui.presets.ui_presets import ToggleSwitch

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 80)
        self.formLayout = QFormLayout(Form)
        self.formLayout.setObjectName(u"formLayout")
        self.label_prefix = QLabel(Form)
        self.label_prefix.setObjectName(u"label_prefix")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_prefix)

        self.le_prefix = QLineEdit(Form)
        self.le_prefix.setObjectName(u"le_prefix")
        self.le_prefix.setMaxLength(30)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_prefix)

        self.label_auto = QLabel(Form)
        self.label_auto.setObjectName(u"label_auto")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_auto)

        self.cb_auto_create = ToggleSwitch(Form)
        self.cb_auto_create.setObjectName(u"cb_auto_create")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.cb_auto_create)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_prefix.setText(QCoreApplication.translate("Form", u"Code prefix of predefined property sets", None))
        self.le_prefix.setPlaceholderText(QCoreApplication.translate("Form", u"EPset_", None))
        self.label_auto.setText(QCoreApplication.translate("Form", u"Create predefined property set for new property sets", None))
    # retranslateUi

