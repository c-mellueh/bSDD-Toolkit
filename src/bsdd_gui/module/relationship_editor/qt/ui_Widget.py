# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
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
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(713, 269)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.hl_releationship_button = QHBoxLayout()
        self.hl_releationship_button.setObjectName("hl_releationship_button")
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName("pushButton")

        self.hl_releationship_button.addWidget(self.pushButton)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hl_releationship_button.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.hl_releationship_button)

        self.hl_relationship_entry = QHBoxLayout()
        self.hl_relationship_entry.setObjectName("hl_relationship_entry")
        self.lb_relationType = QLabel(Form)
        self.lb_relationType.setObjectName("lb_relationType")

        self.hl_relationship_entry.addWidget(self.lb_relationType)

        self.cb_relation_type = QComboBox(Form)
        self.cb_relation_type.addItem("")
        self.cb_relation_type.addItem("")
        self.cb_relation_type.addItem("")
        self.cb_relation_type.addItem("")
        self.cb_relation_type.addItem("")
        self.cb_relation_type.addItem("")
        self.cb_relation_type.addItem("")
        self.cb_relation_type.addItem("")
        self.cb_relation_type.setObjectName("cb_relation_type")
        self.cb_relation_type.setMinimumSize(QSize(100, 0))

        self.hl_relationship_entry.addWidget(self.cb_relation_type)

        self.lb_related_class = QLabel(Form)
        self.lb_related_class.setObjectName("lb_related_class")

        self.hl_relationship_entry.addWidget(self.lb_related_class)

        self.le_related_class = QLineEdit(Form)
        self.le_related_class.setObjectName("le_related_class")
        self.le_related_class.setPlaceholderText("https://identifier.buildingsmart.org/uri/...")

        self.hl_relationship_entry.addWidget(self.le_related_class)

        self.lb_related_class_name = QLabel(Form)
        self.lb_related_class_name.setObjectName("lb_related_class_name")

        self.hl_relationship_entry.addWidget(self.lb_related_class_name)

        self.le_relatec_class_name = QLineEdit(Form)
        self.le_relatec_class_name.setObjectName("le_relatec_class_name")

        self.hl_relationship_entry.addWidget(self.le_relatec_class_name)

        self.lb_fraction = QLabel(Form)
        self.lb_fraction.setObjectName("lb_fraction")

        self.hl_relationship_entry.addWidget(self.lb_fraction)

        self.ds_fraction = QDoubleSpinBox(Form)
        self.ds_fraction.setObjectName("ds_fraction")

        self.hl_relationship_entry.addWidget(self.ds_fraction)

        self.lb_owned_uri = QLabel(Form)
        self.lb_owned_uri.setObjectName("lb_owned_uri")

        self.hl_relationship_entry.addWidget(self.lb_owned_uri)

        self.le_owned_uri = QLineEdit(Form)
        self.le_owned_uri.setObjectName("le_owned_uri")

        self.hl_relationship_entry.addWidget(self.le_owned_uri)

        self.verticalLayout.addLayout(self.hl_relationship_entry)

        self.tableView = QTableView(Form)
        self.tableView.setObjectName("tableView")

        self.verticalLayout.addWidget(self.tableView)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.pushButton.setText(QCoreApplication.translate("Form", "Add", None))
        self.lb_relationType.setText(QCoreApplication.translate("Form", "RelationType", None))
        self.cb_relation_type.setItemText(
            0, QCoreApplication.translate("Form", "IsSimilarTo", None)
        )
        self.cb_relation_type.setItemText(
            1, QCoreApplication.translate("Form", "HasMaterial", None)
        )
        self.cb_relation_type.setItemText(
            2, QCoreApplication.translate("Form", "HasReference", None)
        )
        self.cb_relation_type.setItemText(3, QCoreApplication.translate("Form", "IsEqualTo", None))
        self.cb_relation_type.setItemText(4, QCoreApplication.translate("Form", "IsParentOf", None))
        self.cb_relation_type.setItemText(5, QCoreApplication.translate("Form", "IsChildOf", None))
        self.cb_relation_type.setItemText(6, QCoreApplication.translate("Form", "HasPart", None))
        self.cb_relation_type.setItemText(7, QCoreApplication.translate("Form", "IsPartOf", None))

        self.lb_related_class.setText(QCoreApplication.translate("Form", "RelatedClass", None))
        self.lb_related_class_name.setText(
            QCoreApplication.translate("Form", "Related Class Name", None)
        )
        self.lb_fraction.setText(QCoreApplication.translate("Form", "Fraction", None))
        self.lb_owned_uri.setText(QCoreApplication.translate("Form", "OwnedUri", None))

    # retranslateUi
