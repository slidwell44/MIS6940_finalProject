from prefect import flow, get_run_logger

from .extract import get_mecn_bop_info
from .load import load_mecn_bop_data


@flow(name="run-mecn-bop-update", log_prints=True)
def update_mecn_bop_data():
    logger = get_run_logger()
    logger.info("Starting main flow for mecn/bop update...")

    df = get_mecn_bop_info()

    load_mecn_bop_data(df)
