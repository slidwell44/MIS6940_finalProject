import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text
from src.db import get_connection, WiDatabases


@task(name="load-to-database",
      description="This task loads the MECN data into the Engineering Service Datawarehouse.",
      retries=2,
      retry_delay_seconds=30,
      tags=["PV", "EngineeringServices"])
def load_mecn_data(df: pd.DataFrame):
    logger = get_run_logger()
    logger.info("Updating Engineering Services DW...")

    # noinspection SqlNoDataSourceInspection
    truncate_sql = """ TRUNCATE TABLE [dbo].[MECNData] """
    # noinspection SqlNoDataSourceInspection
    insert_sql = """ INSERT INTO [dbo].[MECNData] ([MECN_ID], [MECN_Rev_ID], [Author], [ChangeType], [ChangeDesc],
                                                    [SubReqd], [SubResults], [DeltaFAI], [FAIReqd])
                     VALUES (:MECN_ID, :MECN_Rev_ID, :Author, :ChangeType, :ChangeDesc,
                             :SubReqd, :SubResults, :DeltaFAI, :FAIReqd);
                """

    conn = get_connection(WiDatabases.WLDWSRV_ENGINEERINGSERVICES)
    with conn.session_scope() as session:

        data_tuples = [tuple(x) for x in df.to_numpy()]

        placeholder_names = [
            "MECN_ID", "MECN_Rev_ID", "Author", "ChangeType", "ChangeDesc",
            "SubReqd", "SubResults", "DeltaFAI", "FAIReqd"
        ]

        data_dicts = [dict(zip(placeholder_names, tup)) for tup in data_tuples]

        logger.info(f"Inserting data into MECNData table in Engineering Services DB...")

        try:
            session.execute(text(truncate_sql))
            logger.info("Table truncated successfully.")

            session.fast_executemany = True

            session.execute(text(insert_sql), data_dicts)

            logger.info("Table truncated and data inserted successfully.")

        except Exception as e:
            logger.exception(f"Failed to INSERT INTO dbo.MECNData: {e}")
            raise e
