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
    QAbstractButton,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QToolBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Settings(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName("Settings")
        Settings.resize(893, 621)
        self.verticalLayout = QVBoxLayout(Settings)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(1, 9, 1, -1)
        self.tabWidget = QTabWidget(Settings)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.West)
        self.tabGeneral = QWidget()
        self.tabGeneral.setObjectName("tabGeneral")
        self.verticalLayout_4 = QVBoxLayout(self.tabGeneral)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(1, 3, 1, 3)
        self.toolBox = QToolBox(self.tabGeneral)
        self.toolBox.setObjectName("toolBox")
        self.toolBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.pageGeneral = QWidget()
        self.pageGeneral.setObjectName("pageGeneral")
        self.pageGeneral.setGeometry(QRect(0, 0, 860, 469))
        self.pageGeneral.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_9 = QVBoxLayout(self.pageGeneral)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_9.addItem(self.verticalSpacer)

        self.toolBox.addItem(self.pageGeneral, "General")
        self.pageLogging = QWidget()
        self.pageLogging.setObjectName("pageLogging")
        self.pageLogging.setGeometry(QRect(0, 0, 860, 469))
        self.pageLogging.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_8 = QVBoxLayout(self.pageLogging)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalSpacer_2 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_8.addItem(self.verticalSpacer_2)

        self.toolBox.addItem(self.pageLogging, "Logging")
        self.pageAI = QWidget()
        self.pageAI.setObjectName("pageAI")
        self.pageAI.setGeometry(QRect(0, 0, 860, 469))
        self.verticalLayout_14 = QVBoxLayout(self.pageAI)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.verticalSpacer_3 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_14.addItem(self.verticalSpacer_3)

        self.toolBox.addItem(self.pageAI, "OpenAI")

        self.verticalLayout_4.addWidget(self.toolBox)

        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabProperty = QWidget()
        self.tabProperty.setObjectName("tabProperty")
        self.verticalLayout_11 = QVBoxLayout(self.tabProperty)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(1, 3, 1, 3)
        self.tb_property_set = QToolBox(self.tabProperty)
        self.tb_property_set.setObjectName("tb_property_set")
        self.tb_property_set.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.pageSplitter = QWidget()
        self.pageSplitter.setObjectName("pageSplitter")
        self.pageSplitter.setGeometry(QRect(0, 0, 860, 499))
        self.pageSplitter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_12 = QVBoxLayout(self.pageSplitter)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.verticalSpacer_4 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_12.addItem(self.verticalSpacer_4)

        self.tb_property_set.addItem(self.pageSplitter, "Splitter")
        self.pageUnits = QWidget()
        self.pageUnits.setObjectName("pageUnits")
        self.pageUnits.setGeometry(QRect(0, 0, 860, 499))
        self.pageUnits.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.pageUnits.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_13 = QVBoxLayout(self.pageUnits)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.verticalSpacer_5 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_13.addItem(self.verticalSpacer_5)

        self.tb_property_set.addItem(self.pageUnits, "Units")

        self.verticalLayout_11.addWidget(self.tb_property_set)

        self.tabWidget.addTab(self.tabProperty, "")
        self.tabPlugins = QWidget()
        self.tabPlugins.setObjectName("tabPlugins")
        self.verticalLayout_2 = QVBoxLayout(self.tabPlugins)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(1, 3, 1, 3)
        self.tbPlugins = QToolBox(self.tabPlugins)
        self.tbPlugins.setObjectName("tbPlugins")
        self.pagePlugins = QWidget()
        self.pagePlugins.setObjectName("pagePlugins")
        self.pagePlugins.setGeometry(QRect(0, 0, 860, 529))
        self.pagePlugins.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_5 = QVBoxLayout(self.pagePlugins)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalSpacer_6 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_5.addItem(self.verticalSpacer_6)

        self.tbPlugins.addItem(self.pagePlugins, "Plugins")

        self.verticalLayout_2.addWidget(self.tbPlugins)

        self.tabWidget.addTab(self.tabPlugins, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(Settings)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )

        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Settings)
        self.buttonBox.accepted.connect(Settings.accept)
        self.buttonBox.rejected.connect(Settings.reject)

        self.tabWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        self.tb_property_set.setCurrentIndex(0)
        self.tbPlugins.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Settings)

    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", "Dialog", None))
        self.toolBox.setItemText(
            self.toolBox.indexOf(self.pageGeneral),
            QCoreApplication.translate("Settings", "General", None),
        )
        self.toolBox.setItemText(
            self.toolBox.indexOf(self.pageLogging),
            QCoreApplication.translate("Settings", "Logging", None),
        )
        self.toolBox.setItemText(
            self.toolBox.indexOf(self.pageAI),
            QCoreApplication.translate("Settings", "OpenAI", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabGeneral),
            QCoreApplication.translate("Settings", "General", None),
        )
        self.tb_property_set.setItemText(
            self.tb_property_set.indexOf(self.pageSplitter),
            QCoreApplication.translate("Settings", "Splitter", None),
        )
        self.tb_property_set.setItemText(
            self.tb_property_set.indexOf(self.pageUnits),
            QCoreApplication.translate("Settings", "Units", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabProperty),
            QCoreApplication.translate("Settings", "Properties", None),
        )
        self.tbPlugins.setItemText(
            self.tbPlugins.indexOf(self.pagePlugins),
            QCoreApplication.translate("Settings", "Plugins", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabPlugins),
            QCoreApplication.translate("Settings", "Plugins", None),
        )

    # retranslateUi
