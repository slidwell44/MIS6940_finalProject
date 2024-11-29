import pandas as pd
from prefect import get_run_logger, task

from src.db import get_connection, WiDatabases

# Disable chained assignment warnings
pd.options.mode.chained_assignment = None


@task(
    name="Get PV License Level Expanded",
    description="This task gets expanded PV license level metrics",
    retries=2,
    retry_delay_seconds=30,
    tags=["PV", "EngineeringServices"],
    result_serializer="pickle",
)
def get_pv_license_info_expanded() -> pd.DataFrame:
    logger = get_run_logger()
    logger.info("Fetching vPV_License_Info_Expanded...")

    # noinspection SqlResolve,SqlNoDataSourceInspection
    query = """
            SELECT 
                pfnd0user_id as 'UserId', 
                pfnd0seat_level as 'LicenseLevel', 
                pval as 'LicenseKeys', 
                pfnd0month as 'Month', 
                pfnd0year as 'Year', 
                pfnd0number_of_logins as 'NumberOfLogins' 
            FROM 
                tc.dbo.vPV_License_Info_Expanded
            """

    conn = get_connection(WiDatabases.WITC14DBSRV_TC)
    with conn.session_scope() as session:
        df = pd.read_sql(query, session.connection())

        logger.info(f"Head of tc.dbo.vPV_License_Info_Expanded result:\n{df.head(5)}")

        return df
