USE ProjectSeminar;
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

DROP PROCEDURE IF EXISTS dbo.sp_UpdateWorkOrder
GO

CREATE PROCEDURE dbo.sp_UpdateWorkOrder @Id UNIQUEIDENTIFIER,
                                        @WorkorderNumber NVARCHAR(16) = NULL,
                                        @Revision NVARCHAR(8) = NULL,
                                        @Quantity FLOAT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ErrorMessage NVARCHAR(MAX);

    BEGIN TRY
        IF NOT EXISTS(SELECT 1 FROM dbo.Workorders WHERE Id = @Id)
            BEGIN
                SET @ErrorMessage = N'Workorder does not exist: ' + CAST(@Id AS NVARCHAR(36));
                RAISERROR (@ErrorMessage, 16, 1);
            END;

        BEGIN TRANSACTION;

        UPDATE dbo.Workorders
        SET WorkorderNumber = COALESCE(@WorkorderNumber, WorkorderNumber),
            Revision        = COALESCE(@Revision, Revision),
            Quantity        = COALESCE(@Quantity, Quantity)
        WHERE Id = @Id;

        IF XACT_STATE() = 1 COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
