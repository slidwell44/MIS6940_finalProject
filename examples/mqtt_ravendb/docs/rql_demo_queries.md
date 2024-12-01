# 1) Workorder Aggregation

All DRs for a Workorder

```text
FROM "kafka-defect-reports" 
WHERE kafka_payload."order_number" == "000001255437"
```

All DRs for a Work Center

```text
FROM "kafka-defect-reports" 
WHERE kafka_payload.mqtt_payload."discoveryCell" == "H64 - Electrical Assembly"
```

A single characteristics over time and work orders ???

Show all evidence recorded for requirement GUID ???

# 2) Machine Data Example