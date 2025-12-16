# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Settings.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QLabel, QLineEdit, QSizePolicy, QSpinBox,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(532, 122)
        self.formLayout = QFormLayout(Form)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.checkBox = QCheckBox(Form)
        self.checkBox.setObjectName(u"checkBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.checkBox)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.cb_language = QComboBox(Form)
        self.cb_language.addItem("")
        self.cb_language.addItem("")
        self.cb_language.setObjectName(u"cb_language")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cb_language)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.spinBox = QSpinBox(Form)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimum(1)
        self.spinBox.setValue(3)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinBox)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"use OpenAI:", None))
        self.checkBox.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"OpenAI API-Key:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"AI-Sprache", None))
        self.cb_language.setItemText(0, QCoreApplication.translate("Form", u"German", None))
        self.cb_language.setItemText(1, QCoreApplication.translate("Form", u"English", None))

        self.label_4.setText(QCoreApplication.translate("Form", u"Satzanzahl", None))
    # retranslateUi

