import pandas as pd
from prefect import get_run_logger, task
from src.db import get_connection, WiDatabases


@task(name="pull-from-team-center",
      description="This task gets the EPS data for BOPs from PV",
      retries=2,
      retry_delay_seconds=30,
      tags=["PV", "EngineeringServices"])
def get_eps_info():
    logger = get_run_logger()

    conn = get_connection(WiDatabases.WITC14DBSRV_TC)
    with conn.session_scope() as session:
        logger.info("Fetching PV data...")

        # noinspection SqlNoDataSourceInspection
        sql_query = """
                        select 
                            pitem_id as 'PV_Part_Number'
                            ,itemRev.pitem_revision_id as 'PV_Rev_ID'
                            , WSO_ItemRev.pobject_name as 'EP_Name'
                            , WSO_Form.pobject_name as 'PV_Mfr_PN'
                            , pw4_MfgName as 'PV_Mfr_Name'
                            , pw4_CountryOrigin as 'Country_Origin'
                            ,T3.[REL STATUS] as 'Status'
                            ,pw4_EDAFPLibPath as 'Path'

                        from
                            tc.dbo.vPITEM item
                            inner join tc.dbo.vPWORKSPACEOBJECT WSO on item.puid = WSO.puid
                            inner join tc.dbo.vPITEMREVISION itemRev on item.puid = itemRev.ritems_tagu
                            inner join tc.dbo.PIMANRELATION ImanRelation on itemRev.puid = ImanRelation.rprimary_objectu
                            inner join tc.dbo.vPWORKSPACEOBJECT WSO_ItemRev on itemRev.puid = WSO_ItemRev.puid
                            inner JOIN tc.dbo.PFORM Form on ImanRelation.rsecondary_objectu = Form.puid --Iman relation table to form (inner since I only want relations that are forms)
                            inner JOIN tc.dbo.PW4_EDAMFGFORMSTORAGE MFG_Form on Form.rdata_fileu = MFG_Form.puid
                            inner join tc.dbo.PWORKSPACEOBJECT WSO_Form on Form.puid = WSO_Form.puid
                            inner join tc.dbo.PIMANTYPE ImanRelationType on ImanRelation.rrelation_typeu = ImanRelationType.puid


                            left join
                            (
                                --ECRO Rel Status
                                select
                                    rel_list.puid
                                    ,status1.pname as [REL STATUS]
                                from
                                    tc.dbo.vPRELEASE_STATUS_LIST rel_list --find wso with release status
                                    left join tc.dbo.vPRELEASESTATUS status1 ON rel_list.pvalu_0 = status1.puid --find wso with release status
                            ) T3 ON itemRev.puid = T3.puid

                        where 
                            WSO.pobject_type like 'W4_EDA_Comp'
                        order by pitem_id
        """

        df = pd.read_sql(sql_query, session.connection())

    return df
