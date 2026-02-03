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
    QPushButton, QSizePolicy, QSplitter, QTableView,
    QToolButton, QVBoxLayout, QWidget)

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
        self.glw_class = QWidget(self.splitter)
        self.glw_class.setObjectName(u"glw_class")
        self.gl_class = QGridLayout(self.glw_class)
        self.gl_class.setObjectName(u"gl_class")
        self.gl_class.setContentsMargins(0, 0, 0, 0)
        self.tb_search = QToolButton(self.glw_class)
        self.tb_search.setObjectName(u"tb_search")

        self.gl_class.addWidget(self.tb_search, 0, 0, 1, 1)

        self.lb_class = QLabel(self.glw_class)
        self.lb_class.setObjectName(u"lb_class")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lb_class.sizePolicy().hasHeightForWidth())
        self.lb_class.setSizePolicy(sizePolicy)

        self.gl_class.addWidget(self.lb_class, 0, 1, 1, 1)

        self.tv_class = GroupOfPropertiesView(self.glw_class)
        self.tv_class.setObjectName(u"tv_class")

        self.gl_class.addWidget(self.tv_class, 1, 0, 1, 3)

        self.pb_new_class = QPushButton(self.glw_class)
        self.pb_new_class.setObjectName(u"pb_new_class")

        self.gl_class.addWidget(self.pb_new_class, 0, 2, 1, 1)

        self.splitter.addWidget(self.glw_class)
        self.glw_property = QWidget(self.splitter)
        self.glw_property.setObjectName(u"glw_property")
        self.gl_property = QGridLayout(self.glw_property)
        self.gl_property.setObjectName(u"gl_property")
        self.gl_property.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.glw_property)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.gl_property.addWidget(self.label, 0, 0, 1, 1)

        self.tableView = QTableView(self.glw_property)
        self.tableView.setObjectName(u"tableView")

        self.gl_property.addWidget(self.tableView, 1, 0, 1, 2)

        self.pb_new_prop = QPushButton(self.glw_property)
        self.pb_new_prop.setObjectName(u"pb_new_prop")

        self.gl_property.addWidget(self.pb_new_prop, 0, 1, 1, 1)

        self.splitter.addWidget(self.glw_property)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.tb_search.setText(QCoreApplication.translate("Form", u"...", None))
        self.lb_class.setText(QCoreApplication.translate("Form", u"Group of Properties:", None))
        self.pb_new_class.setText(QCoreApplication.translate("Form", u"New", None))
        self.label.setText(QCoreApplication.translate("Form", u"Property:", None))
        self.pb_new_prop.setText(QCoreApplication.translate("Form", u"New", None))
    # retranslateUi

