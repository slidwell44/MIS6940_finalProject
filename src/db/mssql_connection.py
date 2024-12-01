from typing import Optional

from .base_connection import WiDatabaseConnection
from .databases import WiDatabases


class MssqlDbConnection(WiDatabaseConnection):
    def __init__(
            self,
            database: WiDatabases,
            trusted_connection: bool = False,
            username: Optional[str] = None,
            password: Optional[str] = None,
    ):
        super().__init__(database, trusted_connection, username, password)
