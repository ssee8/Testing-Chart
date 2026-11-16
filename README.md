# Testing Chart Portal

A lightweight, responsive placeholder portal for the testing chart. The chart area is ready to be updated once the chart and its data are available.

## Run with Docker Compose

From this directory, pull the latest published image and start the portal:

```sh
docker compose pull
docker compose up -d
```

Open [http://localhost:8080](http://localhost:8080). To stop it:

```sh
docker compose down
```

The portal is a static site served by Nginx; no application dependencies or environment variables are required.

## Deploy with GitHub Actions

The workflow builds and publishes `ghcr.io/ssee8/testing-chart` when changes are pushed to `main`, then deploys it to the server. It can also be started manually from the Actions tab.

Configure these repository settings:

- **Variables:** `SERVER_HOST`, `SERVER_USER`, and `SERVER_DEPLOY_PATH` (an absolute server directory without spaces). Optionally set `SERVER_SSH_PORT` (defaults to `22`).
- **Secrets:** `SERVER_SSH_KEY` (the private key for SSH access) and `SERVER_KNOWN_HOSTS` (the server's pinned known-hosts entry).
- If the GHCR package is private, also set `GHCR_USERNAME` and `GHCR_PULL_TOKEN`. The token needs `read:packages` access. For a public package, these two secrets are not needed.

The server must have Docker with the Compose plugin installed, and the SSH user must be able to run Docker. Once deployed, the workflow copies `docker-compose.yml` into `SERVER_DEPLOY_PATH` and runs:

```sh
docker compose pull
docker compose up -d
```
