from typing import Dict, Union
from .databases import WiDatabases
from .hanadb_connection import HanaDbConnection
from .mssql_connection import MssqlDbConnection
from .db_dialects import WiDialects

_connection_registry: Dict[WiDatabases, Union[MssqlDbConnection, HanaDbConnection]] = {}


def get_connection(database: WiDatabases) -> Union[MssqlDbConnection, HanaDbConnection]:
    """
    Factory function to retrieve a database connection instance based on the provided WiDatabases enum member.

    Args:
        database (WiDatabases): The database enum member.

    Returns:
        Union[MssqlDbConnection, HanaDbConnection]: An instance of the appropriate connection class.
    """
    if database in _connection_registry:
        return _connection_registry[database]

    if database.dialect == WiDialects.MSSQL:
        if database == WiDatabases.WITC14DBSRV_TC:
            connection = MssqlDbConnection(
                database=database,
                username="ZMFG",
                password="Love4air",
            )
        else:
            connection = MssqlDbConnection(
                database=database,
                trusted_connection=True,
            )
    elif database.dialect == WiDialects.HANA:
        connection = HanaDbConnection(
            database=database,
            username="ZMFG_US",
            password="ZW!m7890",
        )
    else:
        raise ValueError(f"Unsupported dialect: {database.dialect}")

    _connection_registry[database] = connection
    return connection
