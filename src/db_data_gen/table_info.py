"""Contains enum of supported column types and classes to describe columns and tables"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ColumnType(Enum):
    """Supported column types for generation"""

    BOOL = 'bool'
    TIMESTAMPZ = 'timestamptz'
    INT2 = 'int2'
    INT4 = 'int4'
    INT8 = 'int8'
    UUID = 'uuid'
    VARCHAR = 'varchar'
    TEXT = 'text'
    BYTEA = 'bytea'


class ColumnInfo:
    """Information about column is obtained from table "information_schema.columns".

    You can modify 'ADDITIONAL_FIELDS' dict in format {"attribute name": "field name in SQL table"}
    to get more data from this table. You can create properties similar to "max_length" for convenient
    work with the received fields"""

    ADDITIONAL_FIELDS = {'max_length': 'character_maximum_length'}

    def __init__(self, column_type: ColumnType, can_be_null: bool, additional_info: List[str]):
        self.column_type = column_type
        self.can_be_null = can_be_null
        for attribute, value in zip(ColumnInfo.ADDITIONAL_FIELDS.items(), additional_info):
            setattr(self, f'_{attribute[0]}', value)

    @staticmethod
    def get_sql_columns_names() -> str:
        """Return columns names of additional fields for SQL request"""
        if len(ColumnInfo.ADDITIONAL_FIELDS):
            return ', ' + ', '.join(ColumnInfo.ADDITIONAL_FIELDS.values())
        return ''

    @property
    def max_length(self) -> Optional[int]:
        """Get field max length for string type"""
        return None if self._max_length is None else int(self._max_length)  # pylint: disable=no-member

    def __repr__(self) -> str:
        return f'ColumnInfo({self.__dict__})'


@dataclass
class ForeignKey:
    """Information about foreign table and column"""

    table: str
    column: str


@dataclass
class TableInfo:
    """Information about table schema, unique groups (contains primary and unique keys) and foreign keys"""

    schema: Dict[str, ColumnInfo]
    unique_groups: List[List[str]]
    foreign_keys: Dict[str, ForeignKey]
