import pandas as pd
from prefect import get_run_logger, task


@task(
    name="Transform PV License Level Expanded",
    description="Does some basic transformations on PV License Level Expanded",
    tags=["PV", "EngineeringServices"],
)
def transform_pv_license_level_expanded(df: pd.DataFrame) -> pd.DataFrame:
    """Process and transform data"""
    logger = get_run_logger()
    logger.info("Processing license usage data...")

    df['Month'] += 1
    df['Day'] = 1
    df['Month'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    df['LicenseKey'] = df['LicenseKeys'].str.split(',').map(lambda elements: [e.strip() for e in elements])
    df = df.explode('LicenseKey')
    df = df.sort_values(by='Month')
    df = df.reset_index(drop=True)

    # Filter data
    StartDate = '2022-05-01'
    df = df.loc[(df['Month'] >= StartDate)]

    return df
