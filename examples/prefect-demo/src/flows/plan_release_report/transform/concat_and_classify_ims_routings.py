import pandas as pd
from prefect import task


@task()
def concat_and_classify_ims_routings(latest_created_df: pd.DataFrame, latest_changed_df: pd.DataFrame) -> pd.DataFrame:
    ims_latest_routing_df = (
        (pd.concat([latest_created_df, latest_changed_df]))
        .drop_duplicates(subset=["part_no"], keep='last')
        .sort_values(by=["part_no"])
    )

    ims_latest_routing_df["Source"] = "CIMx"
    ims_latest_routing_df.loc[ims_latest_routing_df["filename"].str.upper().str.contains("HTML"), "Source"] = "PV"

    ims_latest_routing_df["ims_date"] = ims_latest_routing_df["ims_date"].apply(
        lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))

    return ims_latest_routing_df
