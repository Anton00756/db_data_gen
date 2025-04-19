# Introduction

Package to generate data in Postgres database based on schema.

*Tested on Postgres 14 and Python 3.8*

### Installation

`pip install db_data_gen[==<version>]`

### Usage

```python
import os
from db_data_gen import DBDataGenerator


if __name__ == '__main__':
    generator = DBDataGenerator(
        {
            'database': os.environ.get('POSTGRES_DB'),
            'user': os.environ.get('POSTGRES_USER'),
            'password': os.environ.get('POSTGRES_PASSWORD'),
            'host': os.environ.get('POSTGRES_HOST'),
            'port': os.environ.get('POSTGRES_PORT'),
        }
    )
    generator.generate_data(skip_tables={'table_to_skip'}, records_count=150)
```

### Customization

1. You can change generator classes to create data based on column type
2. You can set special data generators for specific columns
3. You can set percentage of data that can be NULL
4. You can choose uniqueness mode: if value for unique column or column groups is repeated, then you can skip value output or generate it until it becomes unique
5. You can select tables for which you don`t need to generate data
6. You can set global records count (for all tables) and set special number for some tables

### Expansion

#### Adding new Postgres data types:

1. Extend ColumnType in src/db_data_gen/table_info.py

2. Add new generators in 'STANDART_GENERATION_FUNCTIONS' in src/db_data_gen/generator.py or pass dict of generators to DBDataGenerator

#### Getting additional information about column from DB:

Extend 'ADDITIONAL_FIELDS' in ColumnInfo in src/db_data_gen/table_info.py to get more information about column from table "information_schema.columns"

### Package build

#### Dev version:

Build dev version:

```shell
python3 -m pip install poetry
poetry build
```

To install package use:
```shell
pip install dist/PACKAGE.whl
```

#### Product version:

**TODO**

## DB data generator algorithm

1. Extract tables information from DB:
    - table list from DB table "information_schema.tables"
    - column info from DB table "information_schema.columns"
    - unique values and primary key columns from DB tables "pg_class", "pg_index" and "pg_attribute"
    - foreign keys from DB table "information_schema.table_constraints", "information_schema.key_column_usage" and "information_schema.constraint_column_usage"
2. Generate data for each table:

    1. If table has dependencies on other tables, then generate these tables first
    2. List of generators is generated for table: if there is no specific data generator for column, then generator is created based on column type
    3. Row values are generated for insertion into table