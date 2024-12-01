import abc
from contextlib import contextmanager
import logging
from sqlalchemy import create_engine, Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import urllib.parse

from .databases import WiDatabases
from .db_dialects import WiDialects


class WiDatabaseConnection(abc.ABC):
    def __init__(
            self,
            widatabase: WiDatabases,
            trusted_connection: bool = False,
            username: Optional[str] = None,
            password: Optional[str] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing WiDatabaseConnection for {widatabase.name}")

        self.widatabase = widatabase
        self._host = widatabase.host
        self._port = widatabase.port
        self._database = widatabase.database
        self._dialect = widatabase.dialect
        self.trusted_connection = trusted_connection
        self.__username = username
        self.__password = password
        self.engine: Optional[Engine] = None
        self.SessionLocal = None

    def get_engine(self) -> Engine:
        """Creates and returns a SQLAlchemy engine based on the provided configuration."""
        if self.engine:
            self.logger.info(f"Using cached engine for database {self.widatabase.name}")
            return self.engine

        self.logger.info(f"Creating new engine for database {self.widatabase.name}")
        try:
            if self._dialect == WiDialects.MSSQL:
                odbc_driver = "ODBC Driver 17 for SQL Server"
                driver = "pyodbc"
                drivername = f"{self._dialect.value}+{driver}"
                query = {"driver": odbc_driver, "trusted_connection": "yes"} if self.trusted_connection else {
                    "driver": odbc_driver}

                if self.trusted_connection:
                    connection_url = URL.create(
                        drivername=drivername,
                        host=self._host,
                        database=self._database,
                        query=query,
                    )
                elif self.__username and self.__password:
                    username = urllib.parse.quote_plus(self.__username)
                    password = urllib.parse.quote_plus(self.__password)
                    connection_url = URL.create(
                        drivername=drivername,
                        username=username,
                        password=password,
                        host=self._host,
                        database=self._database,
                        query=query,
                    )
                else:
                    error_msg = "Either trusted_connection must be True or both username and password must be provided."
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

            elif self._dialect == WiDialects.HANA:
                driver = "hdbcli"
                drivername = f"{self._dialect.value}+{driver}"

                connection_url = URL.create(
                    drivername=drivername,
                    username=self.__username,
                    password=self.__password,
                    host=self._host,
                    port=self._port,
                )
            else:
                raise ValueError(f"Unsupported dialect: {self._dialect}")

            # Create the engine
            self.engine = create_engine(
                connection_url,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False,
            )
            self.logger.info(f"Engine created successfully for {self.widatabase.name}")
            self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
            self.logger.debug("SessionLocal has been initialized.")
            return self.engine

        except Exception as e:
            self.logger.error(f"Failed to create engine for database {self.widatabase.name}: {e}")
            raise ConnectionError(f"Failed to create engine for database {self.widatabase.name}") from e

    def get_session(self) -> Session:
        """Creates and returns a new SQLAlchemy session."""
        if not self.engine:
            self.logger.debug("Engine not initialized. Initializing engine before creating session.")
            self.get_engine()

        if not self.SessionLocal:
            error_msg = "SessionLocal not initialized. Engine must be initialized first."
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        self.logger.info(f"Creating new session for database {self.widatabase.name}")
        try:
            session = self.SessionLocal()
            self.logger.debug(f"Session created: {session}")
            return session
        except Exception as e:
            self.logger.error(
                f"Failed to create session for database {self.widatabase.name}: {e}"
            )
            raise RuntimeError(
                f"Failed to create session for database {self.widatabase.name}"
            ) from e

    @contextmanager
    def session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
            self.logger.info("Session committed successfully.")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Session rollback due to error: {e}")
            raise
        finally:
            session.close()
            self.logger.info("Session closed.")
