from .extract import get_ims_routing_by_latest_changed, get_ims_routing_by_latest_created
from .transform import concat_and_classify_ims_routings
from .load import insert_latest_routings

from prefect import flow, get_run_logger


@flow(retries=2, retry_delay_seconds=30)
def update_plan_release_report() -> None:
    logger = get_run_logger()
    logger.info("Updating Plan Release Report...")

    # extract
    latest_created_df = get_ims_routing_by_latest_created()
    latest_changed_df = get_ims_routing_by_latest_changed()

    # transform
    latest_routing_df = concat_and_classify_ims_routings(latest_created_df, latest_changed_df)

    # load
    insert_latest_routings(latest_routing_df)

    logger.info("Plan Release Report successfully updated...")
