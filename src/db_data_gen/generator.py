# pylint: disable=too-many-instance-attributes
"""Module kernel to generate data in DB by schema"""

import logging
from typing import Dict, Optional, Set, Type

from psycopg2 import errors

from .database_provider import DB
from .generation_functions import (
    BoolGenFunction,
    ByteaGenFunction,
    GenFunction,
    Int2GenFunction,
    Int4GenFunction,
    Int8GenFunction,
    TextGenFunction,
    TimestampzGenFunction,
    UUIDGenFunction,
    VarcharGenFunction,
)
from .row_generator import RowGenerator
from .table_info import ColumnInfo, ColumnType, ForeignKey, TableInfo

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(r'%(asctime)s [%(levelname)s] %(message)s', r'%Y-%m-%d %H:%M:%S'))
LOGGER.addHandler(handler)

STANDART_GENERATION_FUNCTIONS = {
    ColumnType.BOOL: BoolGenFunction,
    ColumnType.TIMESTAMPZ: TimestampzGenFunction,
    ColumnType.INT2: Int2GenFunction,
    ColumnType.INT4: Int4GenFunction,
    ColumnType.INT8: Int8GenFunction,
    ColumnType.UUID: UUIDGenFunction,
    ColumnType.VARCHAR: VarcharGenFunction,
    ColumnType.TEXT: TextGenFunction,
    ColumnType.BYTEA: ByteaGenFunction,
}


class DBDataGenerator:
    """Class to generate data in DB by schema"""

    def __init__(
        self,
        config: dict,
        generation_functions: Optional[Dict[ColumnType, Type[GenFunction]]] = None,
        null_records_percentage: float = 0.2,
        skip_mode_for_uniqueness: bool = False,
    ):
        """
        :param config: dict setting for psycopg2 DB connection
        :param generation_functions: generator classes to create data based on column type
        :param null_records_percentage: percentage of data that can be NULL; accepts value from 0 to 1
        :param skip_mode_for_uniqueness: skip value if the row isn`t unique
        """
        self.config = config
        self.records_count = 0
        self.generation_functions = (
            STANDART_GENERATION_FUNCTIONS if generation_functions is None else generation_functions
        )
        self.null_records_percentage = null_records_percentage
        self.skip_mode_for_uniqueness = skip_mode_for_uniqueness

        self._tables_info: Dict[str, TableInfo] = {}
        self._records_count_for_table: Dict[str, int] = {}
        self._special_generators: Dict[str, Dict[str, GenFunction]] = {}
        self._generated_tables = set()

    def _extract_schemas(self, skip_tables: Set[str]):
        """Extract schemas from DB"""
        self._tables_info.clear()
        with DB(self.config) as cur:
            cur.execute(
                "select table_name from information_schema.tables where table_schema = 'public' order by table_name;"
            )
            tables = cur.fetchall()

            for table in tables:
                table_name = table[0]
                if table_name in skip_tables:
                    continue

                cur.execute(
                    f'select column_name, udt_name, is_nullable {ColumnInfo.get_sql_columns_names()} '
                    'from information_schema.columns where table_name = %s order by ordinal_position',
                    (table_name,),
                )
                columns = cur.fetchall()
                schema = {
                    item[0]: ColumnInfo(
                        column_type=ColumnType(item[1]),
                        can_be_null=item[2] == 'YES',
                        additional_info=item[3:],
                    )
                    for item in columns
                }
                cur.execute(
                    'select array_agg(a.attname order by x.ordinality) from pg_class t join pg_index ix on t.oid = '
                    'ix.indrelid join pg_class i on i.oid = ix.indexrelid join unnest(ix.indkey) with ordinality as '
                    'x(attnum, ordinality) on true join pg_attribute a on a.attrelid = t.oid AND a.attnum = x.attnum '
                    'where t.relname = %s and ix.indisunique group by i.relname, ix.indisunique, ix.indisprimary',
                    (table_name,),
                )
                unique_groups = list(map(lambda item: item[0], cur.fetchall()))
                cur.execute(
                    'select kcu.column_name, ccu.table_name, ccu.column_name from '
                    'information_schema.table_constraints tc join information_schema.key_column_usage kcu on '
                    'tc.constraint_name = kcu.constraint_name join information_schema.constraint_column_usage ccu '
                    'on ccu.constraint_name = tc.constraint_name where tc.table_name = %s and '
                    "tc.constraint_type = 'FOREIGN KEY'",
                    (table_name,),
                )
                foreign_keys = {
                    column: ForeignKey(foreign_table, foreign_column)
                    for column, foreign_table, foreign_column in cur.fetchall()
                }
                self._tables_info[table_name] = TableInfo(schema, unique_groups, foreign_keys)

    def _get_foreign_column_value(self, foreign_key: ForeignKey):
        """Get available values for foreign key"""
        with DB(self.config) as cur:
            cur.execute(f'select {foreign_key.column} from {foreign_key.table}')
            return (value[0] for value in cur.fetchall())

    def _generate_data_for_table(self, table_name: str):
        """Generate data for one DB table"""
        table_info = self._tables_info[table_name]
        for key_info in table_info.foreign_keys.values():
            if key_info.table not in self._generated_tables:
                self._generate_data_for_table(key_info.table)
        records_count = self._records_count_for_table.get(table_name, self.records_count)
        generators = [
            self._get_foreign_column_value(table_info.foreign_keys[column])
            if column in table_info.foreign_keys
            else self._special_generators.get(table_name, {}).get(
                column,
                self.generation_functions[info.column_type](
                    column_info=info,
                    acceptable_count_of_null=int(self.null_records_percentage * records_count),
                ),
            )
            for column, info in table_info.schema.items()
        ]
        sql_reqiest = f'insert into {table_name} values ({", ".join(["%s"] * len(generators))})'
        column_mapping = {column: index for index, column in enumerate(table_info.schema.keys())}
        unique_groups = [[column_mapping[column] for column in group] for group in table_info.unique_groups]
        row_generator = RowGenerator(generators, self.skip_mode_for_uniqueness, unique_groups)

        with DB(self.config) as cur:
            for row in row_generator.generate(records_count):
                try:
                    cur.execute(sql_reqiest, row)
                    cur.connection.commit()
                except errors.UniqueViolation:  # pylint: disable=no-member
                    cur.connection.rollback()
                    row_generator.generated_records_count -= 1
        self._generated_tables.add(table_name)
        LOGGER.info(f'Data for "{table_name}" was generated: {row_generator.generated_records_count} records')

    def generate_data(
        self,
        skip_tables: Optional[Set[str]] = None,
        records_count: int = 100,
        records_count_for_table: Optional[Dict[str, int]] = None,
        special_generators: Optional[Dict[str, Dict[str, GenFunction]]] = None,
    ):
        """
        Generate data for DB

        :param skip_tables: tables to skip from extracting
        :param records_count: number of records to generate
        :param records_count_for_table: special numbers of records to generate for each table
        :param special_generators: special data generators for specific columns: {table_name: {column: GenFunction}}
        """
        if skip_tables is None:
            skip_tables = set()
        self._extract_schemas(skip_tables)
        LOGGER.info('DB schemas were extracted')
        self._records_count_for_table = {} if records_count_for_table is None else records_count_for_table
        self._special_generators = {} if special_generators is None else special_generators
        self._generated_tables.clear()
        self.records_count = records_count
        for table_name in self._tables_info:
            self._generate_data_for_table(table_name)
