-- USE ProjectSeminar;
-- GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

DROP PROCEDURE IF EXISTS dbo.sp_DeleteWorkOrder
GO

CREATE PROCEDURE dbo.sp_DeleteWorkOrder @Id UNIQUEIDENTIFIER
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

        DELETE FROM dbo.Workorders WHERE Id = @Id;

        IF XACT_STATE() = 1 COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
