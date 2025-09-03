# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DictionaryEditor.ui'
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
    QFormLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QWidget,
)

from bsdd_gui.presets.ui_presets.datetime_now import DateTimeWithNow
from bsdd_gui.presets.ui_presets.toggle_switch import ToggleSwitch


class Ui_DictionaryForm(object):
    def setupUi(self, DictionaryForm):
        if not DictionaryForm.objectName():
            DictionaryForm.setObjectName("DictionaryForm")
        DictionaryForm.resize(504, 533)
        self.formLayout = QFormLayout(DictionaryForm)
        self.formLayout.setObjectName("formLayout")
        self.lbOrganizationCode = QLabel(DictionaryForm)
        self.lbOrganizationCode.setObjectName("lbOrganizationCode")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbOrganizationCode)

        self.le_org_code = QLineEdit(DictionaryForm)
        self.le_org_code.setObjectName("le_org_code")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.le_org_code)

        self.lbDictionaryCode = QLabel(DictionaryForm)
        self.lbDictionaryCode.setObjectName("lbDictionaryCode")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbDictionaryCode)

        self.le_dictionary_code = QLineEdit(DictionaryForm)
        self.le_dictionary_code.setObjectName("le_dictionary_code")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.le_dictionary_code)

        self.lbDictionaryName = QLabel(DictionaryForm)
        self.lbDictionaryName.setObjectName("lbDictionaryName")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbDictionaryName)

        self.le_dictionary_name = QLineEdit(DictionaryForm)
        self.le_dictionary_name.setObjectName("le_dictionary_name")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.le_dictionary_name)

        self.lbDictionaryVersion = QLabel(DictionaryForm)
        self.lbDictionaryVersion.setObjectName("lbDictionaryVersion")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbDictionaryVersion)

        self.le_dictionary_version = QLineEdit(DictionaryForm)
        self.le_dictionary_version.setObjectName("le_dictionary_version")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.le_dictionary_version)

        self.lbLanguageIsoCode = QLabel(DictionaryForm)
        self.lbLanguageIsoCode.setObjectName("lbLanguageIsoCode")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lbLanguageIsoCode)

        self.lbLanguageOnly = QLabel(DictionaryForm)
        self.lbLanguageOnly.setObjectName("lbLanguageOnly")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lbLanguageOnly)

        self.cb_language_only = ToggleSwitch(DictionaryForm)
        self.cb_language_only.setObjectName("cb_language_only")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.cb_language_only)

        self.lbUseOwnUri = QLabel(DictionaryForm)
        self.lbUseOwnUri.setObjectName("lbUseOwnUri")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lbUseOwnUri)

        self.cb_use_own_uri = ToggleSwitch(DictionaryForm)
        self.cb_use_own_uri.setObjectName("cb_use_own_uri")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.cb_use_own_uri)

        self.lbDictionaryUri = QLabel(DictionaryForm)
        self.lbDictionaryUri.setObjectName("lbDictionaryUri")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lbDictionaryUri)

        self.le_dictionary_uri = QLineEdit(DictionaryForm)
        self.le_dictionary_uri.setObjectName("le_dictionary_uri")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.le_dictionary_uri)

        self.lbLicense = QLabel(DictionaryForm)
        self.lbLicense.setObjectName("lbLicense")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lbLicense)

        self.le_license = QLineEdit(DictionaryForm)
        self.le_license.setObjectName("le_license")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.le_license)

        self.lbLicenseUrl = QLabel(DictionaryForm)
        self.lbLicenseUrl.setObjectName("lbLicenseUrl")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lbLicenseUrl)

        self.le_license_url = QLineEdit(DictionaryForm)
        self.le_license_url.setObjectName("le_license_url")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.le_license_url)

        self.lbChangeRequestEmailAddress = QLabel(DictionaryForm)
        self.lbChangeRequestEmailAddress.setObjectName("lbChangeRequestEmailAddress")

        self.formLayout.setWidget(
            10, QFormLayout.ItemRole.LabelRole, self.lbChangeRequestEmailAddress
        )

        self.le_change_request_mail = QLineEdit(DictionaryForm)
        self.le_change_request_mail.setObjectName("le_change_request_mail")

        self.formLayout.setWidget(10, QFormLayout.ItemRole.FieldRole, self.le_change_request_mail)

        self.lbModelVersion = QLabel(DictionaryForm)
        self.lbModelVersion.setObjectName("lbModelVersion")

        self.formLayout.setWidget(11, QFormLayout.ItemRole.LabelRole, self.lbModelVersion)

        self.lbMoreInfoUrl = QLabel(DictionaryForm)
        self.lbMoreInfoUrl.setObjectName("lbMoreInfoUrl")

        self.formLayout.setWidget(12, QFormLayout.ItemRole.LabelRole, self.lbMoreInfoUrl)

        self.le_more_info = QLineEdit(DictionaryForm)
        self.le_more_info.setObjectName("le_more_info")

        self.formLayout.setWidget(12, QFormLayout.ItemRole.FieldRole, self.le_more_info)

        self.lbQualityAssuranceProcedure = QLabel(DictionaryForm)
        self.lbQualityAssuranceProcedure.setObjectName("lbQualityAssuranceProcedure")

        self.formLayout.setWidget(
            13, QFormLayout.ItemRole.LabelRole, self.lbQualityAssuranceProcedure
        )

        self.le_qa_procedure = QLineEdit(DictionaryForm)
        self.le_qa_procedure.setObjectName("le_qa_procedure")

        self.formLayout.setWidget(13, QFormLayout.ItemRole.FieldRole, self.le_qa_procedure)

        self.lbQualityAssuranceProcedureUrl = QLabel(DictionaryForm)
        self.lbQualityAssuranceProcedureUrl.setObjectName("lbQualityAssuranceProcedureUrl")

        self.formLayout.setWidget(
            14, QFormLayout.ItemRole.LabelRole, self.lbQualityAssuranceProcedureUrl
        )

        self.le_qa_procedure_url = QLineEdit(DictionaryForm)
        self.le_qa_procedure_url.setObjectName("le_qa_procedure_url")

        self.formLayout.setWidget(14, QFormLayout.ItemRole.FieldRole, self.le_qa_procedure_url)

        self.lbReleaseDate = QLabel(DictionaryForm)
        self.lbReleaseDate.setObjectName("lbReleaseDate")

        self.formLayout.setWidget(15, QFormLayout.ItemRole.LabelRole, self.lbReleaseDate)

        self.lbStatus = QLabel(DictionaryForm)
        self.lbStatus.setObjectName("lbStatus")

        self.formLayout.setWidget(16, QFormLayout.ItemRole.LabelRole, self.lbStatus)

        self.de_release_date = DateTimeWithNow(DictionaryForm)
        self.de_release_date.setObjectName("de_release_date")

        self.formLayout.setWidget(15, QFormLayout.ItemRole.FieldRole, self.de_release_date)

        self.cb_language_iso = QComboBox(DictionaryForm)
        self.cb_language_iso.setObjectName("cb_language_iso")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.cb_language_iso)

        self.cb_model_version = QComboBox(DictionaryForm)
        self.cb_model_version.addItem("")
        self.cb_model_version.addItem("")
        self.cb_model_version.setObjectName("cb_model_version")

        self.formLayout.setWidget(11, QFormLayout.ItemRole.FieldRole, self.cb_model_version)

        self.cb_status = QComboBox(DictionaryForm)
        self.cb_status.addItem("")
        self.cb_status.addItem("")
        self.cb_status.addItem("")
        self.cb_status.setObjectName("cb_status")

        self.formLayout.setWidget(16, QFormLayout.ItemRole.FieldRole, self.cb_status)

        self.retranslateUi(DictionaryForm)

        QMetaObject.connectSlotsByName(DictionaryForm)

    # setupUi

    def retranslateUi(self, DictionaryForm):
        DictionaryForm.setWindowTitle(
            QCoreApplication.translate("DictionaryForm", "Dictionary Form", None)
        )
        self.lbOrganizationCode.setText(
            QCoreApplication.translate("DictionaryForm", "OrganizationCode *", None)
        )
        # if QT_CONFIG(tooltip)
        self.le_org_code.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm",
                "The organisation's code received when registering in bSDD. Preferably short; cannot start with a digit.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.le_org_code.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "e.g. ifc", None)
        )
        self.lbDictionaryCode.setText(
            QCoreApplication.translate("DictionaryForm", "DictionaryCode *", None)
        )
        # if QT_CONFIG(tooltip)
        self.le_dictionary_code.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm", "Code of the dictionary, preferably short.", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.le_dictionary_code.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "e.g. ifc", None)
        )
        self.lbDictionaryName.setText(
            QCoreApplication.translate("DictionaryForm", "DictionaryName *", None)
        )
        # if QT_CONFIG(tooltip)
        self.le_dictionary_name.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm",
                "Name of the dictionary. If the dictionary exists, supplying this name is not necessary.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lbDictionaryVersion.setText(
            QCoreApplication.translate("DictionaryForm", "DictionaryVersion *", None)
        )
        # if QT_CONFIG(tooltip)
        self.le_dictionary_version.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm",
                "Version format: up to three dot-separated numbers. Examples: 12, 10.1, 1.2.3.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.le_dictionary_version.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "e.g. 1.0.1", None)
        )
        self.lbLanguageIsoCode.setText(
            QCoreApplication.translate("DictionaryForm", "LanguageIsoCode *", None)
        )
        self.lbLanguageOnly.setText(
            QCoreApplication.translate("DictionaryForm", "LanguageOnly *", None)
        )
        # if QT_CONFIG(tooltip)
        self.cb_language_only.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm", "True if JSON contains only language-specific info.", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lbUseOwnUri.setText(QCoreApplication.translate("DictionaryForm", "UseOwnUri *", None))
        # if QT_CONFIG(tooltip)
        self.cb_use_own_uri.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm",
                "Use your own URIs for globally unique identification. Default: false.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lbDictionaryUri.setText(
            QCoreApplication.translate("DictionaryForm", "DictionaryUri *", None)
        )
        # if QT_CONFIG(tooltip)
        self.le_dictionary_uri.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm",
                "Required if UseOwnUri = true. First part of all Class/Property URIs.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.le_dictionary_uri.setPlaceholderText(
            QCoreApplication.translate(
                "DictionaryForm",
                "urn:mycompany:mydictionary or https://mycompany.com/mydictionary",
                None,
            )
        )
        self.lbLicense.setText(QCoreApplication.translate("DictionaryForm", "License", None))
        # if QT_CONFIG(tooltip)
        self.le_license.setToolTip(
            QCoreApplication.translate(
                "DictionaryForm", "SPDX or well-known license identifier.", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.le_license.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "e.g. MIT, CC-BY-4.0", None)
        )
        self.lbLicenseUrl.setText(QCoreApplication.translate("DictionaryForm", "LicenseUrl", None))
        self.le_license_url.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "https://...", None)
        )
        self.lbChangeRequestEmailAddress.setText(
            QCoreApplication.translate("DictionaryForm", "ChangeRequestEmailAddress", None)
        )
        self.le_change_request_mail.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "name@example.com", None)
        )
        self.lbModelVersion.setText(
            QCoreApplication.translate("DictionaryForm", "ModelVersion", None)
        )
        self.lbMoreInfoUrl.setText(
            QCoreApplication.translate("DictionaryForm", "MoreInfoUrl", None)
        )
        self.le_more_info.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "https://...", None)
        )
        self.lbQualityAssuranceProcedure.setText(
            QCoreApplication.translate("DictionaryForm", "QualityAssuranceProcedure", None)
        )
        self.le_qa_procedure.setPlaceholderText(
            QCoreApplication.translate(
                "DictionaryForm", "e.g. bSI process, ETIM international", None
            )
        )
        self.lbQualityAssuranceProcedureUrl.setText(
            QCoreApplication.translate("DictionaryForm", "QualityAssuranceProcedureUrl", None)
        )
        self.le_qa_procedure_url.setPlaceholderText(
            QCoreApplication.translate("DictionaryForm", "https://...", None)
        )
        self.lbReleaseDate.setText(
            QCoreApplication.translate("DictionaryForm", "ReleaseDate", None)
        )
        self.lbStatus.setText(QCoreApplication.translate("DictionaryForm", "Status", None))
        self.cb_model_version.setItemText(
            0, QCoreApplication.translate("DictionaryForm", "1.0", None)
        )
        self.cb_model_version.setItemText(
            1, QCoreApplication.translate("DictionaryForm", "2.0", None)
        )

        self.cb_status.setItemText(0, QCoreApplication.translate("DictionaryForm", "Preview", None))
        self.cb_status.setItemText(1, QCoreApplication.translate("DictionaryForm", "Active", None))
        self.cb_status.setItemText(
            2, QCoreApplication.translate("DictionaryForm", "Inactive", None)
        )

    # retranslateUi
