USE ProjectSeminar;
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

DROP PROCEDURE IF EXISTS dbo.Get_CDC_Changes
GO

CREATE PROCEDURE dbo.Get_CDC_Changes
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @from_lsn BINARY(10);
    DECLARE @to_lsn BINARY(10);
    DECLARE @table_name SYSNAME = 'WorkOrders';
    DECLARE @schema_name SYSNAME = 'dbo';

    SET @to_lsn = sys.fn_cdc_get_max_lsn();

    SELECT @from_lsn = Last_LSN
    FROM dbo.CDC_Process_Log
    WHERE Process_Log_ID = (SELECT MAX(Process_Log_ID) FROM dbo.CDC_Process_Log);

    IF @from_lsn IS NULL
        SET @from_lsn = sys.fn_cdc_get_min_lsn('cdc_' + @schema_name + '_' + @table_name);

    DECLARE @cdc_fn NVARCHAR(100) = 'cdc.fn_cdc_get_all_changes_' + @schema_name + '_' + @table_name;

    DECLARE @sql NVARCHAR(MAX) = N'
    SELECT * FROM ' + @cdc_fn + '(@from_lsn, @to_lsn, ''all'')';

    EXEC sp_executesql @sql, N'@from_lsn binary(10), @to_lsn binary(10)', @from_lsn=@from_lsn, @to_lsn=@to_lsn;

    INSERT INTO dbo.CDC_Process_Log (Last_LSN) VALUES (@to_lsn);
END;
