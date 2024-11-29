import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text
from src.db import get_connection, WiDatabases


@task(name="load-to-database")
def load_mecn_bop_data(df: pd.DataFrame):
    logger = get_run_logger()
    logger.info("Updating Engineering Services DW...")

    # noinspection SqlNoDataSourceInspection
    insert_sql = """ INSERT INTO [dbo].[MECNBOPData] ([MECN_ID]
                                                    , [MECN_REV_ID]
                                                    , [full_name])
                               VALUES(:MECN_ID, :MECN_REV_ID, :full_name); """

    # noinspection SqlNoDataSourceInspection
    truncate_sql = """ TRUNCATE TABLE [dbo].[MECNBOPData] """

    conn = get_connection(WiDatabases.WLDWSRV_ENGINEERINGSERVICES)
    with conn.session_scope() as session:

        data_tuples = [tuple(x) for x in df.to_numpy()]

        placeholder_names = [
            "MECN_ID", "MECN_REV_ID", "full_name"
        ]

        data_dicts = [dict(zip(placeholder_names, tup)) for tup in data_tuples]

        logger.info(f"Inserting data into MECNBOP table in Engineering Services DB...")

        try:
            session.execute(text(truncate_sql))
            logger.info("Table truncated successfully.")

            session.fast_executemany = True

            session.execute(text(insert_sql), data_dicts)

            logger.info("Table truncated and data inserted successfully.")

        except Exception as e:
            logger.error(f"Error occurred: {e}")
            raise e
