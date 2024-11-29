from prefect import serve
from prefect.client.schemas.schedules import CronSchedule

from src.flows import (
    update_plan_release_report, update_pv_license_metrics, update_tool_gauge_data,
    update_mecn_bop_data, update_eps_data, update_mecn_data
)

if __name__ == "__main__":
    plan_release_deployment = update_plan_release_report.to_deployment(
        name="Plan Release Report Pipeline",
        schedules=[
            CronSchedule(cron="20/30 * * * *",
                         timezone="America/Detroit")
        ],
        tags=["ims", "pv"],
        description="Pulls plan release report for use in Power BI",
    )

    pv_license_deployment = update_pv_license_metrics.to_deployment(
        name="PV License Usage Metrics Pipeline",
        schedules=[
            CronSchedule(cron="25/30 * * * *",
                         timezone="America/Detroit")
        ],
        tags=["pv"],
        description="Pulls PV License Usage Metrics",
    )

    bop_tool_gauge_deployment = update_tool_gauge_data.to_deployment(
        name="BOP Tool Gauge Data Pipeline",
        schedules=[
            CronSchedule(cron="0/30 * * * *",
                         timezone="America/Detroit")
        ],
        tags=["pv"],
    )

    mecn_bop_deployment = update_mecn_bop_data.to_deployment(
        name="MECN BOP Data Pipeline",
        schedules=[
            CronSchedule(cron="5/30 * * * *",
                         timezone="America/Detroit")
        ],
        tags=["pv"],
    )

    eps_deployment = update_eps_data.to_deployment(
        name="EPS Data Pipeline",
        schedules=[
            CronSchedule(cron="10/30 * * * *",
                         timezone="America/Detroit")
        ],
        tags=["pv"],
    )

    mecn_deployment = update_mecn_data.to_deployment(
        name="MECN Data Pipeline",
        schedules=[
            CronSchedule(cron="15/30 * * * *",
                         timezone="America/Detroit")
        ],
        tags=["pv"],
    )

    serve(
        plan_release_deployment,
        pv_license_deployment,
        bop_tool_gauge_deployment,
        mecn_bop_deployment,
        eps_deployment,
        mecn_deployment,
    )
