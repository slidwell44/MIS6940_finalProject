from sqlalchemy import text

from src.db import get_connection, WiDatabases
from src.routes.models import WorkorderRequest, WorkorderResponse


def create_workorder(workorder: WorkorderRequest) -> WorkorderResponse:
    conn = get_connection(WiDatabases.LOCALDB)
    with conn.session_scope() as session:
        result = session.execute(
            text(
                """
                DECLARE @Result UNIQUEIDENTIFIER;
                
                EXEC dbo.sp_CreateWorkOrder
                    @WorkorderNumber = :WorkorderNumber,
                    @Revision = :Revision,
                    @Quantity = :Quantity,
                    @Id = @Result OUTPUT;
                    
                SELECT @Result;
                """
            ),
            params={
                "WorkorderNumber": workorder.WorkorderNumber,
                "Revision": workorder.Revision,
                "Quantity": workorder.Quantity,
            }
        )

        return WorkorderResponse(
            Id=result.scalar(),
            WorkorderNumber=workorder.WorkorderNumber,
            Revision=workorder.Revision,
            Quantity=workorder.Quantity,
        )
