-- sqldf2
CREATE TABLE tc_license.LicenseUsage
(
    UserId         nvarchar(16)   NOT NULL,
    LicenseLevel   nvarchar(64)   NOT NULL,
    LicenseKeys    nvarchar(4000) NOT NULL,
    Month          int            NOT NULL,
    Year           int            NOT NULL,
    NumberOfLogins int            NOT NULL,
    Day            int            NOT NULL,
    LicenseKey     nvarchar(64)
);
GO