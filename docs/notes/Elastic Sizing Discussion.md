# Elastic Sizing Discussion

Created: November 4, 2024 11:32 AM
Projects: WI Data Engineering (https://www.notion.so/WI-Data-Engineering-111bd64ff89680f28e62f570cf4b0e07?pvs=21), MCP (https://www.notion.so/MCP-111bd64ff89680339028e335e5b8371e?pvs=21)
Tasks: elastic (https://www.notion.so/elastic-12fbd64ff896809aaad2d27ee652e21b?pvs=21)

## Elastic Sizing Comparison

| Feature | Enterprise | Premium/Platinum |
| --- | --- | --- |
| Sizing Model | Total RAM | Per node based on 64 GB RAM |
| Node Count | Fractional | Not fractional (cannot divvy up) |
| Frozen Node | Available | NA |
| Cross Cluster Search | Available | A |
| Priority 1 Response Time | 15 minutes | 30 minutes |

## General Notes

- OS should have double the RAM than Elastic for JVM performance
- Everything is included in both licenses
- Deployment options:
    - Self-Managed
    - ECE (Elastic Cloud Enterprise) - has some pre-prepared setup

Will follow up with some documentation