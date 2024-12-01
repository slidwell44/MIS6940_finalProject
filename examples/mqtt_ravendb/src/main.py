import time

from src import logger
from utils.hivemq import (
    McpSubBroker, WorkOrderSubBroker, DefectReportSubBroker, FanucMachineStatusSubBroker, ImsTpmStatusSubBroker,
    McpWorkOrderDevSubBroker
)

if __name__ == '__main__':
    logger.debug("Entering main...")

    production_order_broker = WorkOrderSubBroker(client_id="wikafka-workorder-broker")
    production_order_broker.connect()
    production_order_broker.subscribe("wi/_ims/productionorders/+/+/#")
    production_order_broker.loop_start()

    defect_report_broker = DefectReportSubBroker(client_id="wikafka-defect-report-broker")
    defect_report_broker.connect()
    defect_report_broker.subscribe("wi/_oqr/defectreports/#")
    defect_report_broker.loop_start()

    fanuc_machine_status_broker = FanucMachineStatusSubBroker(client_id="wikafka-fanuc-machine-status-broker")
    fanuc_machine_status_broker.connect()
    fanuc_machine_status_broker.subscribe("wi/sites/+/cells/+/work-centers/+/machines/+/#")
    fanuc_machine_status_broker.loop_start()

    ims_tpm_status_broker = ImsTpmStatusSubBroker(client_id="wikafka-ims-tpm-status-broker")
    ims_tpm_status_broker.connect()
    ims_tpm_status_broker.subscribe("wi/_ims/tpms/+/+/status")
    ims_tpm_status_broker.loop_start()

    mcp_workorder_broker = McpWorkOrderDevSubBroker(client_id="wikafka-mcp-workorder-devbroker")
    mcp_workorder_broker.connect()
    mcp_workorder_broker.subscribe("wi/_mcp/workorder/+/#")
    mcp_workorder_broker.loop_start()

    # TODO: wi/sites/800/_facilities/outside-temp/ not in wihiveprodsrv01.williams-int.com or wihivedevsrv.williams-int.com

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug("Exiting...")
    finally:
        McpSubBroker.close_all()
