# wazuh-botsv1-lab

Classroom lab for replaying BOTSv1 data into a Wazuh single-node deployment.

## Goals

- Run Wazuh all-in-one on one Ubuntu VM (Option B profile).
- Replay a curated subset of BOTSv1 data for Sysmon, Windows Event logs, and IIS logs.
- Keep setup reproducible and lightweight for 45-60 minute demos.

## Scope

Day 1 includes:

- Sysmon (highest priority)
- Windows Event logs (Security/System/Application)
- IIS logs
- One lightweight live simulation step

Out of scope on Day 1:

- Suricata ingestion and cross-source correlation
- Multi-node Wazuh cluster

## Repository Layout

- deployment/: Wazuh deployment assets and environment templates
- etl/: BOTSv1 normalization pipeline
- replay/: Deterministic replay utilities and manifests
- wazuh/: Local decoder/rule overrides
- runbooks/: Instructor-facing execution guides
- docs/: Data source and architecture docs

## Data Policy

Raw BOTSv1 source data is not committed to this repository.
Use the ETL downloader workflow documented in docs/data-sources.md.

## Quick Start

1. Prepare Ubuntu VM with Docker and Docker Compose.
2. Configure deployment/.env from deployment/.env.example.
3. Start Wazuh stack using deployment/docker-compose.yml.
4. Run ETL to normalize BOTSv1 files into replay-ready outputs.
5. Replay files into Wazuh-monitored paths.

Detailed steps are in runbooks/class-demo.md.
