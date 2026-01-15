# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ClassEditor.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

from bsdd_gui.module.class_editor_widget.ui import IfcTagInput
from bsdd_gui.module.relationship_editor_widget.ui import RelationshipWidget

class Ui_ClassEditor(object):
    def setupUi(self, ClassEditor):
        if not ClassEditor.objectName():
            ClassEditor.setObjectName(u"ClassEditor")
        ClassEditor.resize(709, 713)
        self.verticalLayout = QVBoxLayout(ClassEditor)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gb_required = QGroupBox(ClassEditor)
        self.gb_required.setObjectName(u"gb_required")
        self.gridLayout = QGridLayout(self.gb_required)
        self.gridLayout.setObjectName(u"gridLayout")
        self.hl_code = QHBoxLayout()
        self.hl_code.setObjectName(u"hl_code")
        self.lb_code = QLabel(self.gb_required)
        self.lb_code.setObjectName(u"lb_code")

        self.hl_code.addWidget(self.lb_code)

        self.le_code = QLineEdit(self.gb_required)
        self.le_code.setObjectName(u"le_code")

        self.hl_code.addWidget(self.le_code)


        self.gridLayout.addLayout(self.hl_code, 0, 1, 1, 1)

        self.hl_name = QHBoxLayout()
        self.hl_name.setObjectName(u"hl_name")
        self.lb_name = QLabel(self.gb_required)
        self.lb_name.setObjectName(u"lb_name")

        self.hl_name.addWidget(self.lb_name)

        self.le_name = QLineEdit(self.gb_required)
        self.le_name.setObjectName(u"le_name")

        self.hl_name.addWidget(self.le_name)


        self.gridLayout.addLayout(self.hl_name, 0, 0, 1, 1)

        self.hl_class_type = QHBoxLayout()
        self.hl_class_type.setObjectName(u"hl_class_type")
        self.lb_class_type = QLabel(self.gb_required)
        self.lb_class_type.setObjectName(u"lb_class_type")

        self.hl_class_type.addWidget(self.lb_class_type)

        self.cb_class_type = QComboBox(self.gb_required)
        self.cb_class_type.setObjectName(u"cb_class_type")

        self.hl_class_type.addWidget(self.cb_class_type)


        self.gridLayout.addLayout(self.hl_class_type, 1, 0, 1, 1)

        self.hl_status = QHBoxLayout()
        self.hl_status.setObjectName(u"hl_status")
        self.lb_status = QLabel(self.gb_required)
        self.lb_status.setObjectName(u"lb_status")

        self.hl_status.addWidget(self.lb_status)

        self.cb_status = QComboBox(self.gb_required)
        self.cb_status.setObjectName(u"cb_status")

        self.hl_status.addWidget(self.cb_status)


        self.gridLayout.addLayout(self.hl_status, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.gb_required)

        self.gb_defintion = QGroupBox(ClassEditor)
        self.gb_defintion.setObjectName(u"gb_defintion")
        self.verticalLayout_2 = QVBoxLayout(self.gb_defintion)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.te_definition = QTextEdit(self.gb_defintion)
        self.te_definition.setObjectName(u"te_definition")

        self.verticalLayout_2.addWidget(self.te_definition)


        self.verticalLayout.addWidget(self.gb_defintion)

        self.gb_ifc_entities = QGroupBox(ClassEditor)
        self.gb_ifc_entities.setObjectName(u"gb_ifc_entities")
        self.verticalLayout_4 = QVBoxLayout(self.gb_ifc_entities)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.ti_related_ifc_entity = IfcTagInput(self.gb_ifc_entities)
        self.ti_related_ifc_entity.setObjectName(u"ti_related_ifc_entity")

        self.verticalLayout_4.addWidget(self.ti_related_ifc_entity)


        self.verticalLayout.addWidget(self.gb_ifc_entities)

        self.gb_relationship = QGroupBox(ClassEditor)
        self.gb_relationship.setObjectName(u"gb_relationship")
        self.verticalLayout_3 = QVBoxLayout(self.gb_relationship)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.relationship_editor = RelationshipWidget(self.gb_relationship)
        self.relationship_editor.setObjectName(u"relationship_editor")

        self.verticalLayout_3.addWidget(self.relationship_editor)


        self.verticalLayout.addWidget(self.gb_relationship)


        self.retranslateUi(ClassEditor)

        QMetaObject.connectSlotsByName(ClassEditor)
    # setupUi

    def retranslateUi(self, ClassEditor):
        ClassEditor.setWindowTitle(QCoreApplication.translate("ClassEditor", u"Form", None))
        self.gb_required.setTitle(QCoreApplication.translate("ClassEditor", u"Required", None))
        self.lb_code.setText(QCoreApplication.translate("ClassEditor", u"Code", None))
        self.lb_name.setText(QCoreApplication.translate("ClassEditor", u"Name", None))
        self.lb_class_type.setText(QCoreApplication.translate("ClassEditor", u"Class Type", None))
        self.lb_status.setText(QCoreApplication.translate("ClassEditor", u"Status", None))
        self.gb_defintion.setTitle(QCoreApplication.translate("ClassEditor", u"Definition", None))
        self.gb_ifc_entities.setTitle(QCoreApplication.translate("ClassEditor", u"Related IFC Entities", None))
        self.gb_relationship.setTitle(QCoreApplication.translate("ClassEditor", u"Relationships", None))
    # retranslateUi

