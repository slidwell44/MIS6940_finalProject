import pandas as pd
from prefect import get_run_logger, task
from src.db import get_connection, WiDatabases


@task(name="pull-from-bop",
      description="This task gets the Tool/Gauge data for BOPs from PV",
      retries=2,
      retry_delay_seconds=30,
      tags=["PV", "EngineeringServices"])
def get_bop_tool_gauge_info():
    logger = get_run_logger()

    conn = get_connection(WiDatabases.WITC14DBSRV_TC)
    with conn.session_scope() as session:
        logger.info("Fetching PV data...")

        # noinspection SqlNoDataSourceInspection
        sql_query = """ With TempLatestReleasedRev as (

                        Select 
                            max(pitem_revision_id) as ITEM_LATEST_ID
                            , ITEM_REV_LATEST_LATEST.ritems_tagu as ITEM_LATEST_PUID
                            from 
                                    tc.dbo.vPITEMREVISION ITEM_REV_LATEST_LATEST 
                                    inner join tc.dbo.vPITEM ITEM on ITEM_REV_LATEST_LATEST.ritems_tagu = ITEM.puid
                                    inner join tc.dbo.vPRELEASE_STATUS_LIST rel_list on ITEM_REV_LATEST_LATEST.puid = rel_list.puid
                                    inner join tc.dbo.vPRELEASESTATUS status1 ON rel_list.pvalu_0 = status1.puid --find wso with release status
                                    inner join tc.dbo.vPWORKSPACEOBJECT WSO on ITEM_REV_LATEST_LATEST.puid = WSO.puid
                            where (status1.pname like 'W4_RELEASED') 
                                and WSO.pactive_seq like 1
                            group by 
                                ITEM_REV_LATEST_LATEST.ritems_tagu 
                            )

                        SELECT
                            distinct
                            prc_item.pitem_id as 'BOP_ID'
                            ,prc_item_rev.pitem_revision_id as 'BOP_REV_ID'
                            ,prc_item_rev_wso.pobject_name as 'BOP_REV_NAME'
                            ,op_item.pitem_id as 'OP_ID'
                            ,op_wso.pobject_name as 'OP_NAME'
                            ,stp_item.pitem_id as 'STEP_ID' 
                            ,stp_wso.pobject_name as 'STEP_NAME'
                            ,mfg_item.pitem_id as 'PART_NUMBER'
                            , mfg_item_rev.pitem_revision_id as 'PART_REVISION'
                            , mfg_item_rev_wso.pobject_name as 'PART_DESCRIPTION'
                            ,pw4_ResponsibleCell as 'CELL'
                            ,tool_item.pitem_id as 'Tool_ID'
                            ,Latest_Released_Tool.ITEM_LATEST_ID

                        FROM
                               -- GET PRC/BOP ITEM
                               tc.dbo.PITEM prc_item
                               INNER JOIN tc.dbo.PITEMREVISION prc_item_rev ON prc_item.puid = prc_item_rev.ritems_tagu
                               INNER JOIN tc.dbo.PWORKSPACEOBJECT prc_item_rev_wso ON prc_item_rev.puid = prc_item_rev_wso.puid AND prc_item_rev_wso.pobject_type LIKE 'W4_ProcessGroupRevision'

                               inner join TempLatestReleasedRev on prc_item.puid = TempLatestReleasedRev.ITEM_LATEST_PUID AND prc_item_rev.pitem_revision_id = TempLatestReleasedRev.ITEM_LATEST_ID

                               -- GET PART NUMBER
                               INNER JOIN tc.dbo.PIMANRELATION iman1 ON prc_item_rev.puid = iman1.rprimary_objectu
                               INNER JOIN tc.dbo.PITEMREVISION mfg_item_rev ON iman1.rsecondary_objectu = mfg_item_rev.puid
                               INNER JOIN tc.dbo.PWORKSPACEOBJECT mfg_item_rev_wso ON mfg_item_rev.puid = mfg_item_rev_wso.puid
                               INNER JOIN tc.dbo.PITEM mfg_item ON mfg_item_rev.ritems_tagu = mfg_item.puid
                                inner join tc.dbo.vPIMANTYPE Irel_Type on iman1.rrelation_typeu = Irel_Type.puid

                                --responsible cell
                                inner join tc.dbo.vPIMANRELATION Irel2 on mfg_item.puid = Irel2.rprimary_objectu
                                inner join tc.dbo.vPFORM FORM on Irel2.rsecondary_objectu = FORM.puid
                                --form to form data
                                inner join tc.dbo.vPW4_PARTATTRFORMSTORAGE PAF on FORM.rdata_fileu = PAF.puid

                               -- GET OPERATIONS
                               INNER JOIN tc.dbo.PSTRUCTURE_REVISIONS BOP_structure ON prc_item_rev.puid = BOP_structure.puid
                               INNER JOIN tc.dbo.PPSBOMVIEWREVISION BOP_bvr ON BOP_structure.pvalu_0 = BOP_bvr.puid
                               INNER JOIN tc.dbo.PPSOCCURRENCE op_occ ON BOP_bvr.puid = op_occ.rparent_bvru
                               INNER JOIN tc.dbo.PITEMREVISION op_rev ON op_occ.rchild_itemu = op_rev.puid
                               INNER JOIN tc.dbo.PWORKSPACEOBJECT op_wso ON op_rev.puid = op_wso.puid AND op_wso.pobject_type LIKE 'W4_ProcessRevision'
                               INNER JOIN tc.dbo.PITEM op_item ON op_rev.ritems_tagu = op_item.puid

                               -- GET STEPS
                               INNER JOIN tc.dbo.PSTRUCTURE_REVISIONS op_structure ON op_rev.puid = op_structure.puid
                               INNER JOIN tc.dbo.PPSBOMVIEWREVISION op_bvr ON op_structure.pvalu_0 = op_bvr.puid
                               INNER JOIN tc.dbo.PPSOCCURRENCE stp_occ ON op_bvr.puid = stp_occ.rparent_bvru
                               INNER JOIN tc.dbo.PITEMREVISION stp_rev ON stp_occ.rchild_itemu = stp_rev.puid
                               INNER JOIN tc.dbo.PWORKSPACEOBJECT stp_wso ON stp_rev.puid = stp_wso.puid AND stp_wso.pobject_type LIKE 'W4_ManualWorkRevision'
                               INNER JOIN tc.dbo.PITEM stp_item ON stp_rev.ritems_tagu = stp_item.puid

                                --get tools. tools are imprecise so it uses the sub query below to just grab latest released rev if there is one. 
                                INNER JOIN tc.dbo.PSTRUCTURE_REVISIONS STEP_structure ON stp_rev.puid = STEP_structure.puid
                                INNER JOIN tc.dbo.PPSBOMVIEWREVISION STEP_bvr ON STEP_structure.pvalu_0 = STEP_bvr.puid
                                INNER JOIN tc.dbo.PPSOCCURRENCE tool_occ ON STEP_bvr.puid = tool_occ.rparent_bvru
                                INNER JOIN tc.dbo.PITEM tool_item ON tool_occ.rchild_itemu = tool_item.puid
                                --INNER JOIN tc.dbo.PITEMREVISION tool_rev ON tool_item.puid = tool_rev.ritems_tagu
                                INNER JOIN tc.dbo.PWORKSPACEOBJECT tool_wso ON tool_item.puid = tool_wso.puid AND tool_wso.pobject_type LIKE '%Tool%'

                                left join 
                                (
                                    Select ITEM_LATEST_PUID, ITEM_LATEST_ID
                                    from TempLatestReleasedRev
                                )Latest_Released_Tool on tool_item.puid = Latest_Released_Tool.ITEM_LATEST_PUID

                        WHERE
                                Irel_Type.ptype_name like 'IMAN_METarget'


                        """

        df = pd.read_sql(sql_query, session.connection())

        return df
