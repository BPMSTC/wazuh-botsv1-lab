# Class Demo Runbook

## Duration Target

45-60 minutes total.

## Environment Profile

Option B:

- 4 vCPU
- 8 GB RAM
- 80 GB disk

## Demo Flow

1. Bootstrap official Wazuh single-node assets.
2. Start Wazuh single-node services plus the replay agent sidecar.
3. Confirm dashboard, manager, and replay agent health.
4. Download the curated BOTSv1 lanes.
5. Normalize and optionally trim the dataset for Option B.
6. Replay normalized logs with controlled pacing.
7. Walk through alerts for Sysmon, Windows Event logs, and IIS.
8. Run one lightweight live simulation step.
9. Compare baseline replay alerts with fresh events.

## Timing Guide

- Stack startup and health check: 10-15 min
- ETL + replay: 10-15 min
- Detection walkthrough: 15-20 min
- Live simulation + recap: 10 min

## Pre-class Checklist

- VM reachable and has internet access.
- Docker and Docker Compose installed.
- `vm.max_map_count` set to `262144` on Linux host.
- Disk free space above 20 GB.
- Golden subset already selected for fast replay.

## Command Sequence

1. `python deployment/bootstrap_wazuh_assets.py`
2. `copy deployment\.env.example deployment\.env`
3. `docker compose --env-file deployment/.env -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml up -d`
4. `python etl/download_botsv1.py --lane sysmon --lane winevent_application --lane winevent_security --lane winevent_system --lane iis --decompress`
5. `python etl/main.py --lane sysmon --input data/raw/sysmon/botsv1.XmlWinEventLog-Microsoft-Windows-Sysmon-Operational.json --output etl/output/sysmon.jsonl --limit 5000`
6. `python etl/main.py --lane winevent --input data/raw/winevent_security/botsv1.WinEventLog-Security.json --output etl/output/winevent-security.jsonl --limit 3000`
7. `python etl/main.py --lane winevent --input data/raw/winevent_system/botsv1.WinEventLog-System.json --output etl/output/winevent-system.jsonl --limit 2000`
8. `python etl/main.py --lane winevent --input data/raw/winevent_application/botsv1.WinEventLog-Application.json --output etl/output/winevent-application.jsonl --limit 1000`
9. `python etl/main.py --lane iis --input data/raw/iis/botsv1.iis.json --output etl/output/iis.jsonl --limit 4000`
10. `python replay/replay_runner.py --manifest replay/replay_manifest.example.json --base-dir .`

## Post-class Reset

- Stop replay process.
- Archive run logs.
- Clear replay output/state for next session.
