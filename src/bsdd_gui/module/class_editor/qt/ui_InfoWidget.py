# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'InfoWidget.ui'
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
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_ClassEditor(object):
    def setupUi(self, ClassEditor):
        if not ClassEditor.objectName():
            ClassEditor.setObjectName("ClassEditor")
        ClassEditor.resize(816, 546)
        self.verticalLayout = QVBoxLayout(ClassEditor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gb_required = QGroupBox(ClassEditor)
        self.gb_required.setObjectName("gb_required")
        self.gridLayout = QGridLayout(self.gb_required)
        self.gridLayout.setObjectName("gridLayout")
        self.hl_code = QHBoxLayout()
        self.hl_code.setObjectName("hl_code")
        self.lb_code = QLabel(self.gb_required)
        self.lb_code.setObjectName("lb_code")

        self.hl_code.addWidget(self.lb_code)

        self.le_code = QLineEdit(self.gb_required)
        self.le_code.setObjectName("le_code")

        self.hl_code.addWidget(self.le_code)

        self.gridLayout.addLayout(self.hl_code, 0, 0, 1, 1)

        self.lb_class_type = QLabel(self.gb_required)
        self.lb_class_type.setObjectName("lb_class_type")

        self.gridLayout.addWidget(self.lb_class_type, 1, 0, 1, 1)

        self.hl_name = QHBoxLayout()
        self.hl_name.setObjectName("hl_name")
        self.lb_name = QLabel(self.gb_required)
        self.lb_name.setObjectName("lb_name")

        self.hl_name.addWidget(self.lb_name)

        self.le_name = QLineEdit(self.gb_required)
        self.le_name.setObjectName("le_name")

        self.hl_name.addWidget(self.le_name)

        self.gridLayout.addLayout(self.hl_name, 0, 1, 1, 1)

        self.cb_class_type = QComboBox(self.gb_required)
        self.cb_class_type.addItem("")
        self.cb_class_type.addItem("")
        self.cb_class_type.addItem("")
        self.cb_class_type.addItem("")
        self.cb_class_type.setObjectName("cb_class_type")
        self.cb_class_type.setEditable(False)

        self.gridLayout.addWidget(self.cb_class_type, 1, 1, 1, 1)

        self.verticalLayout.addWidget(self.gb_required)

        self.gb_defintion = QGroupBox(ClassEditor)
        self.gb_defintion.setObjectName("gb_defintion")
        self.verticalLayout_2 = QVBoxLayout(self.gb_defintion)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.te_definition = QTextEdit(self.gb_defintion)
        self.te_definition.setObjectName("te_definition")

        self.verticalLayout_2.addWidget(self.te_definition)

        self.verticalLayout.addWidget(self.gb_defintion)

        self.gb_relationship = QGroupBox(ClassEditor)
        self.gb_relationship.setObjectName("gb_relationship")
        self.verticalLayout_3 = QVBoxLayout(self.gb_relationship)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.vl_relationship = QVBoxLayout()
        self.vl_relationship.setObjectName("vl_relationship")

        self.verticalLayout_3.addLayout(self.vl_relationship)

        self.hl_releationship_button = QHBoxLayout()
        self.hl_releationship_button.setObjectName("hl_releationship_button")
        self.pushButton = QPushButton(self.gb_relationship)
        self.pushButton.setObjectName("pushButton")

        self.hl_releationship_button.addWidget(self.pushButton)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hl_releationship_button.addItem(self.horizontalSpacer)

        self.verticalLayout_3.addLayout(self.hl_releationship_button)

        self.verticalLayout.addWidget(self.gb_relationship)

        self.retranslateUi(ClassEditor)

        QMetaObject.connectSlotsByName(ClassEditor)

    # setupUi

    def retranslateUi(self, ClassEditor):
        ClassEditor.setWindowTitle(QCoreApplication.translate("ClassEditor", "Form", None))
        self.gb_required.setTitle(QCoreApplication.translate("ClassEditor", "Required", None))
        self.lb_code.setText(QCoreApplication.translate("ClassEditor", "Code", None))
        self.lb_class_type.setText(QCoreApplication.translate("ClassEditor", "Class Type", None))
        self.lb_name.setText(QCoreApplication.translate("ClassEditor", "Name", None))
        self.cb_class_type.setItemText(0, QCoreApplication.translate("ClassEditor", "Class", None))
        self.cb_class_type.setItemText(
            1, QCoreApplication.translate("ClassEditor", "Material", None)
        )
        self.cb_class_type.setItemText(
            2, QCoreApplication.translate("ClassEditor", "GroupOfProperties", None)
        )
        self.cb_class_type.setItemText(
            3, QCoreApplication.translate("ClassEditor", "AlternativeUse", None)
        )

        self.gb_defintion.setTitle(QCoreApplication.translate("ClassEditor", "Definition", None))
        self.gb_relationship.setTitle(
            QCoreApplication.translate("ClassEditor", "Relationships", None)
        )
        self.pushButton.setText(QCoreApplication.translate("ClassEditor", "Add", None))

    # retranslateUi
