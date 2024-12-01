USE ProjectSeminar;
GO

EXEC sys.sp_cdc_enable_db;
GO

EXEC sys.sp_cdc_enable_table
     @source_schema = 'dbo',
     @source_name = 'WorkOrders',
     @role_name = NULL,
     @supports_net_changes = 1;
GO

SELECT *
FROM cdc.change_tables;

EXEC sys.sp_cdc_disable_table
     @source_schema = 'dbo',
     @source_name = 'WorkOrders',
     @capture_instance = 'dbo_WorkOrders';
GO

IF OBJECT_ID('dbo.CDC_Process_Log', 'U') IS NULL
    BEGIN
        CREATE TABLE dbo.CDC_Process_Log
        (
            Process_Log_ID INT IDENTITY (1,1) PRIMARY KEY,
            Last_LSN       BINARY(10),
            Processed_Date DATETIME DEFAULT GETDATE()
        );
    END
