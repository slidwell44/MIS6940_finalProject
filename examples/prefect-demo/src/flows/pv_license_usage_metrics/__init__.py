import numpy as np
import pandas as pd
from prefect import flow, get_run_logger

from .extract import get_pv_license_level, get_pv_license_info_expanded
from .transform import transform_pv_license_level_expanded
from .load import export_license_level, export_license_usage

from .utils import grab_ID_from_number, grab_ID_from_string


@flow(name="run-pv-license-update", log_prints=True)
def update_pv_license_metrics():
    logger = get_run_logger()
    logger.info("Starting the main task...")

    pv_license_level_df = get_pv_license_level()
    pv_license_level_expanded_df = get_pv_license_info_expanded()

    pv_license_level_expanded_df = transform_pv_license_level_expanded(pv_license_level_expanded_df)

    # Merge and process authors and consumers
    logger.info("Processing authors and consumers...")
    authors = pv_license_level_df.loc[(pv_license_level_df['LicenseLevel'] == 0) & (pv_license_level_df['Status'] == 0)]
    consumers = pv_license_level_df.loc[
        (pv_license_level_df['LicenseLevel'] == 1) & (pv_license_level_df['Status'] == 0)]
    fp = open(
        "\\\\sandsrv\\09261\\1 Program Rqmts\\Program Mgmt\\LicenseUsage\\Options File\\License data\\wi_options.txt",
        "r")
    s = fp.readline()
    fp.close()

    user_list = pd.DataFrame(s.split(" ")[2:-4])
    user_list.columns = ["UserId"]
    user_list["OptionsFile"] = 1
    authors = authors.merge(user_list, left_on="UserId", right_on="UserId", how="outer")
    authors["Type"] = 'Author'
    authors["Type"] = np.where(authors["OptionsFile"] == 1, "Consumer", "Author")
    authors = authors[["Name", "UserId", "Type", "OptionsFile"]]
    consumers['Type'] = 'Consumer'
    result = authors.merge(consumers, how="outer")
    pv_license_level_df = result

    # Load supervisor data and merge
    logger.info("Loading supervisor data...")
    supervisors = pd.read_excel(open(
        '\\\\sandsrv\\09261\\1 Program Rqmts\\Program Mgmt\\LicenseUsage\\Options File\\License data\\PPE Roster_FT.xlsx',
        'rb'),
        sheet_name='Page1', skiprows=2, skipfooter=1, dtype=object)
    supervisors = supervisors[["Employee Number", "Supervisor Name (Last Suffix, First MI)"]]
    supervisors["UserId Number"] = supervisors.apply(grab_ID_from_number, axis=1)
    pv_license_level_df["UserId Number"] = pv_license_level_df.apply(grab_ID_from_string, axis=1)
    supervisors = supervisors[["UserId Number", "Supervisor Name (Last Suffix, First MI)"]]
    pv_license_level_df = pv_license_level_df.merge(supervisors, how="left", left_on="UserId Number",
                                                    right_on="UserId Number")
    pv_license_level_df = pv_license_level_df[
        ["UserId", "Name", "Type", "Supervisor Name (Last Suffix, First MI)", "OptionsFile"]]
    pv_license_level_df = pv_license_level_df.rename(
        columns={'Supervisor Name (Last Suffix, First MI)': 'SupervisorName'})

    export_license_usage(pv_license_level_expanded_df)
    export_license_level(pv_license_level_df)
