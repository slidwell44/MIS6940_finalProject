import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text

from src.db import get_connection, WiDatabases


@task(
    name="Export PV License Level metrics",
    description="This task exports PV license level metrics",
    retries=2,
    retry_delay_seconds=30,
    tags=["PV", "EngineeringServices"],
)
def export_license_level(df: pd.DataFrame) -> None:
    logger = get_run_logger()
    logger.info("Starting export of license level data...")

    try:
        conn = get_connection(WiDatabases.WLQADWSRV_ENGINEERINGSERVICES)
        with conn.session_scope() as session:
            logger.info("explicit conversion to false to preserve values")
            df['OptionsFile'] = df['OptionsFile'].fillna(False).astype(bool)

            logger.info("Transform the data types")
            df = df.astype({
                'UserId': str,
                'Name': str,
                'Type': str,
                'SupervisorName': str,
                'OptionsFile': bool
            })

            df = df.dropna()

            logger.info("Killing data currently in tc_license.LicenseLevel...")
            # noinspection SqlNoDataSourceInspection,SqlResolve
            session.execute(
                text(
                    """
                    TRUNCATE TABLE tc_license.LicenseLevel;
                    """
                )
            )

            logger.info("Inserting data into tc_license.LicenseLevel...")
            for index, row in df.iterrows():
                # noinspection SqlNoDataSourceInspection,SqlResolve
                insert_query = text(
                    """
                    INSERT INTO tc_license.LicenseLevel(
                        UserId, 
                        Name, 
                        Type, 
                        SupervisorName, 
                        OptionsFile
                    )
                    VALUES (
                        :UserId,
                        :Name,
                        :Type,
                        :SupervisorName,
                        :OptionsFile
                    )
                    """
                )

                params = {
                    'UserId': row['UserId'],
                    'Name': row['Name'],
                    'Type': row['Type'],
                    'SupervisorName': row['SupervisorName'],
                    'OptionsFile': row['OptionsFile']
                }

                session.execute(insert_query, params)

            logger.info("License level data export completed.")
    except Exception as e:
        logger.exception(f"Failed to INSERT INTO tc_license.LicenseLevel: {e}")
        raise e
