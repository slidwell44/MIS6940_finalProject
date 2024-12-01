from uuid import UUID

from sqlalchemy import text

from src.db import get_connection, WiDatabases
from src.routes.models import WorkorderRequest


def update_workorder(workorderid: UUID, workorder: WorkorderRequest):
    conn = get_connection(WiDatabases.LOCALDB)
    with conn.session_scope() as session:
        session.execute(
            text(
                """
                EXEC dbo.sp_UpdateWorkOrder
                    @Id = :Id,
                    @WorkorderNumber = :WorkorderNumber,
                    @Revision = :Revision,
                    @Quantity = :Quantity;
                """
            ),
            params={
                "Id": workorderid,
                "WorkorderNumber": workorder.WorkorderNumber,
                "Revision": workorder.Revision,
                "Quantity": workorder.Quantity,
            }
        )
