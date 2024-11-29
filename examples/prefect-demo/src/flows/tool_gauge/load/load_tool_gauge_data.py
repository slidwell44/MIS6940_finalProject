import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text
from src.db import get_connection, WiDatabases


@task(name="load-to-database",
      description="This task loads the Tool/Gauge data into the Engineering Service Datawarehouse.",
      retries=2,
      retry_delay_seconds=30,
      tags=["PV", "EngineeringServices"])
def load_tool_gauge_data(df: pd.DataFrame):
    logger = get_run_logger()
    logger.info("Updating Engineering Services DW...")

    # noinspection SqlNoDataSourceInspection
    insert_sql = """ INSERT INTO [dbo].[ToolGaugeData] ([BOP_ID]
                                            , [BOP_REV_ID]
                                            , [BOP_REV_NAME]
                                            , [OP_ID]
                                            , [OP_NAME]
                                            , [STEP_ID]
                                            , [STEP_NAME]
                                            , [PART_NUMBER]
                                            , [PART_REVISION]
                                            , [PART_DESCRIPTION]
                                            , [CELL]
                                            , [Tool_ID]
                                            , [ITEM_LATEST_ID])
                            VALUES (:BOP_ID, :BOP_REV_ID, :BOP_REV_NAME, :OP_ID, :OP_NAME,
                                    :STEP_ID, :STEP_NAME, :PART_NUMBER, :PART_REVISION,
                                    :PART_DESCRIPTION, :CELL, :Tool_ID, :ITEM_LATEST_ID); """
    # noinspection SqlNoDataSourceInspection
    truncate_sql = """ TRUNCATE TABLE [dbo].[ToolGaugeData]; """

    conn = get_connection(WiDatabases.WLDWSRV_ENGINEERINGSERVICES)
    with conn.session_scope() as session:

        data_tuples = [tuple(x) for x in df.to_numpy()]

        placeholder_names = [
            "BOP_ID", "BOP_REV_ID", "BOP_REV_NAME", "OP_ID", "OP_NAME",
            "STEP_ID", "STEP_NAME", "PART_NUMBER", "PART_REVISION",
            "PART_DESCRIPTION", "CELL", "Tool_ID", "ITEM_LATEST_ID"
        ]

        data_dicts = [dict(zip(placeholder_names, tup)) for tup in data_tuples]

        logger.info(f"Inserting data into ToolGaugeData table in Engineering Services DB...")

        try:
            session.execute(text(truncate_sql))
            logger.info("Table truncated successfully.")

            session.fast_executemany = True

            session.execute(text(insert_sql), data_dicts)

            logger.info("Table truncated and data inserted successfully.")

        except Exception as e:
            logger.exception(f"Failed to INSERT INTO dbo.ToolGaugeData: {e}")
            raise e
