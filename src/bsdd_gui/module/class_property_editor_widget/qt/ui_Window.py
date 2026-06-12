# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSplitter, QTextEdit,
    QVBoxLayout, QWidget)

from bsdd_gui.module.allowed_values_table_view.ui import AllowedValuesTable
from bsdd_gui.presets.ui_presets.line_edit_with_button import LineEditWithButton

class Ui_PropertyWindow(object):
    def setupUi(self, PropertyWindow):
        if not PropertyWindow.objectName():
            PropertyWindow.setObjectName(u"PropertyWindow")
        PropertyWindow.resize(655, 713)
        self.verticalLayout = QVBoxLayout(PropertyWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.vl_values = QVBoxLayout()
        self.vl_values.setObjectName(u"vl_values")

        self.verticalLayout.addLayout(self.vl_values)

        self.fl_code = QFormLayout()
        self.fl_code.setObjectName(u"fl_code")
        self.lb_code = QLabel(PropertyWindow)
        self.lb_code.setObjectName(u"lb_code")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lb_code.sizePolicy().hasHeightForWidth())
        self.lb_code.setSizePolicy(sizePolicy)

        self.fl_code.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_code)

        self.le_code = QLineEdit(PropertyWindow)
        self.le_code.setObjectName(u"le_code")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.le_code.sizePolicy().hasHeightForWidth())
        self.le_code.setSizePolicy(sizePolicy1)
        self.le_code.setMinimumSize(QSize(350, 0))

        self.fl_code.setWidget(1, QFormLayout.ItemRole.FieldRole, self.le_code)

        self.lb_property_reference = QLabel(PropertyWindow)
        self.lb_property_reference.setObjectName(u"lb_property_reference")

        self.fl_code.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_property_reference)

        self.le_property_reference = LineEditWithButton(PropertyWindow)
        self.le_property_reference.setObjectName(u"le_property_reference")

        self.fl_code.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_property_reference)

        self.lb_unit = QLabel(PropertyWindow)
        self.lb_unit.setObjectName(u"lb_unit")

        self.fl_code.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lb_unit)

        self.cb_unit = QComboBox(PropertyWindow)
        self.cb_unit.setObjectName(u"cb_unit")

        self.fl_code.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cb_unit)


        self.verticalLayout.addLayout(self.fl_code)

        self.hl_value_description = QHBoxLayout()
        self.hl_value_description.setObjectName(u"hl_value_description")
        self.pb_new_value = QPushButton(PropertyWindow)
        self.pb_new_value.setObjectName(u"pb_new_value")
        self.pb_new_value.setMaximumSize(QSize(24, 24))

        self.hl_value_description.addWidget(self.pb_new_value)

        self.lb_allowed_values = QLabel(PropertyWindow)
        self.lb_allowed_values.setObjectName(u"lb_allowed_values")
        self.lb_allowed_values.setMinimumSize(QSize(0, 0))

        self.hl_value_description.addWidget(self.lb_allowed_values)

        self.cb_is_required = QCheckBox(PropertyWindow)
        self.cb_is_required.setObjectName(u"cb_is_required")
        self.cb_is_required.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.hl_value_description.addWidget(self.cb_is_required)


        self.verticalLayout.addLayout(self.hl_value_description)

        self.tv_allowed_values = AllowedValuesTable(PropertyWindow)
        self.tv_allowed_values.setObjectName(u"tv_allowed_values")

        self.verticalLayout.addWidget(self.tv_allowed_values)

        self.la_description = QLabel(PropertyWindow)
        self.la_description.setObjectName(u"la_description")

        self.verticalLayout.addWidget(self.la_description)

        self.splitter = QSplitter(PropertyWindow)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.te_description = QTextEdit(self.splitter)
        self.te_description.setObjectName(u"te_description")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.te_description.sizePolicy().hasHeightForWidth())
        self.te_description.setSizePolicy(sizePolicy2)
        self.te_description.setMinimumSize(QSize(0, 28))
        self.te_description.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoAll)
        self.te_description.setReadOnly(False)
        self.splitter.addWidget(self.te_description)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(PropertyWindow)

        QMetaObject.connectSlotsByName(PropertyWindow)
    # setupUi

    def retranslateUi(self, PropertyWindow):
        PropertyWindow.setWindowTitle(QCoreApplication.translate("PropertyWindow", u"Form", None))
        self.lb_code.setText(QCoreApplication.translate("PropertyWindow", u"Code:", None))
        self.le_code.setPlaceholderText(QCoreApplication.translate("PropertyWindow", u"Code", None))
        self.lb_property_reference.setText(QCoreApplication.translate("PropertyWindow", u"Property Reference", None))
        self.le_property_reference.setPlaceholderText(QCoreApplication.translate("PropertyWindow", u"Property Code or URI", None))
        self.lb_unit.setText(QCoreApplication.translate("PropertyWindow", u"Unit:", None))
        self.pb_new_value.setText("")
        self.lb_allowed_values.setText(QCoreApplication.translate("PropertyWindow", u"Allowed Values:", None))
        self.cb_is_required.setText(QCoreApplication.translate("PropertyWindow", u"Is Required", None))
        self.la_description.setText(QCoreApplication.translate("PropertyWindow", u"Description:", None))
        self.te_description.setPlaceholderText(QCoreApplication.translate("PropertyWindow", u"Description", None))
    # retranslateUi

