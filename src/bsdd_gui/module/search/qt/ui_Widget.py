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
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QDialog,
    QGridLayout,
    QHeaderView,
    QLineEdit,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


class Ui_Search(object):
    def setupUi(self, Search):
        if not Search.objectName():
            Search.setObjectName("Search")
        Search.resize(444, 480)
        self.gridLayout = QGridLayout(Search)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit = QLineEdit(Search)
        self.lineEdit.setObjectName("lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)

        self.tableWidget = QTableWidget(Search)
        self.tableWidget.setObjectName("tableWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 2)

        self.checkBox_strict = QCheckBox(Search)
        self.checkBox_strict.setObjectName("checkBox_strict")

        self.gridLayout.addWidget(self.checkBox_strict, 0, 1, 1, 1)

        self.retranslateUi(Search)

        QMetaObject.connectSlotsByName(Search)

    # setupUi

    def retranslateUi(self, Search):
        Search.setWindowTitle(QCoreApplication.translate("Search", "Dialog", None))
        self.checkBox_strict.setText(QCoreApplication.translate("Search", "Strict", None))

    # retranslateUi
