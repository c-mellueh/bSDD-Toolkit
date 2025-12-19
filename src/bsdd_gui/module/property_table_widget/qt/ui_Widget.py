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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFormLayout, QHeaderView,
    QLabel, QSizePolicy, QSplitter, QToolButton,
    QVBoxLayout, QWidget)

from bsdd_gui.module.property_table_widget.views import (ClassTable, PropertyTable)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(722, 639)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tv_properties = PropertyTable(self.verticalLayoutWidget)
        self.tv_properties.setObjectName(u"tv_properties")
        self.tv_properties.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tv_properties.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tv_properties.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tv_properties.setSortingEnabled(True)
        self.tv_properties.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.tv_properties)

        self.tb_new = QToolButton(self.verticalLayoutWidget)
        self.tb_new.setObjectName(u"tb_new")
        self.tb_new.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.tb_new.setArrowType(Qt.ArrowType.NoArrow)

        self.verticalLayout.addWidget(self.tb_new)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.lb_property = QLabel(self.verticalLayoutWidget_2)
        self.lb_property.setObjectName(u"lb_property")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_property)

        self.lb_property_name = QLabel(self.verticalLayoutWidget_2)
        self.lb_property_name.setObjectName(u"lb_property_name")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lb_property_name)


        self.verticalLayout_3.addLayout(self.formLayout)

        self.tv_classes = ClassTable(self.verticalLayoutWidget_2)
        self.tv_classes.setObjectName(u"tv_classes")
        self.tv_classes.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tv_classes.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tv_classes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tv_classes.setSortingEnabled(True)
        self.tv_classes.horizontalHeader().setProperty(u"showSortIndicator", True)
        self.tv_classes.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_3.addWidget(self.tv_classes)

        self.splitter.addWidget(self.verticalLayoutWidget_2)

        self.verticalLayout_2.addWidget(self.splitter)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.tb_new.setToolTip(QCoreApplication.translate("Form", u"create new property", None))
#endif // QT_CONFIG(tooltip)
        self.tb_new.setText(QCoreApplication.translate("Form", u"New", None))
        self.lb_property.setText(QCoreApplication.translate("Form", u"Property:", None))
        self.lb_property_name.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

