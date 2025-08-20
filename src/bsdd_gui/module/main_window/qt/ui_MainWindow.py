# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
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
    QAction,
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
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from som_gui.module.class_tree.ui import ClassView
from som_gui.module.property_set.ui import PsetTableWidget
from som_gui.module.property_table.ui import PropertyTable


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1510, 754)
        MainWindow.setMinimumSize(QSize(0, 0))
        self.actiondqwd = QAction(MainWindow)
        self.actiondqwd.setObjectName("actiondqwd")
        self.verticalLayout_main = QWidget(MainWindow)
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.verticalLayout = QVBoxLayout(self.verticalLayout_main)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QSplitter(self.verticalLayout_main)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_classes = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_classes.setObjectName("verticalLayout_classes")
        self.verticalLayout_classes.setContentsMargins(0, 0, 5, 0)
        self.gridLayout_classes = QGridLayout()
        self.gridLayout_classes.setObjectName("gridLayout_classes")
        self.label_class = QLabel(self.layoutWidget)
        self.label_class.setObjectName("label_class")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_class.sizePolicy().hasHeightForWidth())
        self.label_class.setSizePolicy(sizePolicy)
        self.label_class.setMinimumSize(QSize(30, 0))
        self.label_class.setLineWidth(1)

        self.gridLayout_classes.addWidget(self.label_class, 0, 1, 1, 1)

        self.button_classes_add = QPushButton(self.layoutWidget)
        self.button_classes_add.setObjectName("button_classes_add")
        self.button_classes_add.setAutoDefault(True)

        self.gridLayout_classes.addWidget(self.button_classes_add, 0, 3, 1, 1)

        self.button_search = QPushButton(self.layoutWidget)
        self.button_search.setObjectName("button_search")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.button_search.sizePolicy().hasHeightForWidth()
        )
        self.button_search.setSizePolicy(sizePolicy1)
        self.button_search.setMinimumSize(QSize(24, 0))
        self.button_search.setMaximumSize(QSize(24, 24))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditFind))
        self.button_search.setIcon(icon)
        self.button_search.setIconSize(QSize(16, 16))

        self.gridLayout_classes.addWidget(self.button_search, 0, 0, 1, 1)

        self.label_class_name = QLabel(self.layoutWidget)
        self.label_class_name.setObjectName("label_class_name")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.label_class_name.sizePolicy().hasHeightForWidth()
        )
        self.label_class_name.setSizePolicy(sizePolicy2)

        self.gridLayout_classes.addWidget(self.label_class_name, 0, 2, 1, 1)

        self.verticalLayout_classes.addLayout(self.gridLayout_classes)

        self.tree_class = ClassView(self.layoutWidget)
        self.tree_class.setObjectName("tree_class")
        self.tree_class.setEnabled(True)
        self.tree_class.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_class.setAcceptDrops(True)
        self.tree_class.setDragEnabled(True)
        self.tree_class.setDragDropOverwriteMode(False)
        self.tree_class.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.tree_class.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.tree_class.setAlternatingRowColors(False)
        self.tree_class.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.tree_class.setSortingEnabled(True)
        self.tree_class.setExpandsOnDoubleClick(False)

        self.verticalLayout_classes.addWidget(self.tree_class)

        self.splitter.addWidget(self.layoutWidget)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.vertical_layout_pset = QVBoxLayout(self.verticalLayoutWidget)
        self.vertical_layout_pset.setObjectName("vertical_layout_pset")
        self.vertical_layout_pset.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_pSet_button = QHBoxLayout()
        self.horizontalLayout_pSet_button.setObjectName("horizontalLayout_pSet_button")
        self.label_pset = QLabel(self.verticalLayoutWidget)
        self.label_pset.setObjectName("label_pset")
        self.label_pset.setMinimumSize(QSize(30, 0))

        self.horizontalLayout_pSet_button.addWidget(self.label_pset)

        self.label_pset_name = QLabel(self.verticalLayoutWidget)
        self.label_pset_name.setObjectName("label_pset_name")
        sizePolicy2.setHeightForWidth(
            self.label_pset_name.sizePolicy().hasHeightForWidth()
        )
        self.label_pset_name.setSizePolicy(sizePolicy2)

        self.horizontalLayout_pSet_button.addWidget(self.label_pset_name)

        self.button_Pset_add = QPushButton(self.verticalLayoutWidget)
        self.button_Pset_add.setObjectName("button_Pset_add")
        sizePolicy.setHeightForWidth(
            self.button_Pset_add.sizePolicy().hasHeightForWidth()
        )
        self.button_Pset_add.setSizePolicy(sizePolicy)
        self.button_Pset_add.setAutoDefault(True)

        self.horizontalLayout_pSet_button.addWidget(self.button_Pset_add)

        self.vertical_layout_pset.addLayout(self.horizontalLayout_pSet_button)

        self.table_pset = PsetTableWidget(self.verticalLayoutWidget)
        if self.table_pset.columnCount() < 3:
            self.table_pset.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.table_pset.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table_pset.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.table_pset.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.table_pset.setObjectName("table_pset")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.table_pset.sizePolicy().hasHeightForWidth())
        self.table_pset.setSizePolicy(sizePolicy3)
        self.table_pset.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table_pset.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_pset.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_pset.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table_pset.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_pset.horizontalHeader().setStretchLastSection(True)
        self.table_pset.verticalHeader().setVisible(False)
        self.table_pset.verticalHeader().setCascadingSectionResizes(False)

        self.vertical_layout_pset.addWidget(self.table_pset)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.vertical_layout_properties = QVBoxLayout(self.verticalLayoutWidget_2)
        self.vertical_layout_properties.setObjectName("vertical_layout_properties")
        self.vertical_layout_properties.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_properties = QHBoxLayout()
        self.horizontalLayout_properties.setObjectName("horizontalLayout_properties")
        self.label = QLabel(self.verticalLayoutWidget_2)
        self.label.setObjectName("label")

        self.horizontalLayout_properties.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_properties.addItem(self.horizontalSpacer)

        self.button_property_add = QPushButton(self.verticalLayoutWidget_2)
        self.button_property_add.setObjectName("button_property_add")

        self.horizontalLayout_properties.addWidget(self.button_property_add)

        self.vertical_layout_properties.addLayout(self.horizontalLayout_properties)

        self.table_property = PropertyTable(self.verticalLayoutWidget_2)
        self.table_property.setObjectName("table_property")
        self.table_property.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_property.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table_property.setDragEnabled(True)
        self.table_property.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.table_property.setSortingEnabled(True)
        self.table_property.horizontalHeader().setStretchLastSection(True)

        self.vertical_layout_properties.addWidget(self.table_property)

        self.splitter.addWidget(self.verticalLayoutWidget_2)

        self.verticalLayout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.verticalLayout_main)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1510, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuExport = QMenu(self.menuFile)
        self.menuExport.setObjectName("menuExport")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuDesite = QMenu(self.menubar)
        self.menuDesite.setObjectName("menuDesite")
        self.menuModels = QMenu(self.menubar)
        self.menuModels.setObjectName("menuModels")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.button_classes_add, self.tree_class)
        QWidget.setTabOrder(self.tree_class, self.button_search)
        QWidget.setTabOrder(self.button_search, self.button_Pset_add)
        QWidget.setTabOrder(self.button_Pset_add, self.table_property)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuModels.menuAction())
        self.menubar.addAction(self.menuDesite.menuAction())
        self.menuFile.addAction(self.menuExport.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "SOMToolkit", None)
        )
        self.actiondqwd.setText(QCoreApplication.translate("MainWindow", "dqwd", None))
        self.label_class.setText(
            QCoreApplication.translate("MainWindow", "Class:", None)
        )
        self.button_classes_add.setText(
            QCoreApplication.translate("MainWindow", "New", None)
        )
        self.button_search.setText("")
        self.label_class_name.setText("")
        self.label_pset.setText(
            QCoreApplication.translate("MainWindow", "PropertySet:", None)
        )
        self.label_pset_name.setText("")
        self.button_Pset_add.setText(
            QCoreApplication.translate("MainWindow", "New", None)
        )
        ___qtablewidgetitem = self.table_pset.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MainWindow", "PropertySet", None)
        )
        ___qtablewidgetitem1 = self.table_pset.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", "Inherited By", None)
        )
        ___qtablewidgetitem2 = self.table_pset.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("MainWindow", "Optional", None)
        )
        self.label.setText(QCoreApplication.translate("MainWindow", "Property:", None))
        self.button_property_add.setText(
            QCoreApplication.translate("MainWindow", "New", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuExport.setTitle(
            QCoreApplication.translate("MainWindow", "Export", None)
        )
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", "Edit", None))
        self.menuDesite.setTitle(
            QCoreApplication.translate("MainWindow", "Desite", None)
        )
        self.menuModels.setTitle(
            QCoreApplication.translate("MainWindow", "Models", None)
        )

    # retranslateUi
