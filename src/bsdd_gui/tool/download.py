from __future__ import annotations
from typing import TYPE_CHECKING, Type
from types import ModuleType
from bsdd import Client
from bsdd_json import BsddDictionary, BsddClass, BsddProperty
import logging
from bsdd_gui.presets.tool_presets import FieldTool, ActionTool
from bsdd_gui.presets.tool_presets import FieldSignals
from PySide6.QtCore import Signal, QObject, Slot, QThread
from PySide6.QtWidgets import QProgressBar, QLabel
import bsdd_gui
from bsdd_json.utils import class_utils
from bsdd_json.utils import property_utils as prop_utils
import time
from bsdd_gui.module.download import ui, trigger

if TYPE_CHECKING:
    from bsdd_gui.module.download.prop import DownloadProperties


class Signals(FieldSignals):
    progress_changed = Signal(int, object)  # value,progressbar
    bsdd_import_finished = Signal(object)
    import_finished = Signal(object)


class Download(FieldTool, ActionTool):
    signals = Signals()

    @classmethod
    def connect_internal_signals(cls):
        return super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.DownloadWidget):
        super().connect_widget_signals(widget)
        widget.btn_start.clicked.connect(lambda _, w=widget: trigger.start_download(w))
        widget.btn_cancel.clicked.connect(lambda w=widget: cls.cancel(w))
        widget.cb_save.toggled.connect(lambda v: widget.fs_save_path.setVisible(v))

    @classmethod
    def get_properties(cls) -> DownloadProperties:
        return bsdd_gui.DownloadProperties

    @classmethod
    def _get_trigger(cls) -> ModuleType:
        return trigger

    @classmethod
    def _get_widget_class(cls) -> Type[ui.DownloadWidget]:
        return ui.DownloadWidget

    @classmethod
    def get_client(cls) -> Client:
        client = cls.get_properties().client
        if not client:
            cls.get_properties().client = Client()
        return cls.get_properties().client

    @classmethod
    def swap_codes(cls, data_dict: dict, old: str, new: str):
        if old not in data_dict:
            return
        data_dict[new] = data_dict[old]
        data_dict.pop(old)

    @classmethod
    def import_dictionary(cls, dictionary_uri):
        def read_lang_code():
            if "availableLanguages" not in dictionary_data:
                return
            dictionary_data.pop("availableLanguages")

        dictionary_data = cls.get_client().get_dictionary(dictionary_uri)["dictionaries"][0]
        read_lang_code()
        cls.swap_codes(dictionary_data, "organizationCodeOwner", "OrganizationCode")
        cls.swap_codes(dictionary_data, "code", "DictionaryCode")
        cls.swap_codes(dictionary_data, "version", "DictionaryVersion")
        cls.swap_codes(dictionary_data, "defaultLanguageCode", "LanguageIsoCode")
        cls.swap_codes(dictionary_data, "name", "DictionaryName")
        cls.swap_codes(dictionary_data, "changeRequestEmail", "ChangeRequestEmailAddress")
        dictionary_data["LanguageOnly"] = False
        dictionary_data["UseOwnUri"] = False
        return BsddDictionary.model_validate(dictionary_data)

    @classmethod
    def set_buttons_enabled(cls, widget: ui.DownloadWidget, state: bool):
        # TODO
        return

    @classmethod
    def create_worker(
        cls,
        bar: QProgressBar,
        label: QLabel,
        widget: ui.DownloadWidget,
        worker_class: Type[ClassWorker] | Type[PropertyWorker],
        result_save_place,
        *args,
        **kwargs,
    ):

        def _handle_finish():
            logging.info("Import Done!")
            cls.set_buttons_enabled(widget, True)
            bsdd_dictionary = cls.get_properties().bsdd_dictionary
            bsdd_dictionary.Classes = cls.get_properties().bsdd_classes
            for bsdd_class in bsdd_dictionary.Classes:
                bsdd_class._set_parent(bsdd_dictionary)
            bsdd_dictionary.Properties = cls.get_properties().bsdd_properies
            for bsdd_property in bsdd_dictionary.Properties:
                bsdd_property._set_parent(bsdd_dictionary)
            
            if widget.cb_save.isChecked():
                bsdd_dictionary.save(cls.get_properties().save_path)
            cls.reset(widget)
            time.sleep(0.1)
            cls.signals.import_finished.emit(bsdd_dictionary)

        def _on_worker_finished():
            prop = cls.get_properties()
            setattr(prop, result_save_place, worker.result)
            label.setText(f"Import done!")
            cls.get_properties().done_count += 1
            if cls.get_properties().done_count == 2:
                _handle_finish()

        bar.setValue(0)
        label.setText("Started")
        thread = QThread(widget)
        worker = worker_class(*args, **kwargs)
        worker.moveToThread(thread)
        cls.get_properties().workers.append(worker)
        cls.get_properties().threads.append(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(bar.setValue)
        worker.status.connect(label.setText)
        worker.error.connect(logging.error)

        worker.finished.connect(thread.quit)
        worker.finished.connect(_on_worker_finished)

        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(thread.deleteLater)
        thread.start()

    @classmethod
    def get_all_classes(
        cls, widget: ui.DownloadWidget, dictionary_uri: str, bsdd_dictionary: BsddDictionary
    ):
        bar = widget.pb_classes
        label = widget.lb_classes

        cls.create_worker(
            bar,
            label,
            widget,
            ClassWorker,
            "bsdd_classes",
            bsdd_dictionary,
            dictionary_uri,
            cls.get_client(),
        )

    @classmethod
    def get_all_properties(cls, widget: ui.DownloadWidget, dictionary_uri: str):
        bar = widget.pb_properties
        label = widget.lb_properties
        cls.create_worker(
            bar,
            label,
            widget,
            PropertyWorker,
            "bsdd_properies",
            dictionary_uri,
            cls.get_client(),
        )

    @classmethod
    def set_save_path(cls, value: str):
        cls.get_properties().save_path = value

    @classmethod
    def set_bsdd_dictionary(cls, value: BsddDictionary):
        cls.get_properties().bsdd_dictionary = value

    @classmethod
    def cancel(cls, widget: ui.DownloadWidget):
        for w in cls.get_properties().workers:
            w: Worker
            w.cancel()
        cls.reset(widget)

    @classmethod
    def reset(cls, widget: ui.DownloadWidget):
        cls.set_widget_run_mode(widget, False)
        cls.get_properties().workers = list()
        cls.get_properties().threads = list()
        cls.get_properties().done_count = 0

    @classmethod
    def set_widget_run_mode(cls, widget: ui.DownloadWidget, state: bool):
        """
        if state = true DOwnload is Running
        if state = False Waiting for input
        """
        widget.btn_cancel.setVisible(state)
        widget.btn_start.setVisible(not state)
        widget.wd_progressbars.setVisible(state)
        widget.le_uri.setEnabled(not state)
        widget.fs_save_path.setEnabled(not state)
        widget.cb_save.setEnabled(not state)

        w = widget.width()
        layout = widget.layout()
        layout.invalidate()
        layout.activate()
        widget.adjustSize()
        geometry = widget.geometry()
        geometry.setWidth(w)
        widget.setGeometry(geometry)


class Worker(QObject):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, client):
        super().__init__()
        self._cancel = False
        self.result = list()
        self.client = client

    @Slot()
    def cancel(self):
        self._cancel = True


class ClassWorker(Worker):

    def __init__(
        self,
        bsdd_dictionary: BsddDictionary,
        dictionary_uri: str,
        client: Client,
    ):
        super().__init__(client)
        self.dictionary_uri = dictionary_uri
        self.bsdd_dictionary = bsdd_dictionary

    @Slot()
    def run(self):
        try:
            self._cancel = False
            classes_info = list()
            class_count = 0
            total_count = None
            while total_count is None or class_count < total_count:
                if self._cancel:
                    self.status.emit("Cancelled")
                    break

                cd = self.client.get_classes(
                    self.dictionary_uri, use_nested_classes=False, limit=1_000, offset=class_count
                )
                classes_info += cd["classes"]
                class_count += cd["classesCount"]
                total_count = cd["classesTotalCount"]

            total = len(classes_info)

            self.status.emit(f"Processed Classes: {0}/{total}")
            for index, class_definition in enumerate(classes_info):
                if self._cancel:
                    self.status.emit("Cancelled")
                    break
                bsdd_class = class_utils.load_class(
                    class_definition["uri"], self.bsdd_dictionary, True, True, self.client
                )
                self.result.append(bsdd_class)
                pct = int((index + 1) / total * 100)
                self.progress.emit(pct)
                self.status.emit(f"Processed Classes: {index+1}/{total}")
            time.sleep(0.1)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class PropertyWorker(Worker):

    def __init__(self, dictionary_uri: str, client: Client):
        super().__init__(client)
        self.client = client
        self.dictionary_uri = dictionary_uri

    @Slot()
    def run(self):
        try:
            self._cancel = False
            property_info = list()
            property_count = 0
            total_count = None
            while total_count is None or property_count < total_count:
                if self._cancel:
                    self.status.emit("Cancelled")
                    break

                pd = self.client.get_properties(
                    self.dictionary_uri, limit=1000, offset=property_count
                )

                property_info += pd["properties"]
                property_count += pd["propertiesCount"]
                total_count = pd["propertiesTotalCount"]

            total = len(property_info)
            self.status.emit(f"Processed Properties: {0}/{total}")
            for index, property_definition in enumerate(property_info):
                if self._cancel:
                    self.status.emit("Cancelled")
                    break
                bsdd_property = prop_utils.load_property(
                    property_definition["uri"], client=self.client
                )
                self.result.append(bsdd_property)
                pct = int((index + 1) / total * 100)
                self.progress.emit(pct)
                self.status.emit(f"Processed Properties: {index+1}/{total}")
            time.sleep(0.1)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
