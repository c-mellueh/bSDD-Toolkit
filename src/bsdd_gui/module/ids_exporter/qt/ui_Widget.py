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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QScrollArea, QSizePolicy, QSpacerItem, QSplitter,
    QToolButton, QVBoxLayout, QWidget)

from bsdd_gui.module.ids_exporter.model_views import (ClassView, PropertyView, TagInput_IfcVersion)
from bsdd_gui.presets.ui_presets import (DateTimeWithNow, FileSelector, ToggleSwitch)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1600, 900)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

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
        self.verticalLayout.setContentsMargins(-1, 0, -1, 0)
        self.main_settings = QFrame(self.widget)
        self.main_settings.setObjectName(u"main_settings")
        self.main_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.main_settings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_classification = QLabel(self.main_settings)
        self.label_classification.setObjectName(u"label_classification")

        self.gridLayout_2.addWidget(self.label_classification, 2, 0, 1, 1)

        self.cb_clsf = ToggleSwitch(self.main_settings)
        self.cb_clsf.setObjectName(u"cb_clsf")
        self.cb_clsf.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_2.addWidget(self.cb_clsf, 2, 1, 1, 1)

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


        self.gridLayout_2.addWidget(self.widget_prop, 3, 0, 1, 2)

        self.cb_inh = ToggleSwitch(self.main_settings)
        self.cb_inh.setObjectName(u"cb_inh")
        self.cb_inh.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_2.addWidget(self.cb_inh, 1, 1, 1, 1)

        self.label = QLabel(self.main_settings)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)

        self.label_13 = QLabel(self.main_settings)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 2)


        self.verticalLayout.addWidget(self.main_settings)

        self.scrollArea = QScrollArea(self.widget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setAutoFillBackground(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 376, 660))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.ids_settings = QFrame(self.scrollAreaWidgetContents)
        self.ids_settings.setObjectName(u"ids_settings")
        self.ids_settings.setAutoFillBackground(False)
        self.ids_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.ids_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_4 = QGridLayout(self.ids_settings)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.le_desc = QLineEdit(self.ids_settings)
        self.le_desc.setObjectName(u"le_desc")

        self.gridLayout_4.addWidget(self.le_desc, 5, 0, 1, 1)

        self.label_10 = QLabel(self.ids_settings)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_4.addWidget(self.label_10, 14, 0, 1, 1)

        self.label_8 = QLabel(self.ids_settings)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_4.addWidget(self.label_8, 10, 0, 1, 1)

        self.dt_date = DateTimeWithNow(self.ids_settings)
        self.dt_date.setObjectName(u"dt_date")

        self.gridLayout_4.addWidget(self.dt_date, 11, 0, 1, 1)

        self.label_6 = QLabel(self.ids_settings)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_4.addWidget(self.label_6, 6, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(40, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 20, 0, 1, 1)

        self.label_7 = QLabel(self.ids_settings)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_4.addWidget(self.label_7, 8, 0, 1, 1)

        self.label_11 = QLabel(self.ids_settings)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_4.addWidget(self.label_11, 16, 0, 1, 1)

        self.label_4 = QLabel(self.ids_settings)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_4.addWidget(self.label_4, 2, 0, 1, 1)

        self.le_author = QLineEdit(self.ids_settings)
        self.le_author.setObjectName(u"le_author")

        self.gridLayout_4.addWidget(self.le_author, 7, 0, 1, 1)

        self.label_9 = QLabel(self.ids_settings)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_4.addWidget(self.label_9, 12, 0, 1, 1)

        self.ti_ifc_vers = TagInput_IfcVersion(self.ids_settings)
        self.ti_ifc_vers.setObjectName(u"ti_ifc_vers")

        self.gridLayout_4.addWidget(self.ti_ifc_vers, 19, 0, 1, 1)

        self.le_copyr = QLineEdit(self.ids_settings)
        self.le_copyr.setObjectName(u"le_copyr")

        self.gridLayout_4.addWidget(self.le_copyr, 17, 0, 1, 1)

        self.le_miles = QLineEdit(self.ids_settings)
        self.le_miles.setObjectName(u"le_miles")

        self.gridLayout_4.addWidget(self.le_miles, 9, 0, 1, 1)

        self.le_title = QLineEdit(self.ids_settings)
        self.le_title.setObjectName(u"le_title")

        self.gridLayout_4.addWidget(self.le_title, 3, 0, 1, 1)

        self.label_5 = QLabel(self.ids_settings)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_4.addWidget(self.label_5, 4, 0, 1, 1)

        self.le_purpose = QLineEdit(self.ids_settings)
        self.le_purpose.setObjectName(u"le_purpose")

        self.gridLayout_4.addWidget(self.le_purpose, 13, 0, 1, 1)

        self.le_version = QLineEdit(self.ids_settings)
        self.le_version.setObjectName(u"le_version")

        self.gridLayout_4.addWidget(self.le_version, 15, 0, 1, 1)

        self.label_12 = QLabel(self.ids_settings)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_4.addWidget(self.label_12, 18, 0, 1, 1)

        self.label_14 = QLabel(self.ids_settings)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.label_14, 1, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.ids_settings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.fr_download = QFrame(self.widget)
        self.fr_download.setObjectName(u"fr_download")
        self.fr_download.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_download.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.fr_download)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.tb_export = QToolButton(self.fr_download)
        self.tb_export.setObjectName(u"tb_export")

        self.horizontalLayout.addWidget(self.tb_export)

        self.tb_import = QToolButton(self.fr_download)
        self.tb_import.setObjectName(u"tb_import")

        self.horizontalLayout.addWidget(self.tb_import)


        self.verticalLayout.addWidget(self.fr_download)

        self.splitter.addWidget(self.widget)

        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Template:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Export:", None))
#if QT_CONFIG(tooltip)
        self.label_classification.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>When checked, the IDS-Rules will automatically evaluate all entities classified under the <span style=\" font-weight:700;\">bSDD classification</span>. If unchecked, you must manually specify a Property to associate the entities with a class definition.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_classification.setText(QCoreApplication.translate("Form", u"Check for Classification", None))
#if QT_CONFIG(tooltip)
        self.cb_clsf.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>When checked, the IDS-Rules will automatically evaluate all entities classified under the <span style=\" font-weight:700;\">bSDD classification</span>. If unchecked, you must manually specify a Property to associate the entities with a class definition.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cb_clsf.setText(QCoreApplication.translate("Form", u"CheckBox", None))
        self.label.setText(QCoreApplication.translate("Form", u"Inherit Checkstates", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"**Settings**", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Version", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Date", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Author", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Milestone", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Copyright", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Title", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Purpose", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Description", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"IFC-Versions", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"**IDS Metadata**", None))
        self.tb_export.setText(QCoreApplication.translate("Form", u"D", None))
        self.tb_import.setText(QCoreApplication.translate("Form", u"U", None))
    # retranslateUi

