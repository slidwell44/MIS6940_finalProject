DECLARE @Id uniqueidentifier;
EXEC dbo.sp_CreateWorkOrder '12345', '000', 5.00, @Id OUTPUT;
SELECT @Id;

SELECT * FROM dbo.fn_ReadWorkOrder('C82F7B4A-314C-46F1-891A-CD786B130C12');

EXEC dbo.sp_UpdateWorkOrder @Id = 'C82F7B4A-314C-46F1-891A-CD786B130C12', @Revision = '001';

SELECT * FROM dbo.fn_ReadWorkOrder('C82F7B4A-314C-46F1-891A-CD786B130C12');

EXEC dbo.sp_DeleteWorkOrder 'C82F7B4A-314C-46F1-891A-CD786B130C12';

/* Should get [S0001][50000] Line 15: Workorder does not exist: C82F7B4A-314C-46F1-891A-CD786B130C12 */
EXEC dbo.sp_UpdateWorkOrder @Id = 'C82F7B4A-314C-46F1-891A-CD786B130C12', @Revision = '001';

