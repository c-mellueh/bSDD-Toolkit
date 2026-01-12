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
from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy, QSlider, QVBoxLayout, QWidget


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(312, 166)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QLabel(Form)
        self.titleLabel.setObjectName("titleLabel")

        self.verticalLayout.addWidget(self.titleLabel)

        self.lb_l0 = QLabel(Form)
        self.lb_l0.setObjectName("lb_l0")

        self.verticalLayout.addWidget(self.lb_l0)

        self.sl_l0 = QSlider(Form)
        self.sl_l0.setObjectName("sl_l0")
        self.sl_l0.setMinimum(100)
        self.sl_l0.setMaximum(750)
        self.sl_l0.setSingleStep(5)
        self.sl_l0.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout.addWidget(self.sl_l0)

        self.lb_ks = QLabel(Form)
        self.lb_ks.setObjectName("lb_ks")

        self.verticalLayout.addWidget(self.lb_ks)

        self.sl_ks = QSlider(Form)
        self.sl_ks.setObjectName("sl_ks")
        self.sl_ks.setMinimum(1)
        self.sl_ks.setMaximum(100)
        self.sl_ks.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout.addWidget(self.sl_ks)

        self.lb_rep = QLabel(Form)
        self.lb_rep.setObjectName("lb_rep")

        self.verticalLayout.addWidget(self.lb_rep)

        self.sl_rep = QSlider(Form)
        self.sl_rep.setObjectName("sl_rep")
        self.sl_rep.setMinimum(10)
        self.sl_rep.setMaximum(2500)
        self.sl_rep.setSingleStep(10)
        self.sl_rep.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout.addWidget(self.sl_rep)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.titleLabel.setText(QCoreApplication.translate("Form", "Physics Settings", None))
        self.lb_l0.setText(QCoreApplication.translate("Form", "L\u2080 (spring length)", None))
        self.lb_ks.setText(QCoreApplication.translate("Form", "k_spring", None))
        self.lb_rep.setText(QCoreApplication.translate("Form", "repulsion", None))

    # retranslateUi
