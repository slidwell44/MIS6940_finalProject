from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class Widevdbsrv:
    def __init__(self):
        self.__username = "ZMES"
        self.__password = "Love4stars"
        self.__server = "widevdbsrv"
        self.__database = "EngineeringServices"
        self.__connection_string = f"mssql+pyodbc://{self.__username}:{self.__password}@{self.__server}/{self.__database}?driver=ODBC+Driver+17+for+SQL+Server"
        self.engine: Engine = create_engine(self.__connection_string,
                                            connect_args={"check_same_thread": False},
                                            fast_executemany=True,
                                            pool_pre_ping=True,
                                            echo=False)


def get_engine() -> Widevdbsrv:
    return Widevdbsrv()
