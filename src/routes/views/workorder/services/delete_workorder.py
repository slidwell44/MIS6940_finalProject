from sqlalchemy import text
from uuid import UUID

from src.db import get_connection, WiDatabases


def delete_workorder(workorderid: UUID):
    conn = get_connection(WiDatabases.LOCALDB)
    with conn.session_scope() as session:
        session.execute(
            text(
                """
                EXEC dbo.sp_DeleteWorkOrder @Id = :workorderid;
                """
            ),
            params={"workorderid": workorderid},
        )
