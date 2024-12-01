USE ProjectSeminar;
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

DROP PROCEDURE IF EXISTS dbo.sp_CreateWorkOrder
GO

CREATE PROCEDURE dbo.sp_CreateWorkOrder @WorkorderNumber NVARCHAR(16),
                                        @Revision NVARCHAR(8),
                                        @Quantity FLOAT = NULL,
                                        @Id UNIQUEIDENTIFIER OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Sql NVARCHAR(MAX);
    DECLARE @ParamDefinition NVARCHAR(MAX);

    DROP TABLE IF EXISTS #Output;
    CREATE TABLE #Output
    (
        Id uniqueidentifier
    )

    SET @ParamDefinition = N'@WorkorderNumber NVARCHAR(16), ' +
                           N'@Revision NVARCHAR(8), ' +
                           N'@Quantity FLOAT';

    SET @Sql = N'INSERT INTO dbo.Workorders (WorkorderNumber, Revision'
        + IIF(@Quantity IS NOT NULL, N', Quantity', N'')
        + N') OUTPUT INSERTED.Id INTO #Output '
        + N'VALUES (@WorkorderNumber, @Revision'
        + IIF(@Quantity IS NOT NULL, N', @Quantity', N'')
        + N')';

    BEGIN TRY
        BEGIN TRANSACTION;

        EXEC sp_executesql @Sql,
             @ParamDefinition,
             @WorkorderNumber = @WorkorderNumber,
             @Revision = @Revision,
             @Quantity = @Quantity;

        SELECT @Id = Id FROM #Output;

        IF XACT_STATE() = 1 COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO
