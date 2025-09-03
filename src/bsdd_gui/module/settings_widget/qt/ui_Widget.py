# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
    QTabWidget,
    QToolBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Settings(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName("Settings")
        Settings.resize(889, 617)
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
        self.pageGeneral = QWidget()
        self.pageGeneral.setObjectName("pageGeneral")
        self.pageGeneral.setGeometry(QRect(0, 0, 856, 467))
        self.pageGeneral.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_9 = QVBoxLayout(self.pageGeneral)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.toolBox.addItem(self.pageGeneral, "General")
        self.pageLogging = QWidget()
        self.pageLogging.setObjectName("pageLogging")
        self.pageLogging.setGeometry(QRect(0, 0, 856, 467))
        self.pageLogging.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_8 = QVBoxLayout(self.pageLogging)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.toolBox.addItem(self.pageLogging, "Logging")
        self.pageFilter = QWidget()
        self.pageFilter.setObjectName("pageFilter")
        self.pageFilter.setGeometry(QRect(0, 0, 856, 467))
        self.pageFilter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_10 = QVBoxLayout(self.pageFilter)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.toolBox.addItem(self.pageFilter, "Filter")

        self.verticalLayout_4.addWidget(self.toolBox)

        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabPath = QWidget()
        self.tabPath.setObjectName("tabPath")
        self.verticalLayout_3 = QVBoxLayout(self.tabPath)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(1, 3, 1, 3)
        self.tbPath = QToolBox(self.tabPath)
        self.tbPath.setObjectName("tbPath")
        self.pageProject = QWidget()
        self.pageProject.setObjectName("pageProject")
        self.pageProject.setGeometry(QRect(0, 0, 856, 497))
        self.pageProject.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_6 = QVBoxLayout(self.pageProject)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.tbPath.addItem(self.pageProject, "Project")
        self.pageExport = QWidget()
        self.pageExport.setObjectName("pageExport")
        self.pageExport.setGeometry(QRect(0, 0, 856, 497))
        self.pageExport.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_7 = QVBoxLayout(self.pageExport)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.tbPath.addItem(self.pageExport, "Export")

        self.verticalLayout_3.addWidget(self.tbPath)

        self.tabWidget.addTab(self.tabPath, "")
        self.tabProperty = QWidget()
        self.tabProperty.setObjectName("tabProperty")
        self.verticalLayout_11 = QVBoxLayout(self.tabProperty)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.tb_property_set = QToolBox(self.tabProperty)
        self.tb_property_set.setObjectName("tb_property_set")
        self.tb_property_set.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.pageSplitter = QWidget()
        self.pageSplitter.setObjectName("pageSplitter")
        self.pageSplitter.setGeometry(QRect(0, 0, 840, 485))
        self.pageSplitter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_12 = QVBoxLayout(self.pageSplitter)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.tb_property_set.addItem(self.pageSplitter, "Splitter")
        self.pageUnits = QWidget()
        self.pageUnits.setObjectName("pageUnits")
        self.pageUnits.setGeometry(QRect(0, 0, 840, 485))
        self.pageUnits.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.pageUnits.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_13 = QVBoxLayout(self.pageUnits)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
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
        self.pagePlugins.setGeometry(QRect(0, 0, 856, 527))
        self.pagePlugins.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_5 = QVBoxLayout(self.pagePlugins)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
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
        self.tbPath.setCurrentIndex(0)
        self.tb_property_set.setCurrentIndex(1)
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
            self.toolBox.indexOf(self.pageFilter),
            QCoreApplication.translate("Settings", "Filter", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabGeneral),
            QCoreApplication.translate("Settings", "General", None),
        )
        self.tbPath.setItemText(
            self.tbPath.indexOf(self.pageProject),
            QCoreApplication.translate("Settings", "Project", None),
        )
        self.tbPath.setItemText(
            self.tbPath.indexOf(self.pageExport),
            QCoreApplication.translate("Settings", "Export", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabPath),
            QCoreApplication.translate("Settings", "Path", None),
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
