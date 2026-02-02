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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QSizePolicy, QSplitter, QTableView, QToolButton,
    QVBoxLayout, QWidget)

from bsdd_gui.module.group_of_properties.views import GroupOfPropertiesView

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1068, 706)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.gridLayoutWidget_2 = QWidget(self.splitter)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tb_search = QToolButton(self.gridLayoutWidget_2)
        self.tb_search.setObjectName(u"tb_search")

        self.gridLayout_2.addWidget(self.tb_search, 0, 0, 1, 1)

        self.lb_class = QLabel(self.gridLayoutWidget_2)
        self.lb_class.setObjectName(u"lb_class")

        self.gridLayout_2.addWidget(self.lb_class, 0, 1, 1, 1)

        self.tb_new = QToolButton(self.gridLayoutWidget_2)
        self.tb_new.setObjectName(u"tb_new")

        self.gridLayout_2.addWidget(self.tb_new, 0, 2, 1, 1)

        self.treeView = GroupOfPropertiesView(self.gridLayoutWidget_2)
        self.treeView.setObjectName(u"treeView")

        self.gridLayout_2.addWidget(self.treeView, 1, 0, 1, 3)

        self.splitter.addWidget(self.gridLayoutWidget_2)
        self.gridLayoutWidget = QWidget(self.splitter)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(self.gridLayoutWidget)
        self.tableView.setObjectName(u"tableView")

        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)

        self.splitter.addWidget(self.gridLayoutWidget)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.tb_search.setText(QCoreApplication.translate("Form", u"...", None))
        self.lb_class.setText(QCoreApplication.translate("Form", u"Group of Properties:", None))
        self.tb_new.setText(QCoreApplication.translate("Form", u"New", None))
    # retranslateUi

