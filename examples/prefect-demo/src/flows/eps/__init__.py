from prefect import flow, get_run_logger

from .extract import get_eps_info
from .load import load_eps_data


@flow(name="run-esp-info-update", log_prints=True)
def update_eps_data():
    logger = get_run_logger()
    logger.info("Starting main flow for ESP Info update...")

    df = get_eps_info()

    load_eps_data(df)
