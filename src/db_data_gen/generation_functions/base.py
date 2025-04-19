"""Contains base classes of generator"""

import random
from abc import ABC, abstractmethod
from typing import Optional

from ..table_info import ColumnInfo


class GenFunction(ABC):
    """Abstract class to implement generator logic"""

    def __init__(
        self,
        column_info: ColumnInfo,
        acceptable_count_of_null: int = 100,
        null_probability: float = 0.5,
        special_values: Optional[list] = None,
    ):
        """
        :param column_info: info about column
        :param acceptable_count_of_null: number of records that can be NULL
        :param null_probability: probability of NULL generation
        :param special_values: special values that generator outputs first
        """
        self.column_info = column_info
        self.__acceptable_count_of_null = acceptable_count_of_null
        self.__null_probability = null_probability
        if not isinstance(special_values, list):
            special_values = self.get_special_values()
        self.__special = len(special_values)
        if self.__special:
            self.__special_generator = (item for item in special_values)

    def get_special_values(self) -> list:
        """Get list of special values. Can be overridden"""
        return []

    @abstractmethod
    def get_common_value(self):
        """Get common value"""

    def get_value(self):
        """Get generated value"""
        if self.__special:
            try:
                return next(self.__special_generator)
            except StopIteration:
                self.__special = False
        if (
            self.column_info.can_be_null
            and self.__acceptable_count_of_null
            and random.random() < self.__null_probability
        ):
            self.__acceptable_count_of_null -= 1
            return None
        return self.get_common_value()
