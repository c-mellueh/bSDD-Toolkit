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
    QHeaderView,
    QSizePolicy,
    QSplitter,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(813, 637)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QSplitter(Form)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tv_properties = QTableView(self.verticalLayoutWidget)
        self.tv_properties.setObjectName("tv_properties")
        self.tv_properties.setSortingEnabled(True)
        self.tv_properties.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.tv_properties)

        self.tb_new = QToolButton(self.verticalLayoutWidget)
        self.tb_new.setObjectName("tb_new")
        self.tb_new.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.tb_new.setArrowType(Qt.ArrowType.NoArrow)

        self.verticalLayout.addWidget(self.tb_new)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.tv_classes = QTableView(self.splitter)
        self.tv_classes.setObjectName("tv_classes")
        self.splitter.addWidget(self.tv_classes)

        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.tb_new.setText(QCoreApplication.translate("Form", "New", None))

    # retranslateUi
