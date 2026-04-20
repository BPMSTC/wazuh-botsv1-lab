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
- documents/: Extended architecture, startup, and classroom demo documentation

## Data Policy

Raw BOTSv1 source data is not committed to this repository.
Use the ETL downloader workflow documented in docs/data-sources.md.

## Quick Start

1. Prepare Ubuntu VM with Docker and Docker Compose.
2. Run `python deployment/bootstrap_wazuh_assets.py` to vendor the pinned Wazuh single-node assets.
3. Configure deployment/.env from deployment/.env.example.
4. Start the base single-node stack plus this repository's override compose file.
5. Run `python etl/download_botsv1.py --decompress` for the selected lanes.
6. Run ETL to normalize BOTSv1 files into replay-ready outputs.
7. Replay files into the sidecar agent's monitored paths.

Detailed steps are in runbooks/class-demo.md.
Extended documentation is in documents/README.md.
