# Data Sources and Attribution

## Upstream Source

This lab uses data from BOTSv1:

- Repository: https://github.com/splunk/botsv1
- Owner: Splunk

This repository is a separate implementation owned by bpmstc and is not a fork of the upstream source.

## Data Handling Policy

- Do not commit raw BOTSv1 files into git.
- Store raw downloads under data/raw/ (ignored by git).
- Store normalized/replay artifacts under etl/output/ and replay/output/ (ignored by git).
- Commit only code, schemas, manifests, and small synthetic fixtures.

## Initial Sourcetypes in Scope

- XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
- WinEventLog:Security
- WinEventLog:System
- WinEventLog:Application
- iis

The initial lane manifest is stored in `etl/source_manifest.json`.

## Downloader Strategy

The ETL layer should support a download step that fetches selected BOTSv1 files and stages them into data/raw/. The download code should:

- Require explicit user action.
- Verify source URL and checksum if available.
- Log source path, timestamp, and lane mapping used for transformation.

## Current Download Targets

- Sysmon JSON by sourcetype
- Security JSON by sourcetype
- System JSON by sourcetype
- Application JSON by sourcetype
- IIS JSON by sourcetype

These URLs are sourced from the upstream BOTSv1 repository documentation and intentionally kept outside git-managed raw data storage.
