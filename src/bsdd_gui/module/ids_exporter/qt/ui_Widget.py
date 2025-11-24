# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QSplitter,
    QToolButton, QVBoxLayout, QWidget)

from bsdd_gui.module.ids_exporter.model_views import (ClassView, PropertyView, TagInput_IfcVersion)
from bsdd_gui.presets.ui_presets import (FileSelector, ToggleSwitch)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1083, 714)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)

        self.fw_output = FileSelector(Form)
        self.fw_output.setObjectName(u"fw_output")

        self.gridLayout.addWidget(self.fw_output, 6, 0, 1, 1)

        self.fw_template = FileSelector(Form)
        self.fw_template.setObjectName(u"fw_template")

        self.gridLayout.addWidget(self.fw_template, 4, 0, 1, 1)

        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.tv_classes = ClassView(self.splitter)
        self.tv_classes.setObjectName(u"tv_classes")
        self.splitter.addWidget(self.tv_classes)
        self.tv_properties = PropertyView(self.splitter)
        self.tv_properties.setObjectName(u"tv_properties")
        self.splitter.addWidget(self.tv_properties)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.main_settings = QFrame(self.widget)
        self.main_settings.setObjectName(u"main_settings")
        self.main_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.main_settings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.cb_inherit = ToggleSwitch(self.main_settings)
        self.cb_inherit.setObjectName(u"cb_inherit")
        self.cb_inherit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_2.addWidget(self.cb_inherit, 0, 1, 1, 1)

        self.label = QLabel(self.main_settings)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_classification = QLabel(self.main_settings)
        self.label_classification.setObjectName(u"label_classification")

        self.gridLayout_2.addWidget(self.label_classification, 1, 0, 1, 1)

        self.cb_classification = ToggleSwitch(self.main_settings)
        self.cb_classification.setObjectName(u"cb_classification")
        self.cb_classification.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_2.addWidget(self.cb_classification, 1, 1, 1, 1)

        self.widget_prop = QWidget(self.main_settings)
        self.widget_prop.setObjectName(u"widget_prop")
        self.gridLayout_3 = QGridLayout(self.widget_prop)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.cb_pset = QComboBox(self.widget_prop)
        self.cb_pset.setObjectName(u"cb_pset")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cb_pset.sizePolicy().hasHeightForWidth())
        self.cb_pset.setSizePolicy(sizePolicy1)
        self.cb_pset.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)

        self.gridLayout_3.addWidget(self.cb_pset, 0, 0, 1, 1)

        self.cb_prop = QComboBox(self.widget_prop)
        self.cb_prop.setObjectName(u"cb_prop")

        self.gridLayout_3.addWidget(self.cb_prop, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.widget_prop, 2, 0, 1, 2)


        self.verticalLayout.addWidget(self.main_settings)

        self.ids_settings = QFrame(self.widget)
        self.ids_settings.setObjectName(u"ids_settings")
        self.ids_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.ids_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_4 = QGridLayout(self.ids_settings)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_12 = QLabel(self.ids_settings)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_4.addWidget(self.label_12, 16, 0, 1, 1)

        self.de_date = QDateEdit(self.ids_settings)
        self.de_date.setObjectName(u"de_date")

        self.gridLayout_4.addWidget(self.de_date, 9, 0, 1, 1)

        self.label_7 = QLabel(self.ids_settings)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_4.addWidget(self.label_7, 6, 0, 1, 1)

        self.label_4 = QLabel(self.ids_settings)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_4.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_10 = QLabel(self.ids_settings)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_4.addWidget(self.label_10, 12, 0, 1, 1)

        self.le_milestone = QLineEdit(self.ids_settings)
        self.le_milestone.setObjectName(u"le_milestone")

        self.gridLayout_4.addWidget(self.le_milestone, 7, 0, 1, 1)

        self.le_copyright = QLineEdit(self.ids_settings)
        self.le_copyright.setObjectName(u"le_copyright")

        self.gridLayout_4.addWidget(self.le_copyright, 15, 0, 1, 1)

        self.le_version = QLineEdit(self.ids_settings)
        self.le_version.setObjectName(u"le_version")

        self.gridLayout_4.addWidget(self.le_version, 13, 0, 1, 1)

        self.label_11 = QLabel(self.ids_settings)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_4.addWidget(self.label_11, 14, 0, 1, 1)

        self.le_description = QLineEdit(self.ids_settings)
        self.le_description.setObjectName(u"le_description")

        self.gridLayout_4.addWidget(self.le_description, 3, 0, 1, 1)

        self.label_6 = QLabel(self.ids_settings)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_4.addWidget(self.label_6, 4, 0, 1, 1)

        self.le_author = QLineEdit(self.ids_settings)
        self.le_author.setObjectName(u"le_author")

        self.gridLayout_4.addWidget(self.le_author, 5, 0, 1, 1)

        self.label_9 = QLabel(self.ids_settings)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_4.addWidget(self.label_9, 10, 0, 1, 1)

        self.le_title = QLineEdit(self.ids_settings)
        self.le_title.setObjectName(u"le_title")

        self.gridLayout_4.addWidget(self.le_title, 1, 0, 1, 1)

        self.Le_purpose = QLineEdit(self.ids_settings)
        self.Le_purpose.setObjectName(u"Le_purpose")

        self.gridLayout_4.addWidget(self.Le_purpose, 11, 0, 1, 1)

        self.label_5 = QLabel(self.ids_settings)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_4.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_8 = QLabel(self.ids_settings)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_4.addWidget(self.label_8, 8, 0, 1, 1)

        self.ti_ifc_versions = TagInput_IfcVersion(self.ids_settings)
        self.ti_ifc_versions.setObjectName(u"ti_ifc_versions")

        self.gridLayout_4.addWidget(self.ti_ifc_versions, 17, 0, 1, 1)


        self.verticalLayout.addWidget(self.ids_settings)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.tb_export = QToolButton(self.widget)
        self.tb_export.setObjectName(u"tb_export")

        self.horizontalLayout.addWidget(self.tb_export)

        self.tb_import = QToolButton(self.widget)
        self.tb_import.setObjectName(u"tb_import")

        self.horizontalLayout.addWidget(self.tb_import)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter.addWidget(self.widget)

        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 1)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Export:", None))
        self.label.setText(QCoreApplication.translate("Form", u"Inherit Checkstates", None))
#if QT_CONFIG(tooltip)
        self.label_classification.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>When checked, the IDS-Rules will automatically evaluate all entities classified under the <span style=\" font-weight:700;\">bSDD classification</span>. If unchecked, you must manually specify a Property to associate the entities with a class definition.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_classification.setText(QCoreApplication.translate("Form", u"Check for Classification", None))
#if QT_CONFIG(tooltip)
        self.cb_classification.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>When checked, the IDS-Rules will automatically evaluate all entities classified under the <span style=\" font-weight:700;\">bSDD classification</span>. If unchecked, you must manually specify a Property to associate the entities with a class definition.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cb_classification.setText(QCoreApplication.translate("Form", u"CheckBox", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"IFC-Versions", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Milestone", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Title", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Version", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Copyright", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Author", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Purpose", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Description", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Date", None))
        self.tb_export.setText(QCoreApplication.translate("Form", u"D", None))
        self.tb_import.setText(QCoreApplication.translate("Form", u"U", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Template:", None))
    # retranslateUi

