USE ProjectSeminar;
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

DROP FUNCTION IF EXISTS dbo.fn_ReadWorkOrder
GO

CREATE FUNCTION dbo.fn_ReadWorkOrder(@Id UNIQUEIDENTIFIER)
    RETURNS TABLE
        AS
        RETURN(SELECT Id,
                      WorkorderNumber,
                      Revision,
                      Quantity
               FROM dbo.Workorders
               WHERE Id = @Id);
GO
