USE EngineeringServices;
GO

CREATE TABLE dbo.PlanReleaseReport
(
    PartNumber nvarchar(64) not null,
    ImsDate date not null,
    CreatedBy nvarchar(64) null,
    Description nvarchar(256) null,
    Laboratory nvarchar(8) not null,
    Filepath nvarchar(256) not null,
    Filename nvarchar(256) not null,
    Source nvarchar(16) null
);