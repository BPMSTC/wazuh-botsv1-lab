# Architecture

This document describes the full technical architecture of the
Wazuh BOTSv1 classroom lab.

## 1. Objective and constraints

### Objective

Build a reproducible, local-first training lab where historical BOTSv1
telemetry is replayed into Wazuh so students can observe:

- Agent ingestion
- Event decoding and rule matching
- Alert generation and dashboard visibility

### Key constraints

- Must run on a Windows instructor workstation
- Must satisfy Wazuh Linux runtime requirements
- Must be stable enough for a 45-60 minute class
- Must avoid committing raw BOTSv1 source data

## 2. Runtime model

The lab uses Docker Desktop with a Linux backend (WSL2 on Windows).

Even though authoring happens on Windows paths, the Wazuh services run in Linux
containers, which satisfies the Wazuh indexer and manager runtime expectations.

## 3. Component architecture

### 3.1 Wazuh core stack (single node)

Provided by vendored upstream assets under:

- `deployment/vendor/wazuh-docker/single-node/`

Main services:

- `wazuh.manager`
  - Receives events from agents
  - Decodes events and applies rules
  - Writes alerts to `alerts.json`
- `wazuh.indexer`
  - Stores indexed Wazuh alert data
- `wazuh.dashboard`
  - UI for alert exploration

### 3.2 Lab overlay services/config

Defined in:

- `deployment/docker-compose.yml`
- `deployment/config/wazuh-agent/ossec.conf`
- `wazuh/local_rules.xml`

Overlay behavior:

- Mounts local custom rules into manager
- Adds sidecar replay agent container: `wazuh.replay-agent`
- Mounts replay output directory into sidecar at `/replay`

### 3.3 ETL and replay pipeline

Source and transform tools:

- `etl/download_botsv1.py`
  - Downloads selected BOTSv1 sourcetypes from manifest
- `etl/main.py`
  - Normalizes source records into JSONL for replay
- `replay/replay_runner.py`
  - Replays normalized JSONL into watched files

Replay manifest examples:

- `replay/replay_manifest.example.json`
- `replay/replay_manifest.sysmon.json`

## 4. Data flow

The high-level path is:

1. BOTSv1 source JSON is downloaded to `data/raw/`
2. ETL normalizes source records to lane-oriented JSONL under `etl/output/`
3. Replay copies/appends JSONL into `replay/output/*.jsonl`
4. Sidecar agent tails `/replay/*.jsonl` and ships events to manager
5. Manager decodes JSON and applies custom/local/default rules
6. Alerts are written to manager alert log and forwarded to indexer
7. Dashboard shows resulting alerts

## 5. Why a sidecar replay agent

Using a dedicated replay agent gives strong classroom advantages:

- Clean separation between manager telemetry and replay telemetry
- Consistent agent identity (`wazuh.replay-agent`) for filtering
- Realistic agent-manager transport path (1514/tcp)
- Easier troubleshooting when replay data is not visible

## 6. Configuration ownership map

### Upstream-owned (vendored) files

Treat these as base assets:

- `deployment/vendor/wazuh-docker/single-node/docker-compose.yml`
- `deployment/vendor/wazuh-docker/single-node/config/*`

### Lab-owned files

Edit these to change lab behavior:

- `deployment/docker-compose.yml`
- `deployment/config/wazuh-agent/ossec.conf`
- `wazuh/local_rules.xml`
- `etl/*`
- `replay/*`

## 7. Current detection behavior

The Sysmon lane is currently validated end-to-end.

Local rule used:

- Rule id `100500`
- Description: `BOTSv1 lab Sysmon event observed`
- Match condition: field `lane == sysmon`

## 8. Security and data policy

### Raw data policy

- Raw BOTSv1 payloads are intentionally excluded from git
- See `.gitignore` and `docs/data-sources.md`

### Generated certificates

- Generated cert artifacts under
  `deployment/vendor/wazuh-docker/single-node/config/wazuh_indexer_ssl_certs/`
  are ignored and should not be committed

### Sensitive defaults

- Upstream sample credentials exist in vendored files
- For classroom-only isolated use, defaults are acceptable
- For shared or persistent environments, rotate credentials

## 9. Performance expectations

On the chosen class profile (Option B), expected behavior:

- First image pull can take significant time
- Stack startup is usually 1-3 minutes after images are present
- Sysmon replay of 5,000 records should complete quickly

## 10. Known operational caveats

- If replay output files do not exist when agent starts, initial
  logcollector file-open errors can appear; this is expected and can self-heal
- Docker Desktop + bind mounts on Windows can behave differently than native
  Linux file semantics; prefer deterministic replay steps and validation checks
- If manager custom decoder syntax is invalid, manager may fail startup; local
  rules are safer than custom decoders for the first demo iteration

## 11. Architectural extension points

The design is intentionally modular. You can extend it by:

- Enabling additional lanes in `ossec.conf` and replay manifests
- Adding targeted local rules for specific ATT&CK narratives
- Introducing small live simulation events to complement replayed history
- Adding optional correlation exercises once students complete baseline replay
