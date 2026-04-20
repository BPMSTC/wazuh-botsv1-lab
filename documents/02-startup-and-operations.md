# Startup And Operations Guide

This guide covers prerequisites, first-time startup, normal operations,
health checks, and troubleshooting.

## 1. Prerequisites

## Host requirements

- Windows 10/11 with Docker Desktop installed
- WSL2 backend enabled in Docker Desktop
- Recommended resources for class profile:
  - 4 vCPU
  - 8 GB RAM
  - 80 GB disk

## Tooling

- Docker Desktop (with Compose v2)
- Python 3.11+ (repo currently uses `c:/python313/python.exe`)
- Git

## Verify Docker is ready

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh"
docker version
docker context ls
docker ps
```

Expected:

- Docker server shows Linux backend
- `docker ps` succeeds without daemon errors

## 2. First-time bootstrap

## 2.1 Vendor upstream Wazuh single-node assets

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh"
c:/python313/python.exe deployment/bootstrap_wazuh_assets.py
```

This populates:

- `deployment/vendor/wazuh-docker/single-node/`

## 2.2 Generate certs for indexer/dashboard/manager

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh\deployment\vendor\wazuh-docker\single-node"
docker compose -f generate-indexer-certs.yml run --rm generator
```

## 2.3 Prepare env file

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh"
Copy-Item deployment/.env.example deployment/.env
```

Adjust values as needed for classroom credentials.

## 3. Start the stack

From repo root:

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh"
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml up -d
```

## Validate container state

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected containers:

- `single-node-wazuh.manager-1`
- `single-node-wazuh.indexer-1`
- `single-node-wazuh.dashboard-1`
- `wazuh.replay-agent`

## 4. Health verification checks

## 4.1 Manager health

```powershell
docker logs single-node-wazuh.manager-1 --since 3m --tail 200
```

Look for:

- Wazuh components started (`analysisd`, `authd`, `remoted`)
- Filebeat connected to indexer

## 4.2 Replay agent enrollment

```powershell
docker logs wazuh.replay-agent --since 3m --tail 200
```

Look for:

- `Valid key received`
- `Connected to the server ([wazuh.manager]:1514/tcp)`

## 4.3 Dashboard reachability

Open:

- `https://localhost`

Use credentials configured in environment and upstream config.

## 5. Data preparation workflow

## 5.1 Download BOTSv1 lane data (Sysmon first)

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh"
c:/python313/python.exe etl/download_botsv1.py --lane sysmon --decompress
```

## 5.2 Run ETL normalization

```powershell
c:/python313/python.exe etl/main.py --lane sysmon --input data/raw/sysmon.json --output etl/output/sysmon.jsonl
```

## 5.3 Replay prepared records

```powershell
c:/python313/python.exe replay/replay_runner.py --manifest replay/replay_manifest.sysmon.json --base-dir . --reset-targets
```

## 6. Alert validation

## 6.1 Validate custom Sysmon rule

```powershell
docker exec single-node-wazuh.manager-1 sh -lc "grep -n '100500' /var/ossec/logs/alerts/alerts.json | tail -n 20"
```

Expected:

- Alerts with rule id `100500`
- Description `BOTSv1 lab Sysmon event observed`

## 6.2 Validate replay agent visibility

```powershell
docker exec single-node-wazuh.manager-1 sh -lc "grep -n 'wazuh.replay-agent' /var/ossec/logs/alerts/alerts.json | tail -n 20"
```

## 7. Day-to-day operations

## Start

```powershell
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml up -d
```

## Stop (keep data volumes)

```powershell
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml down
```

## Stop and remove volumes (full reset)

```powershell
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml down -v
```

Use full reset only when you intentionally want to wipe Wazuh persisted state.

## 8. Common troubleshooting

## Symptom: manager fails to start

Checks:

- `docker logs single-node-wazuh.manager-1 --tail 300`
- Validate custom rule XML in `wazuh/local_rules.xml`

Typical cause:

- Invalid decoder/rule syntax

## Symptom: replay agent connected but no alerts

Checks:

- `docker logs wazuh.replay-agent --tail 300`
- Confirm replay file exists inside container:

```powershell
docker exec wazuh.replay-agent sh -lc "wc -l /replay/sysmon.jsonl"
```

- Confirm rule 100500 grep command returns matches

## Symptom: Docker Desktop resource pressure

Actions:

- Increase Docker Desktop memory/CPU settings
- Restart Docker Desktop
- Wait for indexer startup to stabilize before replay

## Symptom: path or mount confusion in compose override

Action:

- Always run compose commands from repo root using both `-f` files exactly as
  shown in this guide

## 9. Operational guardrails

- Do not commit generated cert private keys
- Do not commit raw BOTSv1 source payloads
- Keep replay manifests lane-specific during live demos to reduce noise
