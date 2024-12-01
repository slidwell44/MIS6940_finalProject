-- sqldf
CREATE TABLE tc_license.LicenseLevel
(
    UserId nvarchar(16) NOT NULL,
    Name nvarchar(128) NOT NULL,
    Type nvarchar(32) NOT NULL,
    SupervisorName nvarchar(128),
    OptionsFile bit NOT NULL
);
GO