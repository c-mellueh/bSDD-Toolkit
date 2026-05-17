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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QSizePolicy,
    QSplitter, QWidget)

from bsdd_gui.module.property_picker.model_views import (ClassView, PropertyView, PsetView)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(709, 486)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.spl_horizontal = QSplitter(Form)
        self.spl_horizontal.setObjectName(u"spl_horizontal")
        self.spl_horizontal.setOrientation(Qt.Orientation.Horizontal)
        self.spl_vertical = QSplitter(self.spl_horizontal)
        self.spl_vertical.setObjectName(u"spl_vertical")
        self.spl_vertical.setOrientation(Qt.Orientation.Vertical)
        self.tv_classes = ClassView(self.spl_vertical)
        self.tv_classes.setObjectName(u"tv_classes")
        self.spl_vertical.addWidget(self.tv_classes)
        self.tv_pset = PsetView(self.spl_vertical)
        self.tv_pset.setObjectName(u"tv_pset")
        self.spl_vertical.addWidget(self.tv_pset)
        self.spl_horizontal.addWidget(self.spl_vertical)
        self.tv_properties = PropertyView(self.spl_horizontal)
        self.tv_properties.setObjectName(u"tv_properties")
        self.tv_properties.setEnabled(True)
        self.spl_horizontal.addWidget(self.tv_properties)

        self.gridLayout.addWidget(self.spl_horizontal, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
    # retranslateUi

