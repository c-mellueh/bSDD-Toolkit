from __future__ import annotations

import logging
import os
from configparser import ConfigParser

import appdirs

import bsdd_gui
from bsdd_gui import tool

OPTION_SEPERATOR = ";"
PATHS_SECTION = "paths"


class CustomConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getlist(self, section, option):
        value = self.get(section, option)
        return value.split(OPTION_SEPERATOR)

    def setstring(self, section, option, value):
        self.set(section, option)

    def get(self, section, option, *args, **kargs):
        if not self.has_section(section):
            return None
        if not self.has_option(section, option):
            return None
        res = super().get(section, option, *args, **kargs)
        if not isinstance(res, str):
            return res
        if res.startswith("'") and res.endswith("'"):
            res = res.strip("'")
        return res

    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)
        if type(value) in (list, set, tuple):
            value = OPTION_SEPERATOR.join([str(v) for v in value])
        if isinstance(value, str):
            value = f"'{value}'"
        super().set(section, option, str(value))


class Appdata:
    @classmethod
    def _write_config(cls, config_parser) -> None:
        with open(cls.get_ini_path(), "w") as f:
            config_parser.write(f)

    @classmethod
    def _get_config(
        cls,
    ) -> CustomConfigParser:
        ConfigParser()
        config = CustomConfigParser()
        config_path = cls.get_ini_path()
        parent_folder = os.path.dirname(config_path)
        if not os.path.exists(parent_folder):
            tool.Util.create_directory(parent_folder)
            return config
        if not os.path.exists(config_path):
            return config
        config.read(config_path)
        return config

    @classmethod
    def get_appdata_folder(cls):
        return appdirs.user_config_dir(bsdd_gui.__name__)

    @classmethod
    def get_ini_path(cls):
        return os.path.join(cls.get_appdata_folder(), "config.ini")

    @classmethod
    def get_path(cls, value: str) -> str | list | set:
        logging.info(f"Appdata Path '{value}' requested")
        config = cls._get_config()
        path = config.get(PATHS_SECTION, value)
        if not path:
            return ""
        if OPTION_SEPERATOR in path:
            return path.split(OPTION_SEPERATOR)
        return path

    @classmethod
    def set_path(cls, path, value: str | list | set) -> None:
        if isinstance(value, (list, set)):
            value = OPTION_SEPERATOR.join(value)
        cls.set_setting(PATHS_SECTION, path, value)

    @classmethod
    def set_setting(cls, section: str, option: str, value):
        config_parser = cls._get_config()
        config_parser.set(section, option, value)
        cls._write_config(config_parser)

    @classmethod
    def get_bool_setting(cls, section: str, option: str, default=False) -> bool:
        config_parser = cls._get_config()
        if config_parser.has_option(section, option):
            return config_parser.getboolean(section, option)
        cls.set_setting(section, option, default)
        return default

    @classmethod
    def get_string_setting(cls, section: str, option: str, default="") -> str:
        config_parser = cls._get_config()
        if config_parser.has_option(section, option):
            value = config_parser.get(section, option)
            if value is not None:
                return value
        cls.set_setting(section, option, default)
        return default

    @classmethod
    def get_int_setting(cls, section: str, option: str, default=0) -> int:
        config_parser = cls._get_config()
        if config_parser.has_option(section, option):
            return config_parser.getint(section, option)
        cls.set_setting(section, option, default)
        return default

    @classmethod
    def get_float_setting(cls, section: str, option: str, default=0) -> float:
        config_parser = cls._get_config()
        if config_parser.has_option(section, option):
            return config_parser.getfloat(section, option)
        cls.set_setting(section, option, default)
        return default

    @classmethod
    def get_list_setting(cls, section: str, option: str, default=[]) -> list[str]:
        config_parser = cls._get_config()
        if config_parser.has_option(section, option):
            value = config_parser.getlist(section, option)
            value = None if value == "None" else value
            if value is not None:
                return value
        cls.set_setting(section, option, default)
        return default
