USE [master];
GO

CREATE LOGIN [kafka_connect_user] WITH PASSWORD = 'password';
GO

USE [ProjectSeminar];
GO

CREATE USER [kafka_connect_user] FOR LOGIN [kafka_connect_user];
GO

EXEC sp_addrolemember N'db_owner', N'kafka_connect_user';
GO

SELECT * FROM sys.server_principals WHERE name = 'kafka_connect_user';

USE [ProjectSeminar];
GO
SELECT * FROM sys.database_principals WHERE name = 'kafka_connect_user';

