import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text
from src.db import get_connection, WiDatabases


@task(name="load-to-database",
      description="This task loads the EPS data into the Engineering Service Datawarehouse.",
      retries=2,
      retry_delay_seconds=30,
      tags=["PV", "EngineeringServices"])
def load_eps_data(df: pd.DataFrame):
    logger = get_run_logger()
    logger.info("Updating Engineering Services DW...")

    # noinspection SqlNoDataSourceInspection
    insert_sql = """
                    INSERT INTO [dbo].[EpsBasicData] ([PV_Part_Number], [PV_Rev_ID], [EP_Name], [PV_Mfr_PN], [PV_Mfr_Name],
                              [Country_Origin], [Status], [Path])
                    VALUES (:PV_Part_Number, :PV_Rev_ID, :EP_Name, :PV_Mfr_PN, :PV_Mfr_Name,
                              :Country_Origin, :Status, :Path);
                """
    # noinspection SqlNoDataSourceInspection
    truncate_sql = """ TRUNCATE TABLE [dbo].[EpsBasicData]; """

    conn = get_connection(WiDatabases.WLDWSRV_ENGINEERINGSERVICES)
    with conn.session_scope() as session:

        data_tuples = [tuple(x) for x in df.to_numpy()]

        placeholder_names = [
            "PV_Part_Number", "PV_Rev_ID", "EP_Name",
            "PV_Mfr_PN", "PV_Mfr_Name",
            "Country_Origin", "Status", "Path"
        ]

        data_dicts = [dict(zip(placeholder_names, tup)) for tup in data_tuples]

        logger.info(f"Inserting data into EPS Info table in Engineering Services DB...")

        try:
            session.execute(text(truncate_sql))
            logger.info("Table truncated successfully.")

            session.fast_executemany = True

            session.execute(text(insert_sql), data_dicts)

            logger.info("Table truncated and data inserted successfully.")

        except Exception as e:
            logger.error(f"Error occurred: {e}")
            raise e
