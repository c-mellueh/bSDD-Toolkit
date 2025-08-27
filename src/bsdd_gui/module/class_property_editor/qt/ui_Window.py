# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from bsdd_gui.module.class_property_editor.views import ValueView


class Ui_PropertyWindow(object):
    def setupUi(self, PropertyWindow):
        if not PropertyWindow.objectName():
            PropertyWindow.setObjectName("PropertyWindow")
        PropertyWindow.resize(649, 695)
        self.verticalLayout = QVBoxLayout(PropertyWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QTabWidget(PropertyWindow)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_basics = QWidget()
        self.tab_basics.setObjectName("tab_basics")
        self.verticalLayout_2 = QVBoxLayout(self.tab_basics)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.fl_code = QFormLayout()
        self.fl_code.setObjectName("fl_code")
        self.lb_code = QLabel(self.tab_basics)
        self.lb_code.setObjectName("lb_code")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lb_code.sizePolicy().hasHeightForWidth())
        self.lb_code.setSizePolicy(sizePolicy)

        self.fl_code.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_code)

        self.le_code = QLineEdit(self.tab_basics)
        self.le_code.setObjectName("le_code")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.le_code.sizePolicy().hasHeightForWidth())
        self.le_code.setSizePolicy(sizePolicy1)
        self.le_code.setMinimumSize(QSize(350, 0))

        self.fl_code.setWidget(1, QFormLayout.ItemRole.FieldRole, self.le_code)

        self.lb_property_reference = QLabel(self.tab_basics)
        self.lb_property_reference.setObjectName("lb_property_reference")

        self.fl_code.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_property_reference)

        self.le_property_reference = QLineEdit(self.tab_basics)
        self.le_property_reference.setObjectName("le_property_reference")

        self.fl_code.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_property_reference)

        self.lb_unit = QLabel(self.tab_basics)
        self.lb_unit.setObjectName("lb_unit")

        self.fl_code.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lb_unit)

        self.cb_unit = QComboBox(self.tab_basics)
        self.cb_unit.setObjectName("cb_unit")

        self.fl_code.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cb_unit)

        self.verticalLayout_2.addLayout(self.fl_code)

        self.hl_value_description = QHBoxLayout()
        self.hl_value_description.setObjectName("hl_value_description")
        self.lb_allowed_values = QLabel(self.tab_basics)
        self.lb_allowed_values.setObjectName("lb_allowed_values")
        self.lb_allowed_values.setMinimumSize(QSize(0, 0))

        self.hl_value_description.addWidget(self.lb_allowed_values)

        self.cb_is_required = QCheckBox(self.tab_basics)
        self.cb_is_required.setObjectName("cb_is_required")
        self.cb_is_required.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.hl_value_description.addWidget(self.cb_is_required)

        self.verticalLayout_2.addLayout(self.hl_value_description)

        self.widget = ValueView(self.tab_basics)
        self.widget.setObjectName("widget")

        self.verticalLayout_2.addWidget(self.widget)

        self.splitter = QSplitter(self.tab_basics)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.te_description = QTextEdit(self.splitter)
        self.te_description.setObjectName("te_description")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.te_description.sizePolicy().hasHeightForWidth())
        self.te_description.setSizePolicy(sizePolicy2)
        self.te_description.setMinimumSize(QSize(0, 28))
        self.te_description.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoAll)
        self.te_description.setReadOnly(False)
        self.splitter.addWidget(self.te_description)

        self.verticalLayout_2.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_basics, "")
        self.tab_advanced = QWidget()
        self.tab_advanced.setObjectName("tab_advanced")
        self.tabWidget.addTab(self.tab_advanced, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(PropertyWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(PropertyWindow)

    # setupUi

    def retranslateUi(self, PropertyWindow):
        PropertyWindow.setWindowTitle(QCoreApplication.translate("PropertyWindow", "Form", None))
        self.lb_code.setText(QCoreApplication.translate("PropertyWindow", "Code:", None))
        self.le_code.setPlaceholderText(QCoreApplication.translate("PropertyWindow", "Code", None))
        self.lb_property_reference.setText(
            QCoreApplication.translate("PropertyWindow", "Property Reference", None)
        )
        self.le_property_reference.setPlaceholderText(
            QCoreApplication.translate("PropertyWindow", "Property Code or URI", None)
        )
        self.lb_unit.setText(QCoreApplication.translate("PropertyWindow", "Unit:", None))
        self.lb_allowed_values.setText(
            QCoreApplication.translate("PropertyWindow", "Allowed Values:", None)
        )
        self.cb_is_required.setText(
            QCoreApplication.translate("PropertyWindow", "Is Required", None)
        )
        self.te_description.setPlaceholderText(
            QCoreApplication.translate("PropertyWindow", "Description", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_basics),
            QCoreApplication.translate("PropertyWindow", "Basics", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_advanced),
            QCoreApplication.translate("PropertyWindow", "Advanced", None),
        )

    # retranslateUi
