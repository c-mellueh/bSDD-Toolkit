from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .prop_presets import ColumnHandlerProperties


class ColumnHandler(ABC):
    @classmethod
    @abstractmethod
    def get_properties(cls) -> ColumnHandlerProperties:
        return None

    @classmethod
    def add_column_to_table(cls, name: str, get_function: Callable) -> None:
        """
        Define Column which should be shown in Table
        :param name: Name of Column
        :param get_function: getter function for cell value. SOMcreator.SOMProperty will be passed as argument
        :return:
        """
        cls.get_properties().columns.append((name, get_function))

    @classmethod
    def get_column_count(cls):
        return len(cls.get_properties().columns)
    
    @classmethod
    def get_column_names(cls):
        return [x[0] for x in cls.get_properties().columns]
    
    @classmethod
    def get_value_functions(cls):
        return [x[1] for x in cls.get_properties().columns]