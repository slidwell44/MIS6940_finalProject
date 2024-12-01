import pandas as pd
from prefect import get_run_logger, task
from src.db import get_connection, WiDatabases


@task(name="pull-from-team-center",
      description="This task gets the Tool/Gauge data for BOPs from PV",
      retries=2,
      retry_delay_seconds=30,
      tags=["PV", "EngineeringServices"])
def get_mecn_info():
    logger = get_run_logger()

    conn = get_connection(WiDatabases.WITC14DBSRV_TC)
    with conn.session_scope() as session:
        logger.info("Fetching PV data...")

        # noinspection SqlNoDataSourceInspection
        sql_query = """ Select 
                            MECN_ITEM.pitem_id as 'MECN_ID'
                            ,MECN_ITEM_REV.pitem_revision_id as 'MECN_REV_ID'
                            ,person.puser_name as 'Author'
                            ,MECN_FORM.pw4_MECNChangeType as 'ChangeType'
                            ,changeDes.pval as 'ChangeDesc'
                            ,subReq2.pval as 'SubReqd'
                            ,results.pval as 'SubResults'
                            ,pw4_DeltaFAI as 'DeltaFAI'
                            ,FAI.pval as 'FAIReqd'

                        from
                            tc.dbo.vPITEM MECN_ITEM
                            inner join tc.dbo.vPITEMREVISION MECN_ITEM_REV on MECN_ITEM.puid = MECN_ITEM_REV.ritems_tagu
                            inner join tc.dbo.vPWORKSPACEOBJECT MECN_REV_WSO on MECN_ITEM_REV.puid = MECN_REV_WSO.puid 
                            inner join tc.dbo.vPIMANRELATION Irel2 on MECN_ITEM_REV.puid = Irel2.rprimary_objectu
                            inner join tc.dbo.vPFORM FORM on Irel2.rsecondary_objectu = FORM.puid
                            inner join tc.dbo.PW4_MECN_VCR_FORMSTORAGE MECN_FORM on FORM.rdata_fileu = MECN_FORM.puid
                            inner join tc.dbo.vPPOM_APPLICATION_OBJECT MECN_POM on MECN_ITEM_REV.puid = MECN_POM.puid
                            inner join tc.dbo.vPUSER user1 on MECN_POM.rowning_useru = user1.puid
                            inner join tc.dbo.PPERSON person on user1.rpersonu = person.puid

                            inner join tc.dbo.PW4_CHANGEDESCRIPTION changeDes on MECN_FORM.puid = changeDes.puid
                            inner join tc.dbo.PW4_SUBSTANTIONREQ subReq2 on MECN_FORM.puid = subReq2.puid
                            inner join tc.dbo.PW4_RESULTS results on MECN_FORM.puid = results.puid
                            inner join tc.dbo.PW4_FAIR FAI on MECN_FORM.puid = FAI.puid

                            --rel status migration
                            inner join 
                            (
                                select 
                                    rel_list.puid as rel_list_puid, status1.pname as STATUS_NAME, status1.pdate_released
                                from
                                    tc.dbo.vPRELEASE_STATUS_LIST rel_list 
                                    inner join tc.dbo.vPRELEASESTATUS status1 ON rel_list.pvalu_0 = status1.puid --find wso with release status
                                where status1.pname in ('W4_RELEASED')
                            )RELS ON MECN_ITEM_REV.puid = RELS.rel_list_puid --find wso with release status	
                    """

        df = pd.read_sql(sql_query, session.connection())

    return df
