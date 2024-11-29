from sqlalchemy import create_engine, Engine


class Wlqadbsrv:
    def __init__(self):
        self.__username = "ZMES"
        self.__password = "Love4stars"
        self.__server = "wlqadbsrv"
        self.__database = "EngineeringServices"
        self.__connection_string = f"mssql+pyodbc://{self.__username}:{self.__password}@{self.__server}/{self.__database}?driver=ODBC Driver 17 for SQL Server"
        self.engine: Engine = create_engine(self.__connection_string,
                                            connect_args={"check_same_thread": False},
                                            fast_executemany=True,
                                            pool_pre_ping=True,
                                            echo=False)


def get_engine():
    return Wlqadbsrv()
