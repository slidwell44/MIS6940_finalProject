from prefect import flow, get_run_logger

from .extract import get_mecn_info
from .load import load_mecn_data


@flow(name="run-mecn-data-update", log_prints=True)
def update_mecn_data():
    logger = get_run_logger()
    logger.info("Starting the main flow for mecn update...")

    df = get_mecn_info()

    load_mecn_data(df)
