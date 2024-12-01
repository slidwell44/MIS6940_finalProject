Verify Kafka Connect is Running
```powershell
Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method GET
```

Start Connector
```powershell
Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body (Get-Content -Raw -Path "connectors/sqlserver-connector.json")
```

Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body (Get-Content -Raw -Path "connectors/simple-connector.json")

