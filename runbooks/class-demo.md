# Class Demo Runbook

## Duration Target

45-60 minutes total.

## Environment Profile

Option B:

- 4 vCPU
- 8 GB RAM
- 80 GB disk

## Demo Flow

1. Start Wazuh single-node services.
2. Confirm dashboard and manager health.
3. Run ETL for a curated BOTSv1 subset.
4. Replay normalized logs with controlled pacing.
5. Walk through alerts for Sysmon, Windows Event logs, and IIS.
6. Run one lightweight live simulation step.
7. Compare baseline replay alerts with fresh events.

## Timing Guide

- Stack startup and health check: 10-15 min
- ETL + replay: 10-15 min
- Detection walkthrough: 15-20 min
- Live simulation + recap: 10 min

## Pre-class Checklist

- VM reachable and has internet access.
- Docker and Docker Compose installed.
- Disk free space above 20 GB.
- Golden subset already selected for fast replay.

## Post-class Reset

- Stop replay process.
- Archive run logs.
- Clear replay output/state for next session.
