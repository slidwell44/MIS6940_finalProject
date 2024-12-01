DECLARE @Id uniqueidentifier;
EXEC dbo.sp_CreateWorkOrder '54321', '000', 5.00, @Id OUTPUT;
SELECT @Id;

SELECT * FROM dbo.fn_ReadWorkOrder('770EE5A7-8174-4D9C-A2AB-424C08CEC1CB');

EXEC dbo.sp_UpdateWorkOrder @Id = '770EE5A7-8174-4D9C-A2AB-424C08CEC1CB', @Revision = '005';

SELECT * FROM dbo.fn_ReadWorkOrder('770EE5A7-8174-4D9C-A2AB-424C08CEC1CB');

EXEC dbo.sp_DeleteWorkOrder '770EE5A7-8174-4D9C-A2AB-424C08CEC1CB';

/* Should get [S0001][50000] Line 15: Workorder does not exist: 770EE5A7-8174-4D9C-A2AB-424C08CEC1CB */
EXEC dbo.sp_UpdateWorkOrder @Id = '770EE5A7-8174-4D9C-A2AB-424C08CEC1CB', @Revision = '001';

EXEC dbo.Get_CDC_Changes

