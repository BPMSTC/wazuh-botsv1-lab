# Class Demo Runbook (45-60 Minutes)

This runbook is designed for an instructor-led SOC telemetry replay class.

## 1. Demo outcomes

By the end of class, students should be able to:

- Explain how replayed telemetry reaches Wazuh
- Start and validate the stack
- Replay Sysmon sample events
- Confirm custom detection alerts are firing

## 2. Suggested timeline

- 0:00-0:10 Intro and architecture walkthrough
- 0:10-0:20 Startup and health checks
- 0:20-0:35 Sysmon download + ETL + replay
- 0:35-0:50 Investigation in dashboard and alert logs
- 0:50-1:00 Wrap-up and extension ideas

## 3. Pre-class checklist (do before students join)

- Docker Desktop is running
- Repo is up to date on `main`
- Stack images already pulled at least once
- Cert generation already completed
- Internet access verified

Optional pre-warm to reduce delays:

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh"
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml up -d
```

## 4. In-class command sequence

Run all commands from repo root unless noted.

### Step A: start stack

```powershell
Set-Location "c:\Users\bpmst\source\repos\wazuh"
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml up -d
```

### Step B: verify containers

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected: manager, indexer, dashboard, replay-agent are Up.

### Step C: verify manager and agent logs

```powershell
docker logs single-node-wazuh.manager-1 --since 3m --tail 150
docker logs wazuh.replay-agent --since 3m --tail 150
```

Highlight lines:

- manager modules started
- replay agent key enrollment and connection

### Step D: download Sysmon lane

```powershell
c:/python313/python.exe etl/download_botsv1.py --lane sysmon --decompress
```

### Step E: normalize Sysmon lane

```powershell
c:/python313/python.exe etl/main.py --lane sysmon --input data/raw/sysmon.json --output etl/output/sysmon.jsonl
```

### Step F: replay Sysmon into monitored path

```powershell
c:/python313/python.exe replay/replay_runner.py --manifest replay/replay_manifest.sysmon.json --base-dir . --reset-targets
```

### Step G: validate detection firing

```powershell
docker exec single-node-wazuh.manager-1 sh -lc "grep -n '100500' /var/ossec/logs/alerts/alerts.json | tail -n 20"
```

Expected:

- Multiple matches for rule id `100500`
- Description `BOTSv1 lab Sysmon event observed`

## 5. Talking points during each phase

## Startup phase

- Why Wazuh runs in Linux containers even on Windows host
- Why we use single-node for classroom reliability

## ETL phase

- Why raw source needs normalization before replay
- What lane metadata (`lane=sysmon`) is used for in detection

## Replay phase

- Role of sidecar agent (`wazuh.replay-agent`)
- Difference between transport success and detection success

## Detection phase

- How local rules complement built-in Wazuh rules
- Where alerts are persisted (`alerts.json`) before dashboard visualization

## 6. Student activities

## Activity 1 (guided)

Ask students to identify these fields in one alert payload:

- `rule.id`
- `agent.name`
- `data.lane`
- `location`

## Activity 2 (semi-guided)

Ask students to compare two Sysmon alerts and explain:

- Same detection logic
- Different network/process context in payload

## Activity 3 (discussion)

Ask how they would create a higher-severity rule for specific Sysmon process
names or destination ports.

## 7. Fallback plans

## If indexer/dashboard are slow

Continue class using manager alert log validation only:

```powershell
docker exec single-node-wazuh.manager-1 sh -lc "tail -n 40 /var/ossec/logs/alerts/alerts.json"
```

## If replay file seems ignored

- Re-run replay with `--reset-targets`
- Verify replay file line count in sidecar container:

```powershell
docker exec wazuh.replay-agent sh -lc "wc -l /replay/sysmon.jsonl"
```

## If manager restart needed

```powershell
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml up -d --force-recreate wazuh.manager wazuh.replay-agent
```

## 8. Post-class teardown

If keeping state for next class:

```powershell
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml down
```

If full cleanup is needed:

```powershell
docker compose -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml down -v
```

## 9. Optional extension for next session

- Enable and test additional lanes: `winevent` and `iis`
- Build one custom medium/high-severity rule with strong field conditions
- Introduce one small live simulation event and compare against replay data
