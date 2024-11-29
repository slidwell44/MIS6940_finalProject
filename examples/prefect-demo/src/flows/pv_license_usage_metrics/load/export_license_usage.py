import pandas as pd
from prefect import get_run_logger, task
from sqlalchemy import text

from src.db import get_connection, WiDatabases


# TODO - Write this so that the query appends to the existing data rather than kill and fill


@task(
    name="Export PV License Usage metrics",
    description="This task exports PV license usage metrics",
    retries=2,
    retry_delay_seconds=30,
    tags=["PV", "EngineeringServices"],
)
def export_license_usage(df: pd.DataFrame) -> None:
    logger = get_run_logger()
    logger.info("Starting export of license usage data...")

    try:
        conn = get_connection(WiDatabases.WLQADWSRV_ENGINEERINGSERVICES)
        with conn.session_scope() as session:
            logger.info("Validating data types")
            df = df.astype({
                'UserId': str,
                'LicenseLevel': str,
                'LicenseKeys': str,
                'Year': int,
                'NumberOfLogins': int,
                'Day': int,
                'LicenseKey': str
            })

            # If 'Month' column is not already the month number, extract it
            if not pd.api.types.is_integer_dtype(df['Month']):
                df['Month'] = pd.to_datetime(df['Month'], errors='coerce').dt.month

            df = df.dropna()

            logger.info("Truncating data in tc_license.LicenseUsage...")
            # noinspection SqlNoDataSourceInspection,SqlResolve
            session.execute(
                text(
                    """
                    TRUNCATE TABLE tc_license.LicenseUsage;
                    """
                )
            )

            logger.info("Inserting data into tc_license.LicenseUsage...")
            for index, row in df.iterrows():
                # noinspection SqlResolve,SqlNoDataSourceInspection
                insert_query = text(
                    """
                    INSERT INTO tc_license.LicenseUsage (
                        UserId, 
                        LicenseLevel, 
                        LicenseKeys, 
                        Month, 
                        Year, 
                        NumberOfLogins, 
                        Day, 
                        LicenseKey
                    )
                    VALUES (
                        :UserId, 
                        :LicenseLevel, 
                        :LicenseKeys, 
                        :Month, 
                        :Year, 
                        :NumberOfLogins, 
                        :Day, 
                        :LicenseKey
                    )
                    """
                )

                params = {
                    'UserId': row['UserId'],
                    'LicenseLevel': row['LicenseLevel'],
                    'LicenseKeys': row['LicenseKeys'],
                    'Month': row['Month'],
                    'Year': row['Year'],
                    'NumberOfLogins': row['NumberOfLogins'],
                    'Day': row['Day'],
                    'LicenseKey': row['LicenseKey']
                }

                session.execute(insert_query, params)

            logger.info("License usage data export completed.")
    except Exception as e:
        logger.exception(f"Failed to INSERT INTO tc_license.LicenseUsage: {e}")
        raise e
