# Architecture Summary

## Core Stack

- Ubuntu Server (single VM)
- Wazuh single-node deployment (manager + indexer + dashboard)
- Python ETL utility for BOTSv1 transformation
- File-based replay utility to feed Wazuh-monitored paths

## Ingestion Lanes

1. Sysmon lane
2. Windows Event log lane (Security/System/Application)
3. IIS lane

## Design Principles

- Prefer built-in Wazuh decoders/rules first.
- Add local decoder/rule customizations only for BOTSv1 export-format gaps.
- Keep replay deterministic via manifest ordering and pacing controls.
- Keep day-1 lab small enough for Option B resources.
