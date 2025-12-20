# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QScrollArea,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)

class Ui_SettingsSidebar(object):
    def setupUi(self, SettingsSidebar):
        if not SettingsSidebar.objectName():
            SettingsSidebar.setObjectName(u"SettingsSidebar")
        SettingsSidebar.resize(772, 942)
        SettingsSidebar.setStyleSheet(u" QWidget#SettingsSidebar {\n"
"                background: transparent; }")
        self.horizontalLayout = QHBoxLayout(SettingsSidebar)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.button_layout = QVBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        self.expand_button = QToolButton(SettingsSidebar)
        self.expand_button.setObjectName(u"expand_button")
        self.expand_button.setCheckable(True)
        self.expand_button.setChecked(True)
        self.expand_button.setArrowType(Qt.ArrowType.LeftArrow)

        self.button_layout.addWidget(self.expand_button)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.button_layout.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.button_layout)

        self.scroll_area = QScrollArea(SettingsSidebar)
        self.scroll_area.setObjectName(u"scroll_area")
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName(u"scroll_content")
        self.scroll_content.setGeometry(QRect(0, 0, 741, 942))
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setObjectName(u"scroll_layout")
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scroll_content)

        self.horizontalLayout.addWidget(self.scroll_area)


        self.retranslateUi(SettingsSidebar)

        QMetaObject.connectSlotsByName(SettingsSidebar)
    # setupUi

    def retranslateUi(self, SettingsSidebar):
        SettingsSidebar.setWindowTitle(QCoreApplication.translate("SettingsSidebar", u"Form", None))
#if QT_CONFIG(tooltip)
        self.expand_button.setToolTip(QCoreApplication.translate("SettingsSidebar", u"Show/Hide Settings", None))
#endif // QT_CONFIG(tooltip)
        self.expand_button.setText(QCoreApplication.translate("SettingsSidebar", u"...", None))
    # retranslateUi

