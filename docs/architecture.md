# Architecture Summary

## Core Stack

- Ubuntu Server (single VM)
- Official Wazuh single-node deployment (manager + indexer + dashboard) vendored by bootstrap script
- Lab-specific Compose override for local rules and replay agent sidecar
- Python ETL utility for BOTSv1 transformation
- File-based replay utility to feed Wazuh-monitored paths

## Ingestion Lanes

1. Sysmon lane
2. Windows Event log lane (Security/System/Application)
3. IIS lane

## Design Principles

- Prefer built-in Wazuh decoders/rules first.
- Add local decoder/rule customizations only for BOTSv1 export-format gaps.
- Keep upstream Wazuh deployment assets pinned and vendored instead of reimplementing the full stack.
- Keep replay deterministic via manifest ordering and pacing controls.
- Keep day-1 lab small enough for Option B resources.
