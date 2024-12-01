from .base_connection import WiDatabaseConnection
from .databases import WiDatabases


class HanaDbConnection(WiDatabaseConnection):
    def __init__(
            self,
            database: WiDatabases,
            username: str,
            password: str,
            trusted_connection: bool = False,
    ):
        super().__init__(database, trusted_connection, username, password)
