import pandas as pd
from prefect import task, get_run_logger
from sqlalchemy import text

from src.db import get_connection, WiDatabases


@task(
    name="Export Plan Release Report",
    description="This task inserts the Plan Release Report into DW",
    retries=2,
    retry_delay_seconds=30,
    tags=["PV", "EngineeringServices"],
)
def insert_latest_routings(ims_routings_df: pd.DataFrame) -> None:
    logger = get_run_logger()

    # Rename DataFrame columns to match SQL table schema
    ims_routings_df = ims_routings_df.rename(columns={
        "part_no": "PartNumber",
        "ims_date": "ImsDate",
        "created_by": "CreatedBy",
        "description": "Description",
        "werks": "Plant",
        "laboratory": "Laboratory",
        "filepath": "Filepath",
        "filename": "Filename"
    })

    # Ensure correct data types
    ims_routings_df["PartNumber"] = ims_routings_df["PartNumber"].astype(str)
    ims_routings_df["ImsDate"] = pd.to_datetime(ims_routings_df["ImsDate"], errors='coerce').dt.date
    ims_routings_df["CreatedBy"] = ims_routings_df["CreatedBy"].astype(str)
    ims_routings_df["Description"] = ims_routings_df["Description"].astype(str)
    ims_routings_df["Plant"] = ims_routings_df["Plant"].astype(int)
    ims_routings_df["Laboratory"] = ims_routings_df["Laboratory"].astype(str)
    ims_routings_df["Filepath"] = ims_routings_df["Filepath"].astype(str)
    ims_routings_df["Filename"] = ims_routings_df["Filename"].astype(str)

    # Ensure 'Source' column exists and is of type str
    if 'Source' not in ims_routings_df.columns:
        ims_routings_df['Source'] = None
    else:
        ims_routings_df['Source'] = ims_routings_df['Source'].astype(str)

    conn = get_connection(WiDatabases.WLQADWSRV_ENGINEERINGSERVICES)
    with conn.session_scope() as session:
        try:
            logger.info("Truncating data in EngineeringServices.dbo.PlanReleaseReport...")
            # noinspection SqlResolve,SqlNoDataSourceInspection
            session.execute(
                text(
                    """
                    TRUNCATE TABLE dbo.PlanReleaseReport;
                    """
                )
            )

            logger.info("Inserting data into dbo.PlanReleaseReport...")
            # noinspection SqlNoDataSourceInspection,SqlResolve
            insert_query = text(
                """
                INSERT INTO dbo.PlanReleaseReport (
                    PartNumber, 
                    ImsDate, 
                    CreatedBy, 
                    Description, 
                    Laboratory, 
                    Filepath, 
                    Filename, 
                    Source, 
                    Plant
                )
                VALUES (
                    :PartNumber, 
                    :ImsDate, 
                    :CreatedBy, 
                    :Description, 
                    :Laboratory, 
                    :Filepath, 
                    :Filename, 
                    :Source, 
                    :Plant
                )
                """
            )

            # Iterate over DataFrame rows and execute parameterized queries
            for index, row in ims_routings_df.iterrows():
                params = {
                    'PartNumber': row['PartNumber'],
                    'ImsDate': row['ImsDate'],
                    'CreatedBy': row['CreatedBy'],
                    'Description': row['Description'],
                    'Laboratory': row['Laboratory'],
                    'Filepath': row['Filepath'],
                    'Filename': row['Filename'],
                    'Source': row['Source'] if pd.notnull(row['Source']) else None,
                    'Plant': row['Plant']
                }
                session.execute(insert_query, params)

            logger.info("PlanReleaseReport inserted successfully")
        except Exception as e:
            logger.exception(f"Failed to insert PlanReleaseReport: {e}")
