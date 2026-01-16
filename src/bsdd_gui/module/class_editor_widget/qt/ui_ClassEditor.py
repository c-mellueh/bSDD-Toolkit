# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ClassEditor.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QTextEdit, QVBoxLayout, QWidget)

from bsdd_gui.module.class_editor_widget.ui import IfcTagInput
from bsdd_gui.module.relationship_editor_widget.ui import RelationshipWidget
from bsdd_gui.presets.ui_presets import (ComboBoxWithToggleSwitch, DateTimeWithNow, TagInput, ToggleSwitch)

class Ui_ClassEditor(object):
    def setupUi(self, ClassEditor):
        if not ClassEditor.objectName():
            ClassEditor.setObjectName(u"ClassEditor")
        ClassEditor.resize(650, 750)
        self.verticalLayout_5 = QVBoxLayout(ClassEditor)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.tabWidget = QTabWidget(ClassEditor)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_basics = QWidget()
        self.tab_basics.setObjectName(u"tab_basics")
        self.verticalLayout = QVBoxLayout(self.tab_basics)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gb_required = QGroupBox(self.tab_basics)
        self.gb_required.setObjectName(u"gb_required")
        self.gridLayout = QGridLayout(self.gb_required)
        self.gridLayout.setObjectName(u"gridLayout")
        self.hl_code = QHBoxLayout()
        self.hl_code.setObjectName(u"hl_code")
        self.lb_code = QLabel(self.gb_required)
        self.lb_code.setObjectName(u"lb_code")

        self.hl_code.addWidget(self.lb_code)

        self.le_code = QLineEdit(self.gb_required)
        self.le_code.setObjectName(u"le_code")

        self.hl_code.addWidget(self.le_code)


        self.gridLayout.addLayout(self.hl_code, 0, 1, 1, 1)

        self.hl_name = QHBoxLayout()
        self.hl_name.setObjectName(u"hl_name")
        self.lb_name = QLabel(self.gb_required)
        self.lb_name.setObjectName(u"lb_name")

        self.hl_name.addWidget(self.lb_name)

        self.le_name = QLineEdit(self.gb_required)
        self.le_name.setObjectName(u"le_name")

        self.hl_name.addWidget(self.le_name)


        self.gridLayout.addLayout(self.hl_name, 0, 0, 1, 1)

        self.hl_class_type = QHBoxLayout()
        self.hl_class_type.setObjectName(u"hl_class_type")
        self.lb_class_type = QLabel(self.gb_required)
        self.lb_class_type.setObjectName(u"lb_class_type")

        self.hl_class_type.addWidget(self.lb_class_type)

        self.cb_class_type = QComboBox(self.gb_required)
        self.cb_class_type.setObjectName(u"cb_class_type")

        self.hl_class_type.addWidget(self.cb_class_type)


        self.gridLayout.addLayout(self.hl_class_type, 1, 0, 1, 1)

        self.hl_status = QHBoxLayout()
        self.hl_status.setObjectName(u"hl_status")
        self.lb_status = QLabel(self.gb_required)
        self.lb_status.setObjectName(u"lb_status")

        self.hl_status.addWidget(self.lb_status)

        self.cb_status = QComboBox(self.gb_required)
        self.cb_status.setObjectName(u"cb_status")

        self.hl_status.addWidget(self.cb_status)


        self.gridLayout.addLayout(self.hl_status, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.gb_required)

        self.gb_synonyms = QGroupBox(self.tab_basics)
        self.gb_synonyms.setObjectName(u"gb_synonyms")
        self.verticalLayout_6 = QVBoxLayout(self.gb_synonyms)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.ti_synonyms = IfcTagInput(self.gb_synonyms)
        self.ti_synonyms.setObjectName(u"ti_synonyms")

        self.verticalLayout_6.addWidget(self.ti_synonyms)


        self.verticalLayout.addWidget(self.gb_synonyms)

        self.gb_ifc_entities = QGroupBox(self.tab_basics)
        self.gb_ifc_entities.setObjectName(u"gb_ifc_entities")
        self.verticalLayout_4 = QVBoxLayout(self.gb_ifc_entities)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.ti_related_ifc_entity = IfcTagInput(self.gb_ifc_entities)
        self.ti_related_ifc_entity.setObjectName(u"ti_related_ifc_entity")

        self.verticalLayout_4.addWidget(self.ti_related_ifc_entity)


        self.verticalLayout.addWidget(self.gb_ifc_entities)

        self.gb_description = QGroupBox(self.tab_basics)
        self.gb_description.setObjectName(u"gb_description")
        self.verticalLayout_8 = QVBoxLayout(self.gb_description)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(6, 6, 6, 6)
        self.te_definition = QTextEdit(self.gb_description)
        self.te_definition.setObjectName(u"te_definition")
        self.te_definition.setAutoFillBackground(True)
        self.te_definition.setStyleSheet(u"background-color:\n"
"                                                            rgba(0, 0, 0,10);")

        self.verticalLayout_8.addWidget(self.te_definition)

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


        self.verticalLayout_8.addLayout(self.hl_defintion)

        self.te_description = QTextEdit(self.gb_description)
        self.te_description.setObjectName(u"te_description")
        self.te_description.setStyleSheet(u"background-color:\n"
"                                                            rgba(0, 0, 0,10);")

        self.verticalLayout_8.addWidget(self.te_description)


        self.verticalLayout.addWidget(self.gb_description)

        self.tabWidget.addTab(self.tab_basics, "")
        self.tab_relations = QWidget()
        self.tab_relations.setObjectName(u"tab_relations")
        self.verticalLayout_2 = QVBoxLayout(self.tab_relations)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gb_relationship = QGroupBox(self.tab_relations)
        self.gb_relationship.setObjectName(u"gb_relationship")
        self.verticalLayout_3 = QVBoxLayout(self.gb_relationship)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.relationship_editor = RelationshipWidget(self.gb_relationship)
        self.relationship_editor.setObjectName(u"relationship_editor")

        self.verticalLayout_3.addWidget(self.relationship_editor)


        self.verticalLayout_2.addWidget(self.gb_relationship)

        self.gb_version_control = QGroupBox(self.tab_relations)
        self.gb_version_control.setObjectName(u"gb_version_control")
        self.formLayout = QFormLayout(self.gb_version_control)
        self.formLayout.setObjectName(u"formLayout")
        self.lb_activation_time = QLabel(self.gb_version_control)
        self.lb_activation_time.setObjectName(u"lb_activation_time")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_activation_time)

        self.de_activation_time = DateTimeWithNow(self.gb_version_control)
        self.de_activation_time.setObjectName(u"de_activation_time")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.de_activation_time)

        self.lb_revision_date = QLabel(self.gb_version_control)
        self.lb_revision_date.setObjectName(u"lb_revision_date")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_revision_date)

        self.de_revision_time = DateTimeWithNow(self.gb_version_control)
        self.de_revision_time.setObjectName(u"de_revision_time")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.de_revision_time)

        self.lb_revision_number = QLabel(self.gb_version_control)
        self.lb_revision_number.setObjectName(u"lb_revision_number")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lb_revision_number)

        self.sb_revision_number = QSpinBox(self.gb_version_control)
        self.sb_revision_number.setObjectName(u"sb_revision_number")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.sb_revision_number)

        self.lb_deactivation_time = QLabel(self.gb_version_control)
        self.lb_deactivation_time.setObjectName(u"lb_deactivation_time")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lb_deactivation_time)

        self.de_deactivation_time = DateTimeWithNow(self.gb_version_control)
        self.de_deactivation_time.setObjectName(u"de_deactivation_time")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.de_deactivation_time)

        self.lb_deprecation_explanation = QLabel(self.gb_version_control)
        self.lb_deprecation_explanation.setObjectName(u"lb_deprecation_explanation")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lb_deprecation_explanation)

        self.le_deprecation_explanation = QLineEdit(self.gb_version_control)
        self.le_deprecation_explanation.setObjectName(u"le_deprecation_explanation")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.le_deprecation_explanation)

        self.lb_version_date = QLabel(self.gb_version_control)
        self.lb_version_date.setObjectName(u"lb_version_date")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lb_version_date)

        self.de_version_date = DateTimeWithNow(self.gb_version_control)
        self.de_version_date.setObjectName(u"de_version_date")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.de_version_date)

        self.lb_version_number = QLabel(self.gb_version_control)
        self.lb_version_number.setObjectName(u"lb_version_number")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lb_version_number)

        self.sb_version_number = QSpinBox(self.gb_version_control)
        self.sb_version_number.setObjectName(u"sb_version_number")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.sb_version_number)

        self.lb_replaced_objects = QLabel(self.gb_version_control)
        self.lb_replaced_objects.setObjectName(u"lb_replaced_objects")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lb_replaced_objects)

        self.ti_replaced_objects = TagInput(self.gb_version_control)
        self.ti_replaced_objects.setObjectName(u"ti_replaced_objects")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.ti_replaced_objects)

        self.lb_replacing_objects = QLabel(self.gb_version_control)
        self.lb_replacing_objects.setObjectName(u"lb_replacing_objects")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lb_replacing_objects)

        self.ti_replacing_objects = TagInput(self.gb_version_control)
        self.ti_replacing_objects.setObjectName(u"ti_replacing_objects")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.ti_replacing_objects)


        self.verticalLayout_2.addWidget(self.gb_version_control)

        self.tabWidget.addTab(self.tab_relations, "")
        self.tab_advanced = QWidget()
        self.tab_advanced.setObjectName(u"tab_advanced")
        self.verticalLayout_7 = QVBoxLayout(self.tab_advanced)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.gb_identification = QGroupBox(self.tab_advanced)
        self.gb_identification.setObjectName(u"gb_identification")
        self.formLayout_3 = QFormLayout(self.gb_identification)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.lb_reference_code = QLabel(self.gb_identification)
        self.lb_reference_code.setObjectName(u"lb_reference_code")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_reference_code)

        self.le_reference_code = QLineEdit(self.gb_identification)
        self.le_reference_code.setObjectName(u"le_reference_code")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_reference_code)

        self.lb_owned_uri = QLabel(self.gb_identification)
        self.lb_owned_uri.setObjectName(u"lb_owned_uri")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_owned_uri)

        self.le_owned_uri = QLabel(self.gb_identification)
        self.le_owned_uri.setObjectName(u"le_owned_uri")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.le_owned_uri)

        self.lb_document_ref = QLabel(self.gb_identification)
        self.lb_document_ref.setObjectName(u"lb_document_ref")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lb_document_ref)

        self.cb_document_ref = ComboBoxWithToggleSwitch(self.gb_identification)
        self.cb_document_ref.setObjectName(u"cb_document_ref")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cb_document_ref)

        self.lb_subdivision = QLabel(self.gb_identification)
        self.lb_subdivision.setObjectName(u"lb_subdivision")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lb_subdivision)

        self.ti_subdivision = TagInput(self.gb_identification)
        self.ti_subdivision.setObjectName(u"ti_subdivision")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.ti_subdivision)

        self.lb_uid = QLabel(self.gb_identification)
        self.lb_uid.setObjectName(u"lb_uid")

        self.formLayout_3.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lb_uid)

        self.le_uid = QLineEdit(self.gb_identification)
        self.le_uid.setObjectName(u"le_uid")

        self.formLayout_3.setWidget(4, QFormLayout.ItemRole.FieldRole, self.le_uid)

        self.lb_visual_rep = QLabel(self.gb_identification)
        self.lb_visual_rep.setObjectName(u"lb_visual_rep")

        self.formLayout_3.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lb_visual_rep)

        self.le_visual_rep = QLineEdit(self.gb_identification)
        self.le_visual_rep.setObjectName(u"le_visual_rep")

        self.formLayout_3.setWidget(5, QFormLayout.ItemRole.FieldRole, self.le_visual_rep)


        self.verticalLayout_7.addWidget(self.gb_identification)

        self.gb_language = QGroupBox(self.tab_advanced)
        self.gb_language.setObjectName(u"gb_language")
        self.formLayout_2 = QFormLayout(self.gb_language)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.lb_country_use = QLabel(self.gb_language)
        self.lb_country_use.setObjectName(u"lb_country_use")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lb_country_use)

        self.ti_countries = TagInput(self.gb_language)
        self.ti_countries.setObjectName(u"ti_countries")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.ti_countries)

        self.lb_country_origin = QLabel(self.gb_language)
        self.lb_country_origin.setObjectName(u"lb_country_origin")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lb_country_origin)

        self.cb_country_origin = ComboBoxWithToggleSwitch(self.gb_language)
        self.cb_country_origin.setObjectName(u"cb_country_origin")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.cb_country_origin)

        self.lb_creator_iso = QLabel(self.gb_language)
        self.lb_creator_iso.setObjectName(u"lb_creator_iso")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lb_creator_iso)

        self.cb_creator_iso = ComboBoxWithToggleSwitch(self.gb_language)
        self.cb_creator_iso.setObjectName(u"cb_creator_iso")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cb_creator_iso)


        self.verticalLayout_7.addWidget(self.gb_language)

        self.tabWidget.addTab(self.tab_advanced, "")

        self.verticalLayout_5.addWidget(self.tabWidget)


        self.retranslateUi(ClassEditor)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ClassEditor)
    # setupUi

    def retranslateUi(self, ClassEditor):
        ClassEditor.setWindowTitle(QCoreApplication.translate("ClassEditor", u"Form", None))
        self.gb_required.setTitle(QCoreApplication.translate("ClassEditor", u"Required", None))
        self.lb_code.setText(QCoreApplication.translate("ClassEditor", u"Code", None))
        self.lb_name.setText(QCoreApplication.translate("ClassEditor", u"Name", None))
        self.lb_class_type.setText(QCoreApplication.translate("ClassEditor", u"Class Type", None))
        self.lb_status.setText(QCoreApplication.translate("ClassEditor", u"Status", None))
        self.gb_synonyms.setTitle(QCoreApplication.translate("ClassEditor", u"Synonyms", None))
        self.gb_ifc_entities.setTitle(QCoreApplication.translate("ClassEditor", u"Related IFC Entities", None))
        self.gb_description.setTitle(QCoreApplication.translate("ClassEditor", u"Definition", None))
        self.lb_description.setText(QCoreApplication.translate("ClassEditor", u"Description", None))
        self.cb_description.setText(QCoreApplication.translate("ClassEditor", u"Description:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_basics), QCoreApplication.translate("ClassEditor", u"Basics", None))
        self.gb_relationship.setTitle(QCoreApplication.translate("ClassEditor", u"ClassRelations", None))
        self.gb_version_control.setTitle(QCoreApplication.translate("ClassEditor", u"Version Control", None))
        self.lb_activation_time.setText(QCoreApplication.translate("ClassEditor", u"Activation Date:", None))
        self.lb_revision_date.setText(QCoreApplication.translate("ClassEditor", u"Revision Date:", None))
        self.lb_revision_number.setText(QCoreApplication.translate("ClassEditor", u"Revision Number:", None))
        self.lb_deactivation_time.setText(QCoreApplication.translate("ClassEditor", u"De Activation Date:", None))
        self.lb_deprecation_explanation.setText(QCoreApplication.translate("ClassEditor", u"DeprecationExplanation:", None))
        self.lb_version_date.setText(QCoreApplication.translate("ClassEditor", u"Version Date:", None))
        self.lb_version_number.setText(QCoreApplication.translate("ClassEditor", u"Version number:", None))
#if QT_CONFIG(tooltip)
        self.lb_replaced_objects.setToolTip(QCoreApplication.translate("ClassEditor", u"List of Property Codes this Property replaces", None))
#endif // QT_CONFIG(tooltip)
        self.lb_replaced_objects.setText(QCoreApplication.translate("ClassEditor", u"Replaced Object Codes:", None))
#if QT_CONFIG(tooltip)
        self.lb_replacing_objects.setToolTip(QCoreApplication.translate("ClassEditor", u"List of Property Codes this Property is replaced by", None))
#endif // QT_CONFIG(tooltip)
        self.lb_replacing_objects.setText(QCoreApplication.translate("ClassEditor", u"Replacing Object Codes:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_relations), QCoreApplication.translate("ClassEditor", u"Relations + Version", None))
        self.gb_identification.setTitle(QCoreApplication.translate("ClassEditor", u"Identification", None))
#if QT_CONFIG(tooltip)
        self.lb_reference_code.setToolTip(QCoreApplication.translate("ClassEditor", u"Example value of the Property", None))
#endif // QT_CONFIG(tooltip)
        self.lb_reference_code.setText(QCoreApplication.translate("ClassEditor", u"ReferenceCode:", None))
        self.lb_owned_uri.setText(QCoreApplication.translate("ClassEditor", u"OwnedUri:", None))
        self.le_owned_uri.setText("")
#if QT_CONFIG(tooltip)
        self.lb_document_ref.setToolTip(QCoreApplication.translate("ClassEditor", u"Reference to document with the full or official\n"
"                                            definition of the Property", None))
#endif // QT_CONFIG(tooltip)
        self.lb_document_ref.setText(QCoreApplication.translate("ClassEditor", u"Document Reference:", None))
#if QT_CONFIG(tooltip)
        self.lb_subdivision.setToolTip(QCoreApplication.translate("ClassEditor", u"List of geographical regions of use Example:\n"
"                                            \"US-MT\"", None))
#endif // QT_CONFIG(tooltip)
        self.lb_subdivision.setText(QCoreApplication.translate("ClassEditor", u"Subdivision of Use:", None))
#if QT_CONFIG(tooltip)
        self.lb_uid.setToolTip(QCoreApplication.translate("ClassEditor", u"Unique identification (ID), in case the URI is not\n"
"                                            enough.", None))
#endif // QT_CONFIG(tooltip)
        self.lb_uid.setText(QCoreApplication.translate("ClassEditor", u"Uid:", None))
        self.lb_visual_rep.setText(QCoreApplication.translate("ClassEditor", u"Visual Representation:", None))
        self.gb_language.setTitle(QCoreApplication.translate("ClassEditor", u"Language", None))
#if QT_CONFIG(tooltip)
        self.lb_country_use.setToolTip(QCoreApplication.translate("ClassEditor", u"List of country ISO codes this Property is being\n"
"                                            used.", None))
#endif // QT_CONFIG(tooltip)
        self.lb_country_use.setText(QCoreApplication.translate("ClassEditor", u"Countries of Use:", None))
#if QT_CONFIG(tooltip)
        self.lb_country_origin.setToolTip(QCoreApplication.translate("ClassEditor", u"ISO Country Code of the country of origin of this\n"
"                                            Property", None))
#endif // QT_CONFIG(tooltip)
        self.lb_country_origin.setText(QCoreApplication.translate("ClassEditor", u"Country of origin:", None))
#if QT_CONFIG(tooltip)
        self.lb_creator_iso.setToolTip(QCoreApplication.translate("ClassEditor", u"Language ISO code of the creator. ", None))
#endif // QT_CONFIG(tooltip)
        self.lb_creator_iso.setText(QCoreApplication.translate("ClassEditor", u"Creator Language IsoCode:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_advanced), QCoreApplication.translate("ClassEditor", u"Advanced", None))
    # retranslateUi

