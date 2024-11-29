from prefect import flow, get_run_logger

from .extract import get_bop_tool_gauge_info
from .load import load_tool_gauge_data


@flow(name="run-tool-gauge-update", log_prints=True)
def update_tool_gauge_data():
    logger = get_run_logger()
    logger.info("Starting main flow for tool/gauge update...")

    df = get_bop_tool_gauge_info()

    load_tool_gauge_data(df)
