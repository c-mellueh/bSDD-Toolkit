# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
    QFrame,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class Ui_SettingsSidebar(object):
    def setupUi(self, SettingsSidebar):
        if not SettingsSidebar.objectName():
            SettingsSidebar.setObjectName("SettingsSidebar")
        SettingsSidebar.resize(772, 942)
        SettingsSidebar.setStyleSheet(
            " QWidget#SettingsSidebar {\n" "                background: transparent; }"
        )
        self.horizontalLayout = QHBoxLayout(SettingsSidebar)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.button_layout = QVBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.expand_button = QToolButton(SettingsSidebar)
        self.expand_button.setObjectName("expand_button")
        self.expand_button.setStyleSheet(
            "QToolButton {\n"
            "    background: transparent;\n"
            "    border: none;\n"
            "    padding: 0px;\n"
            "}"
        )
        self.expand_button.setIconSize(QSize(20, 20))
        self.expand_button.setCheckable(True)
        self.expand_button.setChecked(False)
        self.expand_button.setArrowType(Qt.ArrowType.NoArrow)

        self.button_layout.addWidget(self.expand_button)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.button_layout.addItem(self.verticalSpacer)

        self.horizontalLayout.addLayout(self.button_layout)

        self.scroll_area = QScrollArea(SettingsSidebar)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_content.setGeometry(QRect(0, 0, 744, 942))
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setObjectName("scroll_layout")
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scroll_content)

        self.horizontalLayout.addWidget(self.scroll_area)

        self.retranslateUi(SettingsSidebar)

        QMetaObject.connectSlotsByName(SettingsSidebar)

    # setupUi

    def retranslateUi(self, SettingsSidebar):
        SettingsSidebar.setWindowTitle(QCoreApplication.translate("SettingsSidebar", "Form", None))
        # if QT_CONFIG(tooltip)
        self.expand_button.setToolTip(
            QCoreApplication.translate("SettingsSidebar", "Show/Hide Settings", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.expand_button.setText("")

    # retranslateUi
