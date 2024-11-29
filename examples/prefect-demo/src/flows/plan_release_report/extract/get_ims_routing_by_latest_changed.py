from src.db import get_connection, WiDatabases

import pandas as pd
from prefect import task, get_run_logger

# Disable chained assignment warnings
pd.options.mode.chained_assignment = None


@task(
    name="Get IMS Routing by Latest Changed",
    description="This task gets IMS routings by latest changed date",
    retries=2,
    retry_delay_seconds=30,
    tags=["PV", "EngineeringServices"],
    result_serializer="pickle",
)
def get_ims_routing_by_latest_changed() -> pd.DataFrame:
    logger = get_run_logger()

    # noinspection SqlNoDataSourceInspection,SqlResolve
    query = """
        SELECT DISTINCT
            pr.PART_NO,
            TO_DATE(TO_CHAR(MAX(pr.CHNGD_ON), 'yyyymmdd'), 'YYYYMMDD') AS ims_date,
            pr.CREATED_BY,
            pr.DESCRIPTION,
            prf.WERKS,
            mm.LABORATORY,
            prf.FILEPATH,
            prf.FILENAME
        FROM 
            ZWILLIAMS.zv_wi_gu_production_routing_file prf
            LEFT JOIN ZWILLIAMS.ZV_WI_GU_Production_Routing pr 
                ON pr.PART_NO = prf.MFRPN AND pr.DESCRIPTION = prf.KTEXT
            LEFT JOIN ZWILLIAMS.ZV_WI_GU_MATERIAL_MASTER mm 
                ON pr.PART_NO = mm.PART_NO
        WHERE 
            pr.PART_NO IS NOT NULL
            AND pr.CHNGD_ON >= '20211201'
            AND prf.FILEPATH IS NOT NULL
            AND UPPER(prf.FILEPATH) NOT LIKE '%GMPLANS%'
            AND pr.CHNGD_ON IS NOT NULL
        GROUP BY 
            pr.PART_NO,
            pr.CREATED_BY,
            pr.DESCRIPTION,
            prf.WERKS,
            mm.LABORATORY,
            prf.FILEPATH,
            prf.FILENAME
        ORDER BY
            1, 2
    """

    conn = get_connection(WiDatabases.PRODHANASRV_ZWILLIAMS)
    with conn.session_scope() as session:
        result_df = pd.read_sql(query, session.connection())

    # Log the first 5 rows of the DataFrame
    logger.info(f"Head of latest changed result:\n{result_df.head(5)}")

    return result_df
