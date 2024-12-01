from enum import Enum
from typing import Optional
from .db_dialects import WiDialects


class WiDatabases(Enum):
    WLDWSRV_ENGINEERINGSERVICES = ("wldwsrv", "engineeringservices", WiDialects.MSSQL, None)
    WLQADWSRV_ENGINEERINGSERVICES = ("wlqadwsrv", "engineeringservices", WiDialects.MSSQL, None)
    WIDEVDBSRV_ENGINEERINGSERVICES = ("widevdbsrv", "engineeringservices", WiDialects.MSSQL, None)
    PRODHANASRV_ZWILLIAMS = ("prodhanasrv", "zwilliams", WiDialects.HANA, 30015)
    WITC14DBSRV_TC = ("witc14dbsrv", "tc", WiDialects.MSSQL, None)

    def __init__(self, host: str, database: str, dialect: WiDialects, port: Optional[int]):
        self._host = host
        self._database = database
        self._dialect = dialect
        self._port = port

    @property
    def host(self) -> str:
        """Returns the host name."""
        return self._host

    @property
    def database(self) -> str:
        """Returns the database name."""
        return self._database

    @property
    def dialect(self) -> WiDialects:
        """Returns the database dialect."""
        return self._dialect

    @property
    def port(self) -> Optional[int]:
        """Returns the port number if specified."""
        return self._port
