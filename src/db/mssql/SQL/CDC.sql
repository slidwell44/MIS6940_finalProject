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

