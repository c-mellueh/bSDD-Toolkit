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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QSizePolicy, QSplitter, QVBoxLayout, QWidget)

from bsdd_gui.module.property_picker.model_views import (ClassView, PropertyView, PsetView)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(798, 481)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.spl_horizontal = QSplitter(Form)
        self.spl_horizontal.setObjectName(u"spl_horizontal")
        self.spl_horizontal.setOrientation(Qt.Orientation.Horizontal)
        self.spl_vertical = QSplitter(self.spl_horizontal)
        self.spl_vertical.setObjectName(u"spl_vertical")
        self.spl_vertical.setOrientation(Qt.Orientation.Vertical)
        self.verticalLayoutWidget_2 = QWidget(self.spl_vertical)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.lb_classes = QLabel(self.verticalLayoutWidget_2)
        self.lb_classes.setObjectName(u"lb_classes")

        self.verticalLayout_2.addWidget(self.lb_classes)

        self.tv_classes = ClassView(self.verticalLayoutWidget_2)
        self.tv_classes.setObjectName(u"tv_classes")

        self.verticalLayout_2.addWidget(self.tv_classes)

        self.spl_vertical.addWidget(self.verticalLayoutWidget_2)
        self.verticalLayoutWidget = QWidget(self.spl_vertical)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.lb_predefined_properties = QLabel(self.verticalLayoutWidget)
        self.lb_predefined_properties.setObjectName(u"lb_predefined_properties")

        self.verticalLayout.addWidget(self.lb_predefined_properties)

        self.tv_pset = PsetView(self.verticalLayoutWidget)
        self.tv_pset.setObjectName(u"tv_pset")

        self.verticalLayout.addWidget(self.tv_pset)

        self.spl_vertical.addWidget(self.verticalLayoutWidget)
        self.spl_horizontal.addWidget(self.spl_vertical)
        self.verticalLayoutWidget_3 = QWidget(self.spl_horizontal)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget_3)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.tv_properties = PropertyView(self.verticalLayoutWidget_3)
        self.tv_properties.setObjectName(u"tv_properties")

        self.verticalLayout_3.addWidget(self.tv_properties)

        self.spl_horizontal.addWidget(self.verticalLayoutWidget_3)

        self.gridLayout.addWidget(self.spl_horizontal, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.lb_classes.setText(QCoreApplication.translate("Form", u"Classes", None))
        self.lb_predefined_properties.setText(QCoreApplication.translate("Form", u"Predefined Properties", None))
        self.label.setText(QCoreApplication.translate("Form", u"Class Properties", None))
    # retranslateUi

