# Deployment Notes

This repository uses a single-node Wazuh deployment for classroom demos.

## Option B Capacity Guidance

- Use a reduced replay dataset.
- Keep indexing windows small.
- Avoid high replay rates.

## Local Bring-up

1. Copy .env.example to .env and set strong passwords.
2. Start stack from this directory:

   docker compose --env-file .env -f docker-compose.yml up -d

3. Verify containers are healthy and dashboard is reachable.

## Important

The compose file in this repository is a starting baseline for class use.
If upstream Wazuh docker assets change, update this file and pin tested versions.
