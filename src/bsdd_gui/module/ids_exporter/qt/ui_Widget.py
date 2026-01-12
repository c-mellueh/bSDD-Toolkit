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
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from bsdd_gui.module.ids_exporter.model_views import ClassView, PropertyView, TagInput_IfcVersion
from bsdd_gui.presets.ui_presets import DateTimeWithNow, FileSelector, ToggleSwitch


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1600, 900)
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
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 0, -1, 0)
        self.main_settings = QFrame(self.widget)
        self.main_settings.setObjectName("main_settings")
        self.main_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.main_settings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.cb_inh = ToggleSwitch(self.main_settings)
        self.cb_inh.setObjectName("cb_inh")
        self.cb_inh.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_2.addWidget(self.cb_inh, 1, 1, 1, 1)

        self.label_13 = QLabel(self.main_settings)
        self.label_13.setObjectName("label_13")
        self.label_13.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 2)

        self.cb_clsf = ToggleSwitch(self.main_settings)
        self.cb_clsf.setObjectName("cb_clsf")
        self.cb_clsf.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.gridLayout_2.addWidget(self.cb_clsf, 3, 1, 1, 1)

        self.widget_prop = QWidget(self.main_settings)
        self.widget_prop.setObjectName("widget_prop")
        self.gridLayout_3 = QGridLayout(self.widget_prop)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.cb_prop = QComboBox(self.widget_prop)
        self.cb_prop.setObjectName("cb_prop")

        self.gridLayout_3.addWidget(self.cb_prop, 0, 1, 1, 1)

        self.cb_pset = QComboBox(self.widget_prop)
        self.cb_pset.setObjectName("cb_pset")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cb_pset.sizePolicy().hasHeightForWidth())
        self.cb_pset.setSizePolicy(sizePolicy1)
        self.cb_pset.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )

        self.gridLayout_3.addWidget(self.cb_pset, 0, 0, 1, 1)

        self.cb_datatype = QComboBox(self.widget_prop)
        self.cb_datatype.addItem("")
        self.cb_datatype.addItem("")
        self.cb_datatype.setObjectName("cb_datatype")

        self.gridLayout_3.addWidget(self.cb_datatype, 1, 1, 1, 1)

        self.label_2 = QLabel(self.widget_prop)
        self.label_2.setObjectName("label_2")

        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)

        self.gridLayout_2.addWidget(self.widget_prop, 4, 0, 1, 2)

        self.label_classification = QLabel(self.main_settings)
        self.label_classification.setObjectName("label_classification")

        self.gridLayout_2.addWidget(self.label_classification, 3, 0, 1, 1)

        self.label = QLabel(self.main_settings)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)

        self.label_15 = QLabel(self.main_settings)
        self.label_15.setObjectName("label_15")

        self.gridLayout_2.addWidget(self.label_15, 2, 0, 1, 1)

        self.cb_type_objects = ToggleSwitch(self.main_settings)
        self.cb_type_objects.setObjectName("cb_type_objects")

        self.gridLayout_2.addWidget(self.cb_type_objects, 2, 1, 1, 1)

        self.verticalLayout.addWidget(self.main_settings)

        self.scrollArea = QScrollArea(self.widget)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setAutoFillBackground(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 406, 591))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.ids_settings = QFrame(self.scrollAreaWidgetContents)
        self.ids_settings.setObjectName("ids_settings")
        self.ids_settings.setAutoFillBackground(False)
        self.ids_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.ids_settings.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_4 = QGridLayout(self.ids_settings)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.le_desc = QLineEdit(self.ids_settings)
        self.le_desc.setObjectName("le_desc")

        self.gridLayout_4.addWidget(self.le_desc, 5, 0, 1, 1)

        self.label_10 = QLabel(self.ids_settings)
        self.label_10.setObjectName("label_10")

        self.gridLayout_4.addWidget(self.label_10, 14, 0, 1, 1)

        self.label_8 = QLabel(self.ids_settings)
        self.label_8.setObjectName("label_8")

        self.gridLayout_4.addWidget(self.label_8, 10, 0, 1, 1)

        self.dt_date = DateTimeWithNow(self.ids_settings)
        self.dt_date.setObjectName("dt_date")

        self.gridLayout_4.addWidget(self.dt_date, 11, 0, 1, 1)

        self.label_6 = QLabel(self.ids_settings)
        self.label_6.setObjectName("label_6")

        self.gridLayout_4.addWidget(self.label_6, 6, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(
            40, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout_4.addItem(self.verticalSpacer, 20, 0, 1, 1)

        self.label_7 = QLabel(self.ids_settings)
        self.label_7.setObjectName("label_7")

        self.gridLayout_4.addWidget(self.label_7, 8, 0, 1, 1)

        self.label_11 = QLabel(self.ids_settings)
        self.label_11.setObjectName("label_11")

        self.gridLayout_4.addWidget(self.label_11, 16, 0, 1, 1)

        self.label_4 = QLabel(self.ids_settings)
        self.label_4.setObjectName("label_4")

        self.gridLayout_4.addWidget(self.label_4, 2, 0, 1, 1)

        self.le_author = QLineEdit(self.ids_settings)
        self.le_author.setObjectName("le_author")

        self.gridLayout_4.addWidget(self.le_author, 7, 0, 1, 1)

        self.label_9 = QLabel(self.ids_settings)
        self.label_9.setObjectName("label_9")

        self.gridLayout_4.addWidget(self.label_9, 12, 0, 1, 1)

        self.ti_ifc_vers = TagInput_IfcVersion(self.ids_settings)
        self.ti_ifc_vers.setObjectName("ti_ifc_vers")

        self.gridLayout_4.addWidget(self.ti_ifc_vers, 19, 0, 1, 1)

        self.le_copyr = QLineEdit(self.ids_settings)
        self.le_copyr.setObjectName("le_copyr")

        self.gridLayout_4.addWidget(self.le_copyr, 17, 0, 1, 1)

        self.le_miles = QLineEdit(self.ids_settings)
        self.le_miles.setObjectName("le_miles")

        self.gridLayout_4.addWidget(self.le_miles, 9, 0, 1, 1)

        self.le_title = QLineEdit(self.ids_settings)
        self.le_title.setObjectName("le_title")

        self.gridLayout_4.addWidget(self.le_title, 3, 0, 1, 1)

        self.label_5 = QLabel(self.ids_settings)
        self.label_5.setObjectName("label_5")

        self.gridLayout_4.addWidget(self.label_5, 4, 0, 1, 1)

        self.le_purpose = QLineEdit(self.ids_settings)
        self.le_purpose.setObjectName("le_purpose")

        self.gridLayout_4.addWidget(self.le_purpose, 13, 0, 1, 1)

        self.le_version = QLineEdit(self.ids_settings)
        self.le_version.setObjectName("le_version")

        self.gridLayout_4.addWidget(self.le_version, 15, 0, 1, 1)

        self.label_12 = QLabel(self.ids_settings)
        self.label_12.setObjectName("label_12")

        self.gridLayout_4.addWidget(self.label_12, 18, 0, 1, 1)

        self.label_14 = QLabel(self.ids_settings)
        self.label_14.setObjectName("label_14")
        self.label_14.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.label_14, 1, 0, 1, 1)

        self.verticalLayout_2.addWidget(self.ids_settings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.fr_download = QFrame(self.widget)
        self.fr_download.setObjectName("fr_download")
        self.fr_download.setFrameShape(QFrame.Shape.StyledPanel)
        self.fr_download.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.fr_download)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 5)
        self.horizontalSpacer = QSpacerItem(
            1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pb_import = QToolButton(self.fr_download)
        self.pb_import.setObjectName("pb_import")
        self.pb_import.setMinimumSize(QSize(30, 30))
        self.pb_import.setMaximumSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pb_import)

        self.pb_export = QToolButton(self.fr_download)
        self.pb_export.setObjectName("pb_export")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pb_export.sizePolicy().hasHeightForWidth())
        self.pb_export.setSizePolicy(sizePolicy2)
        self.pb_export.setMinimumSize(QSize(30, 30))
        self.pb_export.setMaximumSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pb_export)

        self.verticalLayout.addWidget(self.fr_download)

        self.splitter.addWidget(self.widget)

        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 1)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName("label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.fw_output = FileSelector(Form)
        self.fw_output.setObjectName("fw_output")

        self.gridLayout.addWidget(self.fw_output, 4, 0, 1, 1)

        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.button_layout.addItem(self.horizontalSpacer_2)

        self.pb_create = QPushButton(Form)
        self.pb_create.setObjectName("pb_create")

        self.button_layout.addWidget(self.pb_create)

        self.gridLayout.addLayout(self.button_layout, 5, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.label_13.setText(QCoreApplication.translate("Form", "**Settings**", None))
        # if QT_CONFIG(tooltip)
        self.cb_clsf.setToolTip(
            QCoreApplication.translate(
                "Form",
                '<html><head/><body><p>When checked, the IDS-Rules will automatically evaluate all entities classified under the <span style=" font-weight:700;">bSDD classification</span>. If unchecked, you must manually specify a Property to associate the entities with a class definition.</p></body></html>',
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cb_clsf.setText(QCoreApplication.translate("Form", "CheckBox", None))
        self.cb_datatype.setItemText(0, QCoreApplication.translate("Form", "IfcLabel", None))
        self.cb_datatype.setItemText(1, QCoreApplication.translate("Form", "IfcText", None))

        self.label_2.setText(QCoreApplication.translate("Form", "Datatype:", None))
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
        self.label_15.setToolTip(
            QCoreApplication.translate(
                "Form",
                "<html><head/><body><p>When enabled, the rules apply not only to the classes themselves, but also to their Type Objects (if they are typed).</p></body></html>",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.label_15.setText(QCoreApplication.translate("Form", "Check IfcTypeObjects", None))
        # if QT_CONFIG(tooltip)
        self.cb_type_objects.setToolTip(
            QCoreApplication.translate(
                "Form",
                "<html><head/><body><p>When enabled, the rules apply not only to the classes themselves, but also to their Type Objects (if they are typed).</p></body></html>",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.label_10.setText(QCoreApplication.translate("Form", "Version", None))
        self.label_8.setText(QCoreApplication.translate("Form", "Date", None))
        self.label_6.setText(QCoreApplication.translate("Form", "Author", None))
        self.label_7.setText(QCoreApplication.translate("Form", "Milestone", None))
        self.label_11.setText(QCoreApplication.translate("Form", "Copyright", None))
        self.label_4.setText(QCoreApplication.translate("Form", "Title", None))
        self.label_9.setText(QCoreApplication.translate("Form", "Purpose", None))
        self.label_5.setText(QCoreApplication.translate("Form", "Description", None))
        self.label_12.setText(QCoreApplication.translate("Form", "IFC-Versions", None))
        self.label_14.setText(QCoreApplication.translate("Form", "**IDS Metadata**", None))
        # if QT_CONFIG(tooltip)
        self.pb_import.setToolTip(QCoreApplication.translate("Form", "Import", None))
        # endif // QT_CONFIG(tooltip)
        self.pb_import.setText("")
        # if QT_CONFIG(tooltip)
        self.pb_export.setToolTip(QCoreApplication.translate("Form", "Export", None))
        # endif // QT_CONFIG(tooltip)
        self.pb_export.setText("")
        self.label_3.setText(QCoreApplication.translate("Form", "Export:", None))
        self.pb_create.setText(QCoreApplication.translate("Form", "Create", None))

    # retranslateUi
