from sqlalchemy import text
from uuid import UUID

from src.db import get_connection, WiDatabases
from src.routes.models.workorder_response import WorkorderResponse


def read_workorder(workorderid: UUID) -> WorkorderResponse:
    conn = get_connection(WiDatabases.LOCALDB)
    with conn.session_scope() as session:
        result = session.execute(
            text(
                """
                SELECT Id, WorkorderNumber, Revision, Quantity 
                FROM dbo.fn_ReadWorkOrder(:workorderid);
                """
            ),
            params={"workorderid": workorderid},
        )

        row = result.mappings().first()

        if not row:
            raise ValueError(f"No workorder found with ID {workorderid}")

        return WorkorderResponse(**row)
