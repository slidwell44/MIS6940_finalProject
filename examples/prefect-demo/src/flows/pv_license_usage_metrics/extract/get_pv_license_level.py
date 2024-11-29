import pandas as pd
from prefect import get_run_logger, task

from src.db import get_connection, WiDatabases

# Disable chained assignment warnings
pd.options.mode.chained_assignment = None

rename_cols = {
    "puser_id": "UserId",
    "puser_name": "Name",
    "pstatus": "Status",
    "plicense_level": "LicenseLevel"
}


@task(
    name="Get PV License Level",
    description="This task gets PV license level metrics",
    retries=2,
    retry_delay_seconds=30,
    tags=["PV", "EngineeringServices"],
    result_serializer="pickle",
)
def get_pv_license_level() -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("Getting tc.dbo.vPV_License_Level...")

    # noinspection SqlNoDataSourceInspection,SqlResolve
    query = """
            SELECT 
                *
            FROM 
                tc.dbo.vPV_License_Level
            """

    conn = get_connection(WiDatabases.WITC14DBSRV_TC)
    with conn.session_scope() as session:
        df = pd.read_sql(query, session.connection())

        logger.info("Renaming columns")
        df = df.rename(columns=rename_cols)

        logger.info(f"Head of tc.dbo.vPV_License_Level result:\n{df.head(5)}")

        return df
