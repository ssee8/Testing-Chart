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

The workflow builds and publishes `ghcr.io/ssee8/testing-chart:latest` when changes are pushed to `main`. It can also be started manually from the Actions tab. It does not connect to a server; any machine with Docker Compose can pull and run the public image.

Make sure the GHCR package `ghcr.io/ssee8/testing-chart` is public. On a server with Docker and the Compose plugin installed, clone this public repository and start the service:

```sh
git clone https://github.com/ssee8/Testing-Chart.git
cd Testing-Chart
docker compose pull
docker compose up -d
```

On later updates, run `git pull` in the repository directory, then repeat the Compose commands. No server SSH secrets are required.
