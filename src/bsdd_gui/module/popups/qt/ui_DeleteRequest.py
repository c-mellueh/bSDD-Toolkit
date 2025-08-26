# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DeleteRequest.ui'
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
    QAbstractButton,
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_DeleteRequest(object):
    def setupUi(self, DeleteRequest):
        if not DeleteRequest.objectName():
            DeleteRequest.setObjectName("DeleteRequest")
        DeleteRequest.resize(397, 202)
        self.verticalLayout = QVBoxLayout(DeleteRequest)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(DeleteRequest)
        self.label.setObjectName("label")

        self.verticalLayout.addWidget(self.label)

        self.listWidget = QListWidget(DeleteRequest)
        self.listWidget.setObjectName("listWidget")

        self.verticalLayout.addWidget(self.listWidget)

        self.check_box_recursion = QCheckBox(DeleteRequest)
        self.check_box_recursion.setObjectName("check_box_recursion")

        self.verticalLayout.addWidget(self.check_box_recursion)

        self.buttonBox = QDialogButtonBox(DeleteRequest)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )

        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DeleteRequest)
        self.buttonBox.accepted.connect(DeleteRequest.accept)
        self.buttonBox.rejected.connect(DeleteRequest.reject)

        QMetaObject.connectSlotsByName(DeleteRequest)

    # setupUi

    def retranslateUi(self, DeleteRequest):
        DeleteRequest.setWindowTitle(QCoreApplication.translate("DeleteRequest", "Dialog", None))
        self.label.setText(
            QCoreApplication.translate("DeleteRequest", "delete the following entities?", None)
        )
        self.check_box_recursion.setText(
            QCoreApplication.translate("DeleteRequest", "Also delete child elements?", None)
        )

    # retranslateUi
