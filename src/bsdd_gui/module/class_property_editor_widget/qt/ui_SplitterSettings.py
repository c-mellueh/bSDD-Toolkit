# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SplitterSettings.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QLineEdit,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_SplitterSettings(object):
    def setupUi(self, SplitterSettings):
        if not SplitterSettings.objectName():
            SplitterSettings.setObjectName(u"SplitterSettings")
        SplitterSettings.resize(478, 133)
        self.gridLayout = QGridLayout(SplitterSettings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.line_edit_seperator = QLineEdit(SplitterSettings)
        self.line_edit_seperator.setObjectName(u"line_edit_seperator")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_edit_seperator.sizePolicy().hasHeightForWidth())
        self.line_edit_seperator.setSizePolicy(sizePolicy)
        self.line_edit_seperator.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.line_edit_seperator, 1, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 0, 1, 2)

        self.check_box_seperator = QCheckBox(SplitterSettings)
        self.check_box_seperator.setObjectName(u"check_box_seperator")
        self.check_box_seperator.setChecked(True)

        self.gridLayout.addWidget(self.check_box_seperator, 1, 0, 1, 1)


        self.retranslateUi(SplitterSettings)

        QMetaObject.connectSlotsByName(SplitterSettings)
    # setupUi

    def retranslateUi(self, SplitterSettings):
        SplitterSettings.setWindowTitle(QCoreApplication.translate("SplitterSettings", u"Form", None))
        self.line_edit_seperator.setPlaceholderText(QCoreApplication.translate("SplitterSettings", u"Splitter text", None))
        self.check_box_seperator.setText(QCoreApplication.translate("SplitterSettings", u"Use Splitter", None))
    # retranslateUi

