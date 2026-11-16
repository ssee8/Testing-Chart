# ELS Erode Server

This app serves the inspection chart and stores submitted JSON and PDF reports.

## Run locally with Python

Run `start.bat` on Windows or `sh start.sh` on Linux/macOS. The app listens on port `8080`; open [http://localhost:8080](http://localhost:8080).

## Deploy with Docker Compose

The GitHub Actions workflow publishes the app image to GHCR on each push to `main`. On the server, clone or update this repository, then run:

```sh
git pull
docker compose pull
docker compose up -d
```

Open `http://<server-address>:8088`. The host port `8088` maps to the app's container port `8080`; this avoids OpenMediaVault's port `80`.

Submitted files persist in the Compose `submissions` volume. Videos in `public/videos/` are tracked in Git and become available on the server after `git pull`. Compose mounts that directory read-only into the container; videos are excluded from the image itself.