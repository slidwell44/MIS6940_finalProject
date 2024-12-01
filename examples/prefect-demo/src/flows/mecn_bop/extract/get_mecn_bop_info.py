import pandas as pd
from prefect import get_run_logger, task
from src.db import get_connection, WiDatabases


@task(name="pull-from-mecn",
      description="This task gets the MECN/BOP data from PV",
      retries=2,
      retry_delay_seconds=30,
      tags=["PV", "EngineeringServices"])
def get_mecn_bop_info():
    logger = get_run_logger()

    conn = get_connection(WiDatabases.WITC14DBSRV_TC)
    with conn.session_scope() as session:
        logger.info("Fetching PV data...")

        # noinspection SqlNoDataSourceInspection
        sql_query = """
            Select ITEM_MECN.pitem_id                                              as 'MECN_ID'
                 , ITEM_REV_MECN.pitem_revision_id                                 as 'MECN_REV_ID'
                 , WSO_BOP_REV.pobject_name + '_' + ITEM_REV_BOP.pitem_revision_id as 'full_name'
            from tc.dbo.vPITEM ITEM_MECN
                     inner join tc.dbo.vPWORKSPACEOBJECT WSO_MECN on ITEM_MECN.puid = WSO_MECN.puid
                     inner join tc.dbo.vPITEMREVISION ITEM_REV_MECN on ITEM_MECN.puid = ITEM_REV_MECN.ritems_tagu
                     inner join tc.dbo.vPIMANRELATION Irel on ITEM_REV_MECN.puid = Irel.rprimary_objectu
                     inner join tc.dbo.vPITEMREVISION ITEM_REV_BOP on Irel.rsecondary_objectu = ITEM_REV_BOP.puid
                     inner join tc.dbo.vPWORKSPACEOBJECT WSO_BOP_REV on ITEM_REV_BOP.puid = WSO_BOP_REV.puid
                     inner join tc.dbo.vPITEM ITEM_BOP on ITEM_REV_BOP.ritems_tagu = ITEM_BOP.puid

                --rel type
                     inner join tc.dbo.vPIMANTYPE rel_type on Irel.rrelation_typeu = rel_type.puid
            where WSO_MECN.pobject_type like 'W4_MECN_VCR'
              AND WSO_BOP_REV.pobject_type like 'W4_ProcessGroupRevision'
              AND rel_type.ptype_name like 'CMHasSolutionItem'
        """

        df = pd.read_sql(sql_query, session.connection())

        return df
