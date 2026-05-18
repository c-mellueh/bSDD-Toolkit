# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from bsdd_gui.module.loin.model_views import ClassView, PropertyView, PsetView


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1005, 682)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.spl_horizontal = QSplitter(Form)
        self.spl_horizontal.setObjectName("spl_horizontal")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spl_horizontal.sizePolicy().hasHeightForWidth())
        self.spl_horizontal.setSizePolicy(sizePolicy)
        self.spl_horizontal.setOrientation(Qt.Orientation.Horizontal)
        self.spl_vertical = QSplitter(self.spl_horizontal)
        self.spl_vertical.setObjectName("spl_vertical")
        self.spl_vertical.setOrientation(Qt.Orientation.Vertical)
        self.verticalLayoutWidget_2 = QWidget(self.spl_vertical)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.lb_classes = QLabel(self.verticalLayoutWidget_2)
        self.lb_classes.setObjectName("lb_classes")

        self.verticalLayout_2.addWidget(self.lb_classes)

        self.tv_classes = ClassView(self.verticalLayoutWidget_2)
        self.tv_classes.setObjectName("tv_classes")

        self.verticalLayout_2.addWidget(self.tv_classes)

        self.spl_vertical.addWidget(self.verticalLayoutWidget_2)
        self.verticalLayoutWidget = QWidget(self.spl_vertical)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.lb_predefined_properties = QLabel(self.verticalLayoutWidget)
        self.lb_predefined_properties.setObjectName("lb_predefined_properties")

        self.verticalLayout.addWidget(self.lb_predefined_properties)

        self.tv_pset = PsetView(self.verticalLayoutWidget)
        self.tv_pset.setObjectName("tv_pset")

        self.verticalLayout.addWidget(self.tv_pset)

        self.spl_vertical.addWidget(self.verticalLayoutWidget)
        self.spl_horizontal.addWidget(self.spl_vertical)
        self.verticalLayoutWidget_3 = QWidget(self.spl_horizontal)
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget_3)
        self.label.setObjectName("label")

        self.verticalLayout_3.addWidget(self.label)

        self.tv_properties = PropertyView(self.verticalLayoutWidget_3)
        self.tv_properties.setObjectName("tv_properties")

        self.verticalLayout_3.addWidget(self.tv_properties)

        self.spl_horizontal.addWidget(self.verticalLayoutWidget_3)

        self.gridLayout.addWidget(self.spl_horizontal, 0, 0, 1, 1)

        self.fr_download = QFrame(Form)
        self.fr_download.setObjectName("fr_download")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.fr_download.sizePolicy().hasHeightForWidth())
        self.fr_download.setSizePolicy(sizePolicy1)
        self.fr_download.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_download.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.fr_download)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 5)
        self.horizontalSpacer = QSpacerItem(
            1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pb_import = QToolButton(self.fr_download)
        self.pb_import.setObjectName("pb_import")
        self.pb_import.setMinimumSize(QSize(30, 30))
        self.pb_import.setMaximumSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pb_import)

        self.pb_export = QToolButton(self.fr_download)
        self.pb_export.setObjectName("pb_export")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pb_export.sizePolicy().hasHeightForWidth())
        self.pb_export.setSizePolicy(sizePolicy2)
        self.pb_export.setMinimumSize(QSize(30, 30))
        self.pb_export.setMaximumSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pb_export)

        self.gridLayout.addWidget(self.fr_download, 1, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.lb_classes.setText(QCoreApplication.translate("Form", "Classes", None))
        self.lb_predefined_properties.setText(
            QCoreApplication.translate("Form", "Predefined Properties", None)
        )
        self.label.setText(QCoreApplication.translate("Form", "Class Properties", None))
        # if QT_CONFIG(tooltip)
        self.pb_import.setToolTip(QCoreApplication.translate("Form", "Import LOIN", None))
        # endif // QT_CONFIG(tooltip)
        self.pb_import.setText("")
        # if QT_CONFIG(tooltip)
        self.pb_export.setToolTip(QCoreApplication.translate("Form", "Export LOIN", None))
        # endif // QT_CONFIG(tooltip)
        self.pb_export.setText("")

    # retranslateUi
