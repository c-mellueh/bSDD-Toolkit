# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Window.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QSplitter, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget)

from bsdd_gui.module.allowed_values_table_view.ui import AllowedValuesTable
from bsdd_gui.module.relationship_editor_widget.ui import RelationshipWidget
from bsdd_gui.presets.ui_presets import (ComboBoxWithToggleSwitch, DateTimeWithNow, TagInput, ToggleSwitch)

class Ui_PropertyWindow(object):
    def setupUi(self, PropertyWindow):
        if not PropertyWindow.objectName():
            PropertyWindow.setObjectName(u"PropertyWindow")
        PropertyWindow.resize(631, 765)
        self.verticalLayout = QVBoxLayout(PropertyWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(PropertyWindow)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setStyleSheet(u"")
        self.tab_basics = QWidget()
        self.tab_basics.setObjectName(u"tab_basics")
        self.verticalLayout_6 = QVBoxLayout(self.tab_basics)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.gb_basics = QGroupBox(self.tab_basics)
        self.gb_basics.setObjectName(u"gb_basics")
        self.verticalLayout_2 = QVBoxLayout(self.gb_basics)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.fl_code = QFormLayout()
        self.fl_code.setObjectName(u"fl_code")
        self.fl_code.setFormAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.le_code = QLineEdit(self.gb_basics)
        self.le_code.setObjectName(u"le_code")

        self.fl_code.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_code)

        self.lb_code = QLabel(self.gb_basics)
        self.lb_code.setObjectName(u"lb_code")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lb_code.sizePolicy().hasHeightForWidth())
        self.lb_code.setSizePolicy(sizePolicy)

        self.fl_code.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_code)

        self.le_name = QLineEdit(self.gb_basics)
        self.le_name.setObjectName(u"le_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.le_name.sizePolicy().hasHeightForWidth())
        self.le_name.setSizePolicy(sizePolicy1)
        self.le_name.setMinimumSize(QSize(350, 0))

        self.fl_code.setWidget(1, QFormLayout.ItemRole.FieldRole, self.le_name)

        self.lb_unit = QLabel(self.gb_basics)
        self.lb_unit.setObjectName(u"lb_unit")

        self.fl_code.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lb_unit)

        self.ti_units = TagInput(self.gb_basics)
        self.ti_units.setObjectName(u"ti_units")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.ti_units.sizePolicy().hasHeightForWidth())
        self.ti_units.setSizePolicy(sizePolicy2)

        self.fl_code.setWidget(2, QFormLayout.ItemRole.FieldRole, self.ti_units)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lb_datatype = QLabel(self.gb_basics)
        self.lb_datatype.setObjectName(u"lb_datatype")

        self.horizontalLayout.addWidget(self.lb_datatype)

        self.cb_datatype = QComboBox(self.gb_basics)
        self.cb_datatype.addItem("")
        self.cb_datatype.addItem("")
        self.cb_datatype.addItem("")
        self.cb_datatype.addItem("")
        self.cb_datatype.addItem("")
        self.cb_datatype.addItem("")
        self.cb_datatype.setObjectName(u"cb_datatype")
        sizePolicy1.setHeightForWidth(self.cb_datatype.sizePolicy().hasHeightForWidth())
        self.cb_datatype.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.cb_datatype)

        self.lb_value_kind = QLabel(self.gb_basics)
        self.lb_value_kind.setObjectName(u"lb_value_kind")

        self.horizontalLayout.addWidget(self.lb_value_kind)

        self.cb_value_kind = QComboBox(self.gb_basics)
        self.cb_value_kind.addItem("")
        self.cb_value_kind.addItem("")
        self.cb_value_kind.addItem("")
        self.cb_value_kind.addItem("")
        self.cb_value_kind.addItem("")
        self.cb_value_kind.setObjectName(u"cb_value_kind")
        sizePolicy1.setHeightForWidth(self.cb_value_kind.sizePolicy().hasHeightForWidth())
        self.cb_value_kind.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.cb_value_kind)

        self.lb_status = QLabel(self.gb_basics)
        self.lb_status.setObjectName(u"lb_status")

        self.horizontalLayout.addWidget(self.lb_status)

        self.cb_status = QComboBox(self.gb_basics)
        self.cb_status.addItem("")
        self.cb_status.addItem("")
        self.cb_status.setObjectName(u"cb_status")
        sizePolicy1.setHeightForWidth(self.cb_status.sizePolicy().hasHeightForWidth())
        self.cb_status.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.cb_status)


        self.fl_code.setLayout(3, QFormLayout.ItemRole.SpanningRole, self.horizontalLayout)

        self.lb_property_reference = QLabel(self.gb_basics)
        self.lb_property_reference.setObjectName(u"lb_property_reference")

        self.fl_code.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_property_reference)


        self.verticalLayout_2.addLayout(self.fl_code)


        self.verticalLayout_6.addWidget(self.gb_basics)

        self.gb_values = QGroupBox(self.tab_basics)
        self.gb_values.setObjectName(u"gb_values")
        self.vl_values = QVBoxLayout(self.gb_values)
        self.vl_values.setObjectName(u"vl_values")
        self.hl_value_description = QHBoxLayout()
        self.hl_value_description.setObjectName(u"hl_value_description")
        self.pb_new_value = QPushButton(self.gb_values)
        self.pb_new_value.setObjectName(u"pb_new_value")
        self.pb_new_value.setMaximumSize(QSize(24, 24))

        self.hl_value_description.addWidget(self.pb_new_value)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_value_description.addItem(self.horizontalSpacer)


        self.vl_values.addLayout(self.hl_value_description)

        self.tv_allowed_values = AllowedValuesTable(self.gb_values)
        self.tv_allowed_values.setObjectName(u"tv_allowed_values")

        self.vl_values.addWidget(self.tv_allowed_values)


        self.verticalLayout_6.addWidget(self.gb_values)

        self.tabWidget.addTab(self.tab_basics, "")
        self.tab_def_and_rel = QWidget()
        self.tab_def_and_rel.setObjectName(u"tab_def_and_rel")
        self.verticalLayout_5 = QVBoxLayout(self.tab_def_and_rel)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter_2 = QSplitter(self.tab_def_and_rel)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Vertical)
        self.gb_relations = QGroupBox(self.splitter_2)
        self.gb_relations.setObjectName(u"gb_relations")
        self.verticalLayout_4 = QVBoxLayout(self.gb_relations)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.relationship_widget = RelationshipWidget(self.gb_relations)
        self.relationship_widget.setObjectName(u"relationship_widget")

        self.verticalLayout_4.addWidget(self.relationship_widget)

        self.line = QFrame(self.gb_relations)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.splitter_2.addWidget(self.gb_relations)
        self.gb_description = QGroupBox(self.splitter_2)
        self.gb_description.setObjectName(u"gb_description")
        self.verticalLayout_3 = QVBoxLayout(self.gb_description)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.te_definition = QTextEdit(self.gb_description)
        self.te_definition.setObjectName(u"te_definition")
        self.te_definition.setAutoFillBackground(True)
        self.te_definition.setStyleSheet(u"background-color:\n"
"                                                            rgba(0, 0, 0,10);")

        self.verticalLayout_3.addWidget(self.te_definition)

        self.hl_defintion = QHBoxLayout()
        self.hl_defintion.setObjectName(u"hl_defintion")
        self.lb_description = QLabel(self.gb_description)
        self.lb_description.setObjectName(u"lb_description")

        self.hl_defintion.addWidget(self.lb_description)

        self.cb_description = ToggleSwitch(self.gb_description)
        self.cb_description.setObjectName(u"cb_description")

        self.hl_defintion.addWidget(self.cb_description)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_defintion.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.hl_defintion)

        self.te_description = QTextEdit(self.gb_description)
        self.te_description.setObjectName(u"te_description")
        self.te_description.setStyleSheet(u"background-color:\n"
"                                                            rgba(0, 0, 0,10);")

        self.verticalLayout_3.addWidget(self.te_description)

        self.splitter_2.addWidget(self.gb_description)

        self.verticalLayout_5.addWidget(self.splitter_2)

        self.tabWidget.addTab(self.tab_def_and_rel, "")
        self.tab_advanced = QWidget()
        self.tab_advanced.setObjectName(u"tab_advanced")
        self.formLayout = QFormLayout(self.tab_advanced)
        self.formLayout.setObjectName(u"formLayout")
        self.lb_example = QLabel(self.tab_advanced)
        self.lb_example.setObjectName(u"lb_example")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_example)

        self.le_example = QLineEdit(self.tab_advanced)
        self.le_example.setObjectName(u"le_example")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_example)

        self.lb_activation_time = QLabel(self.tab_advanced)
        self.lb_activation_time.setObjectName(u"lb_activation_time")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_activation_time)

        self.lb_connected_properties = QLabel(self.tab_advanced)
        self.lb_connected_properties.setObjectName(u"lb_connected_properties")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lb_connected_properties)

        self.ti_connect_properties = TagInput(self.tab_advanced)
        self.ti_connect_properties.setObjectName(u"ti_connect_properties")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.ti_connect_properties)

        self.lb_country_use = QLabel(self.tab_advanced)
        self.lb_country_use.setObjectName(u"lb_country_use")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lb_country_use)

        self.ti_countries = TagInput(self.tab_advanced)
        self.ti_countries.setObjectName(u"ti_countries")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.ti_countries)

        self.lb_country_origin = QLabel(self.tab_advanced)
        self.lb_country_origin.setObjectName(u"lb_country_origin")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lb_country_origin)

        self.cb_country_origin = ComboBoxWithToggleSwitch(self.tab_advanced)
        self.cb_country_origin.setObjectName(u"cb_country_origin")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.cb_country_origin)

        self.lb_creator_iso = QLabel(self.tab_advanced)
        self.lb_creator_iso.setObjectName(u"lb_creator_iso")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lb_creator_iso)

        self.cb_creator_iso = QComboBox(self.tab_advanced)
        self.cb_creator_iso.setObjectName(u"cb_creator_iso")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.cb_creator_iso)

        self.lb_deactivation_time = QLabel(self.tab_advanced)
        self.lb_deactivation_time.setObjectName(u"lb_deactivation_time")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lb_deactivation_time)

        self.lb_document_ref = QLabel(self.tab_advanced)
        self.lb_document_ref.setObjectName(u"lb_document_ref")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lb_document_ref)

        self.cb_document_ref = QComboBox(self.tab_advanced)
        self.cb_document_ref.setObjectName(u"cb_document_ref")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.cb_document_ref)

        self.lb_measurement = QLabel(self.tab_advanced)
        self.lb_measurement.setObjectName(u"lb_measurement")

        self.formLayout.setWidget(10, QFormLayout.ItemRole.LabelRole, self.lb_measurement)

        self.le_measurement = QLineEdit(self.tab_advanced)
        self.le_measurement.setObjectName(u"le_measurement")

        self.formLayout.setWidget(10, QFormLayout.ItemRole.FieldRole, self.le_measurement)

        self.lb_replaced_objects = QLabel(self.tab_advanced)
        self.lb_replaced_objects.setObjectName(u"lb_replaced_objects")

        self.formLayout.setWidget(11, QFormLayout.ItemRole.LabelRole, self.lb_replaced_objects)

        self.lb_replacing_objects = QLabel(self.tab_advanced)
        self.lb_replacing_objects.setObjectName(u"lb_replacing_objects")

        self.formLayout.setWidget(12, QFormLayout.ItemRole.LabelRole, self.lb_replacing_objects)

        self.ti_replaced_objects = TagInput(self.tab_advanced)
        self.ti_replaced_objects.setObjectName(u"ti_replaced_objects")

        self.formLayout.setWidget(11, QFormLayout.ItemRole.FieldRole, self.ti_replaced_objects)

        self.ti_replacing_objects = TagInput(self.tab_advanced)
        self.ti_replacing_objects.setObjectName(u"ti_replacing_objects")

        self.formLayout.setWidget(12, QFormLayout.ItemRole.FieldRole, self.ti_replacing_objects)

        self.lb_revision_date = QLabel(self.tab_advanced)
        self.lb_revision_date.setObjectName(u"lb_revision_date")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lb_revision_date)

        self.lb_subdivision = QLabel(self.tab_advanced)
        self.lb_subdivision.setObjectName(u"lb_subdivision")

        self.formLayout.setWidget(13, QFormLayout.ItemRole.LabelRole, self.lb_subdivision)

        self.ti_subdivision = TagInput(self.tab_advanced)
        self.ti_subdivision.setObjectName(u"ti_subdivision")

        self.formLayout.setWidget(13, QFormLayout.ItemRole.FieldRole, self.ti_subdivision)

        self.lb_text_format = QLabel(self.tab_advanced)
        self.lb_text_format.setObjectName(u"lb_text_format")

        self.formLayout.setWidget(14, QFormLayout.ItemRole.LabelRole, self.lb_text_format)

        self.le_text_format = QLineEdit(self.tab_advanced)
        self.le_text_format.setObjectName(u"le_text_format")

        self.formLayout.setWidget(14, QFormLayout.ItemRole.FieldRole, self.le_text_format)

        self.lb_uid = QLabel(self.tab_advanced)
        self.lb_uid.setObjectName(u"lb_uid")

        self.formLayout.setWidget(15, QFormLayout.ItemRole.LabelRole, self.lb_uid)

        self.le_uid = QLineEdit(self.tab_advanced)
        self.le_uid.setObjectName(u"le_uid")

        self.formLayout.setWidget(15, QFormLayout.ItemRole.FieldRole, self.le_uid)

        self.lb_version_date = QLabel(self.tab_advanced)
        self.lb_version_date.setObjectName(u"lb_version_date")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lb_version_date)

        self.lb_version_number = QLabel(self.tab_advanced)
        self.lb_version_number.setObjectName(u"lb_version_number")

        self.formLayout.setWidget(16, QFormLayout.ItemRole.LabelRole, self.lb_version_number)

        self.sb_version_number = QSpinBox(self.tab_advanced)
        self.sb_version_number.setObjectName(u"sb_version_number")

        self.formLayout.setWidget(16, QFormLayout.ItemRole.FieldRole, self.sb_version_number)

        self.lb_visual_rep = QLabel(self.tab_advanced)
        self.lb_visual_rep.setObjectName(u"lb_visual_rep")

        self.formLayout.setWidget(17, QFormLayout.ItemRole.LabelRole, self.lb_visual_rep)

        self.le_visual_rep = QLineEdit(self.tab_advanced)
        self.le_visual_rep.setObjectName(u"le_visual_rep")

        self.formLayout.setWidget(17, QFormLayout.ItemRole.FieldRole, self.le_visual_rep)

        self.de_activation_time = DateTimeWithNow(self.tab_advanced)
        self.de_activation_time.setObjectName(u"de_activation_time")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.de_activation_time)

        self.de_revision_time = DateTimeWithNow(self.tab_advanced)
        self.de_revision_time.setObjectName(u"de_revision_time")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.de_revision_time)

        self.de_deactivation_time = DateTimeWithNow(self.tab_advanced)
        self.de_deactivation_time.setObjectName(u"de_deactivation_time")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.de_deactivation_time)

        self.de_version_date = DateTimeWithNow(self.tab_advanced)
        self.de_version_date.setObjectName(u"de_version_date")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.de_version_date)

        self.tabWidget.addTab(self.tab_advanced, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(PropertyWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(PropertyWindow)
    # setupUi

    def retranslateUi(self, PropertyWindow):
        PropertyWindow.setWindowTitle(QCoreApplication.translate("PropertyWindow", u"Form", None))
        self.gb_basics.setTitle("")
        self.le_code.setPlaceholderText(QCoreApplication.translate("PropertyWindow", u"Code", None))
#if QT_CONFIG(tooltip)
        self.lb_code.setToolTip(QCoreApplication.translate("PropertyWindow", u"Name of the Property\n"
"                                                                Example: \"IsExternal\"", None))
#endif // QT_CONFIG(tooltip)
        self.lb_code.setText(QCoreApplication.translate("PropertyWindow", u"Name:", None))
        self.le_name.setPlaceholderText(QCoreApplication.translate("PropertyWindow", u"Name", None))
#if QT_CONFIG(tooltip)
        self.lb_unit.setToolTip(QCoreApplication.translate("PropertyWindow", u"The units represent a scale\n"
"                                                                that enables a value to be\n"
"                                                                measured (ISO 80000 or ISO 4217,\n"
"                                                                or ISO 8601). List of values.\n"
"                                                                See reference list (JSON) units.\n"
"                                                                We are working on supporting the\n"
"                                                                QUDT vocabulary. If you would\n"
"                                                                like to import using QUDT units\n"
"                                                                or want to have the QUDT units\n"
"                                                                in the API output, please let us\n"
"                                                                know.", None))
#endif // QT_CONFIG(tooltip)
        self.lb_unit.setText(QCoreApplication.translate("PropertyWindow", u"Units:", None))
        self.lb_datatype.setText(QCoreApplication.translate("PropertyWindow", u"Datatype:", None))
        self.cb_datatype.setItemText(0, QCoreApplication.translate("PropertyWindow", u"Boolean", None))
        self.cb_datatype.setItemText(1, QCoreApplication.translate("PropertyWindow", u"Character", None))
        self.cb_datatype.setItemText(2, QCoreApplication.translate("PropertyWindow", u"Integer", None))
        self.cb_datatype.setItemText(3, QCoreApplication.translate("PropertyWindow", u"Real", None))
        self.cb_datatype.setItemText(4, QCoreApplication.translate("PropertyWindow", u"String", None))
        self.cb_datatype.setItemText(5, QCoreApplication.translate("PropertyWindow", u"Time", None))

#if QT_CONFIG(tooltip)
        self.lb_value_kind.setToolTip(QCoreApplication.translate("PropertyWindow", u"Must be one of:\n"
"                                                                        Single (one value; this\n"
"                                                                        is the default), Range\n"
"                                                                        (two values), List\n"
"                                                                        (multiple values),\n"
"                                                                        Complex (neither\n"
"                                                                        single/range/list, for\n"
"                                                                        example an object like\n"
"                                                                        IfcActor or an\n"
"                                                                        aggregation of connected\n"
"                                                                        properties - see\n"
"                                        "
                        "                                assembling properties),\n"
"                                                                        ComplexList (list of\n"
"                                                                        complex values).", None))
#endif // QT_CONFIG(tooltip)
        self.lb_value_kind.setText(QCoreApplication.translate("PropertyWindow", u"Property Value Kind:", None))
        self.cb_value_kind.setItemText(0, QCoreApplication.translate("PropertyWindow", u"Single", None))
        self.cb_value_kind.setItemText(1, QCoreApplication.translate("PropertyWindow", u"Range", None))
        self.cb_value_kind.setItemText(2, QCoreApplication.translate("PropertyWindow", u"List", None))
        self.cb_value_kind.setItemText(3, QCoreApplication.translate("PropertyWindow", u"Complex", None))
        self.cb_value_kind.setItemText(4, QCoreApplication.translate("PropertyWindow", u"ComplexList", None))

#if QT_CONFIG(tooltip)
        self.cb_value_kind.setToolTip(QCoreApplication.translate("PropertyWindow", u"Must be one of:\n"
"                                                                        Single (one value; this\n"
"                                                                        is the default), Range\n"
"                                                                        (two values), List\n"
"                                                                        (multiple values),\n"
"                                                                        Complex (neither\n"
"                                                                        single/range/list, for\n"
"                                                                        example an object like\n"
"                                                                        IfcActor or an\n"
"                                                                        aggregation of connected\n"
"                                                                        properties - see\n"
"                                        "
                        "                                assembling properties),\n"
"                                                                        ComplexList (list of\n"
"                                                                        complex values).", None))
#endif // QT_CONFIG(tooltip)
        self.lb_status.setText(QCoreApplication.translate("PropertyWindow", u"Status:", None))
        self.cb_status.setItemText(0, QCoreApplication.translate("PropertyWindow", u"Active", None))
        self.cb_status.setItemText(1, QCoreApplication.translate("PropertyWindow", u"Inactive", None))

#if QT_CONFIG(tooltip)
        self.lb_property_reference.setToolTip(QCoreApplication.translate("PropertyWindow", u"Unique identification of the\n"
"                                                                property within the dictionary.\n"
"                                                                Example:\n"
"                                                                \"abc-00123-01\" or\n"
"                                                                \"SpecialWidth\".", None))
#endif // QT_CONFIG(tooltip)
        self.lb_property_reference.setText(QCoreApplication.translate("PropertyWindow", u"Code:", None))
        self.gb_values.setTitle(QCoreApplication.translate("PropertyWindow", u"Allowed Values", None))
        self.pb_new_value.setText(QCoreApplication.translate("PropertyWindow", u"+", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_basics), QCoreApplication.translate("PropertyWindow", u"Basics", None))
        self.gb_relations.setTitle(QCoreApplication.translate("PropertyWindow", u"PropertyRelations", None))
        self.gb_description.setTitle(QCoreApplication.translate("PropertyWindow", u"Definition", None))
        self.lb_description.setText(QCoreApplication.translate("PropertyWindow", u"Description", None))
        self.cb_description.setText(QCoreApplication.translate("PropertyWindow", u"Description:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_def_and_rel), QCoreApplication.translate("PropertyWindow", u"Definitions and Relations", None))
#if QT_CONFIG(tooltip)
        self.lb_example.setToolTip(QCoreApplication.translate("PropertyWindow", u"Example value of the Property", None))
#endif // QT_CONFIG(tooltip)
        self.lb_example.setText(QCoreApplication.translate("PropertyWindow", u"Example:", None))
        self.lb_activation_time.setText(QCoreApplication.translate("PropertyWindow", u"Activation Date:", None))
#if QT_CONFIG(tooltip)
        self.lb_connected_properties.setToolTip(QCoreApplication.translate("PropertyWindow", u" List of codes of one or more connected properties.\n"
"                                            Can also be full URI instead of code, in case it is a\n"
"                                            property of another dictionary.", None))
#endif // QT_CONFIG(tooltip)
        self.lb_connected_properties.setText(QCoreApplication.translate("PropertyWindow", u"Connected Property Codes:", None))
#if QT_CONFIG(tooltip)
        self.lb_country_use.setToolTip(QCoreApplication.translate("PropertyWindow", u"List of country ISO codes this Property is being\n"
"                                            used.", None))
#endif // QT_CONFIG(tooltip)
        self.lb_country_use.setText(QCoreApplication.translate("PropertyWindow", u"Countries of Use:", None))
#if QT_CONFIG(tooltip)
        self.lb_country_origin.setToolTip(QCoreApplication.translate("PropertyWindow", u"ISO Country Code of the country of origin of this\n"
"                                            Property", None))
#endif // QT_CONFIG(tooltip)
        self.lb_country_origin.setText(QCoreApplication.translate("PropertyWindow", u"Country of origin:", None))
#if QT_CONFIG(tooltip)
        self.lb_creator_iso.setToolTip(QCoreApplication.translate("PropertyWindow", u"Language ISO code of the creator. ", None))
#endif // QT_CONFIG(tooltip)
        self.lb_creator_iso.setText(QCoreApplication.translate("PropertyWindow", u"Creator Language IsoCode:", None))
        self.lb_deactivation_time.setText(QCoreApplication.translate("PropertyWindow", u"De Activation Date:", None))
#if QT_CONFIG(tooltip)
        self.lb_document_ref.setToolTip(QCoreApplication.translate("PropertyWindow", u"Reference to document with the full or official\n"
"                                            definition of the Property", None))
#endif // QT_CONFIG(tooltip)
        self.lb_document_ref.setText(QCoreApplication.translate("PropertyWindow", u"Document Reference:", None))
#if QT_CONFIG(tooltip)
        self.lb_measurement.setToolTip(QCoreApplication.translate("PropertyWindow", u"Example: \"Thermal transmittance according to\n"
"                                            ISO 10077-1\"", None))
#endif // QT_CONFIG(tooltip)
        self.lb_measurement.setText(QCoreApplication.translate("PropertyWindow", u"Method of Measurement:", None))
#if QT_CONFIG(tooltip)
        self.lb_replaced_objects.setToolTip(QCoreApplication.translate("PropertyWindow", u"List of Property Codes this Property replaces", None))
#endif // QT_CONFIG(tooltip)
        self.lb_replaced_objects.setText(QCoreApplication.translate("PropertyWindow", u"Replaced Object Codes:", None))
#if QT_CONFIG(tooltip)
        self.lb_replacing_objects.setToolTip(QCoreApplication.translate("PropertyWindow", u"List of Property Codes this Property is replaced by", None))
#endif // QT_CONFIG(tooltip)
        self.lb_replacing_objects.setText(QCoreApplication.translate("PropertyWindow", u"Replacing Object Codes:", None))
        self.lb_revision_date.setText(QCoreApplication.translate("PropertyWindow", u"Revision Date:", None))
#if QT_CONFIG(tooltip)
        self.lb_subdivision.setToolTip(QCoreApplication.translate("PropertyWindow", u"List of geographical regions of use Example:\n"
"                                            \"US-MT\"", None))
#endif // QT_CONFIG(tooltip)
        self.lb_subdivision.setText(QCoreApplication.translate("PropertyWindow", u"Subdivision of Use:", None))
#if QT_CONFIG(tooltip)
        self.lb_text_format.setToolTip(QCoreApplication.translate("PropertyWindow", u"Pair for text type (encoding, number of characters)\n"
"                                            The encoding is set according to \"Name of encoding\n"
"                                            standard\" of IANA, RFC 2978, Example:\n"
"                                            \"(UTF-8,32)\"", None))
#endif // QT_CONFIG(tooltip)
        self.lb_text_format.setText(QCoreApplication.translate("PropertyWindow", u"Text Format:", None))
#if QT_CONFIG(tooltip)
        self.lb_uid.setToolTip(QCoreApplication.translate("PropertyWindow", u"Unique identification (ID), in case the URI is not\n"
"                                            enough.", None))
#endif // QT_CONFIG(tooltip)
        self.lb_uid.setText(QCoreApplication.translate("PropertyWindow", u"Uid:", None))
        self.lb_version_date.setText(QCoreApplication.translate("PropertyWindow", u"Version Date:", None))
        self.lb_version_number.setText(QCoreApplication.translate("PropertyWindow", u"Version number:", None))
        self.lb_visual_rep.setText(QCoreApplication.translate("PropertyWindow", u"Visual Representation:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_advanced), QCoreApplication.translate("PropertyWindow", u"Advanced", None))
    # retranslateUi

