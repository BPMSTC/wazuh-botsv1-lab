# Deployment Notes

This repository uses the official Wazuh Docker single-node assets as the base stack, then layers a lab-specific Compose override on top for replay ingestion and local rules.

## Why This Layout

- Keeps the base Wazuh deployment close to upstream tested assets.
- Avoids maintaining a hand-copied fork of the full single-node stack.
- Makes classroom-specific changes small and reviewable.

## Option B Capacity Guidance

- Keep the replay dataset curated and small.
- Set Docker memory conservatively for the VM.
- Use controlled replay pacing rather than burst writes.

## Bootstrap the Base Stack

1. Copy `.env.example` to `.env`.
2. Run the bootstrap script from the repository root:

   `python deployment/bootstrap_wazuh_assets.py`

3. The script downloads the pinned `wazuh-docker` release archive and extracts the `single-node` assets into `deployment/vendor/wazuh-docker/single-node/`.

## Start the Lab Stack

Run Docker Compose from the repository root using the vendored single-node base file plus this repository's override file:

`docker compose --env-file deployment/.env -f deployment/vendor/wazuh-docker/single-node/docker-compose.yml -f deployment/docker-compose.yml up -d`

## Notes

- The replay agent sidecar tails files written into `replay/output/` and forwards them to the Wazuh manager.
- This repository's override file mounts `wazuh/local_decoder.xml` and `wazuh/local_rules.xml` into the manager container.
- Before first startup on Linux, set `vm.max_map_count=262144`.
