# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from som_gui.module.property_window.ui import ValueView
from som_gui.module.units.ui import UnitComboBox


class Ui_PropertyWindow(object):
    def setupUi(self, PropertyWindow):
        if not PropertyWindow.objectName():
            PropertyWindow.setObjectName("PropertyWindow")
        PropertyWindow.resize(649, 631)
        self.verticalLayout = QVBoxLayout(PropertyWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_name = QLabel(PropertyWindow)
        self.label_name.setObjectName("label_name")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_name.sizePolicy().hasHeightForWidth())
        self.label_name.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label_name)

        self.lineEdit_name = QLineEdit(PropertyWindow)
        self.lineEdit_name.setObjectName("lineEdit_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_name.sizePolicy().hasHeightForWidth())
        self.lineEdit_name.setSizePolicy(sizePolicy1)
        self.lineEdit_name.setMinimumSize(QSize(350, 0))

        self.horizontalLayout.addWidget(self.lineEdit_name)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QLabel(PropertyWindow)
        self.label_2.setObjectName("label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 1, 1, 1)

        self.label = QLabel(PropertyWindow)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_3 = QLabel(PropertyWindow)
        self.label_3.setObjectName("label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 2, 1, 1)

        self.combo_data_type = QComboBox(PropertyWindow)
        self.combo_data_type.setObjectName("combo_data_type")
        self.combo_data_type.setEditable(True)

        self.gridLayout_2.addWidget(self.combo_data_type, 1, 0, 1, 1)

        self.combo_value_type = QComboBox(PropertyWindow)
        self.combo_value_type.setObjectName("combo_value_type")
        self.combo_value_type.setEditable(True)

        self.gridLayout_2.addWidget(self.combo_value_type, 1, 1, 1, 1)

        self.combo_unit = UnitComboBox(PropertyWindow)
        self.combo_unit.setObjectName("combo_unit")
        self.combo_unit.setEditable(True)

        self.gridLayout_2.addWidget(self.combo_unit, 1, 2, 1, 1)

        self.verticalLayout_3.addLayout(self.gridLayout_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.button_add_line = QPushButton(PropertyWindow)
        self.button_add_line.setObjectName("button_add_line")
        sizePolicy.setHeightForWidth(self.button_add_line.sizePolicy().hasHeightForWidth())
        self.button_add_line.setSizePolicy(sizePolicy)
        self.button_add_line.setMinimumSize(QSize(15, 15))
        self.button_add_line.setMaximumSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.button_add_line)

        self.label_values = QLabel(PropertyWindow)
        self.label_values.setObjectName("label_values")
        self.label_values.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_2.addWidget(self.label_values)

        self.check_box_optional = QCheckBox(PropertyWindow)
        self.check_box_optional.setObjectName("check_box_optional")
        self.check_box_optional.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_2.addWidget(self.check_box_optional)

        self.check_box_inherit = QCheckBox(PropertyWindow)
        self.check_box_inherit.setObjectName("check_box_inherit")
        self.check_box_inherit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.check_box_inherit.setIconSize(QSize(0, 0))

        self.horizontalLayout_2.addWidget(self.check_box_inherit)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.splitter = QSplitter(PropertyWindow)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.table_view_value = ValueView(self.splitter)
        self.table_view_value.setObjectName("table_view_value")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.table_view_value.sizePolicy().hasHeightForWidth())
        self.table_view_value.setSizePolicy(sizePolicy2)
        self.table_view_value.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view_value.setEditTriggers(
            QAbstractItemView.EditTrigger.AnyKeyPressed
            | QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.table_view_value.setProperty("showDropIndicator", False)
        self.table_view_value.setAlternatingRowColors(False)
        self.table_view_value.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_view_value.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view_value.setGridStyle(Qt.PenStyle.DashLine)
        self.splitter.addWidget(self.table_view_value)
        self.table_view_value.horizontalHeader().setVisible(False)
        self.table_view_value.horizontalHeader().setStretchLastSection(True)
        self.description = QTextEdit(self.splitter)
        self.description.setObjectName("description")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.description.sizePolicy().hasHeightForWidth())
        self.description.setSizePolicy(sizePolicy3)
        self.description.setMinimumSize(QSize(0, 28))
        self.description.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoAll)
        self.description.setReadOnly(False)
        self.splitter.addWidget(self.description)

        self.verticalLayout_3.addWidget(self.splitter)

        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.retranslateUi(PropertyWindow)

        QMetaObject.connectSlotsByName(PropertyWindow)

    # setupUi

    def retranslateUi(self, PropertyWindow):
        PropertyWindow.setWindowTitle(QCoreApplication.translate("PropertyWindow", "Form", None))
        self.label_name.setText(QCoreApplication.translate("PropertyWindow", "Name:", None))
        self.lineEdit_name.setPlaceholderText(
            QCoreApplication.translate("PropertyWindow", "Name", None)
        )
        self.label_2.setText(QCoreApplication.translate("PropertyWindow", "Valuetype:", None))
        self.label.setText(QCoreApplication.translate("PropertyWindow", "Datatype:", None))
        self.label_3.setText(QCoreApplication.translate("PropertyWindow", "Unit:", None))
        self.button_add_line.setText(QCoreApplication.translate("PropertyWindow", "+", None))
        self.label_values.setText(
            QCoreApplication.translate("PropertyWindow", "Allowed Values:", None)
        )
        self.check_box_optional.setText(
            QCoreApplication.translate("PropertyWindow", "Optional", None)
        )
        self.check_box_inherit.setText(
            QCoreApplication.translate("PropertyWindow", "Inherit Values", None)
        )
        self.description.setPlaceholderText(
            QCoreApplication.translate("PropertyWindow", "Description", None)
        )

    # retranslateUi
