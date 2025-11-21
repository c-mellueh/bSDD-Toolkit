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
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QToolButton,
    QWidget,
)

from bsdd_gui.module.ids_exporter.model_views import ClassView, PropertyView
from bsdd_gui.presets.ui_presets import FileSelector, ToggleSwitch


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1075, 710)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QSplitter(Form)
        self.splitter.setObjectName("splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.tv_classes = ClassView(self.splitter)
        self.tv_classes.setObjectName("tv_classes")
        self.splitter.addWidget(self.tv_classes)
        self.tv_properties = PropertyView(self.splitter)
        self.tv_properties.setObjectName("tv_properties")
        self.splitter.addWidget(self.tv_properties)
        self.fr_settings = QFrame(self.splitter)
        self.fr_settings.setObjectName("fr_settings")
        self.fr_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.fr_settings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_classification = QLabel(self.fr_settings)
        self.label_classification.setObjectName("label_classification")

        self.gridLayout_2.addWidget(self.label_classification, 1, 0, 1, 1)

        self.label = QLabel(self.fr_settings)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout_2.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.cb_classification = ToggleSwitch(self.fr_settings)
        self.cb_classification.setObjectName("cb_classification")
        self.cb_classification.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.gridLayout_2.addWidget(self.cb_classification, 1, 1, 1, 1)

        self.cb_prop = QComboBox(self.fr_settings)
        self.cb_prop.setObjectName("cb_prop")

        self.gridLayout_2.addWidget(self.cb_prop, 2, 1, 1, 1)

        self.cb_inherit = ToggleSwitch(self.fr_settings)
        self.cb_inherit.setObjectName("cb_inherit")
        self.cb_inherit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.gridLayout_2.addWidget(self.cb_inherit, 0, 1, 1, 1)

        self.cb_pset = QComboBox(self.fr_settings)
        self.cb_pset.setObjectName("cb_pset")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cb_pset.sizePolicy().hasHeightForWidth())
        self.cb_pset.setSizePolicy(sizePolicy1)
        self.cb_pset.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )

        self.gridLayout_2.addWidget(self.cb_pset, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.tb_export = QToolButton(self.fr_settings)
        self.tb_export.setObjectName("tb_export")

        self.horizontalLayout.addWidget(self.tb_export)

        self.tb_import = QToolButton(self.fr_settings)
        self.tb_import.setObjectName("tb_import")

        self.horizontalLayout.addWidget(self.tb_import)

        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 2)

        self.splitter.addWidget(self.fr_settings)

        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.fw_output = FileSelector(Form)
        self.fw_output.setObjectName("fw_output")

        self.gridLayout.addWidget(self.fw_output, 1, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        # if QT_CONFIG(tooltip)
        self.label_classification.setToolTip(
            QCoreApplication.translate(
                "Form",
                '<html><head/><body><p>When checked, the IDS-Rules will automatically evaluate all entities classified under the <span style=" font-weight:700;">bSDD classification</span>. If unchecked, you must manually specify a Property to associate the entities with a class definition.</p></body></html>',
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.label_classification.setText(
            QCoreApplication.translate("Form", "Check for Classification", None)
        )
        self.label.setText(QCoreApplication.translate("Form", "Inherit Checkstates", None))
        # if QT_CONFIG(tooltip)
        self.cb_classification.setToolTip(
            QCoreApplication.translate(
                "Form",
                '<html><head/><body><p>When checked, the IDS-Rules will automatically evaluate all entities classified under the <span style=" font-weight:700;">bSDD classification</span>. If unchecked, you must manually specify a Property to associate the entities with a class definition.</p></body></html>',
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cb_classification.setText(QCoreApplication.translate("Form", "CheckBox", None))
        self.tb_export.setText(QCoreApplication.translate("Form", "D", None))
        self.tb_import.setText(QCoreApplication.translate("Form", "U", None))

    # retranslateUi
