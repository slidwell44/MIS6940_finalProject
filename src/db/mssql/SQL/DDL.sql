-- use ProjectSeminar
-- go

create table dbo.Workorders
(
    Id              uniqueidentifier default NEWID(),
    WorkorderNumber nvarchar(16) not null unique,
    Revision        nvarchar(8)  not null,
    Quantity        float            default 0.00,
    CONSTRAINT PK_WorkOrders_Id PRIMARY KEY (Id)
)
go