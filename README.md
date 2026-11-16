# ELS Erode Server

This app serves the inspection chart and stores submitted JSON and PDF reports.

## Run locally with Python

Run `start.bat` on Windows or `sh start.sh` on Linux/macOS. The app listens on port `8080`; open [http://localhost:8080](http://localhost:8080).

## Deploy with GitHub Actions

The image-publish workflow builds and publishes the app to GHCR on pushes to `main`. A second workflow then connects to the server over SSH, updates the repository, pulls the image, and restarts the Compose service.

Configure these **repository variables**:

- `SERVER_HOST`: public SSH hostname or IP (the GitHub-hosted runner cannot reach private addresses such as `10.x.x.x`).
- `SERVER_USER`: SSH user that can run Docker Compose.
- `SERVER_DEPLOY_PATH`: absolute path to the server's clone of this repository, without single quotes. Clone the repository there once before the first deployment.
- `SERVER_SSH_PORT`: optional; defaults to `22`.

For the first deployment, clone the public repository into that path, for example:

```sh
git clone https://github.com/ssee8/Testing-Chart.git /opt/Testing-Chart
```

Set `SERVER_DEPLOY_PATH` to `/opt/Testing-Chart` in this example.

Add these **repository secrets**:

- `SERVER_SSH_KEY`: private SSH key whose public key is authorized for `SERVER_USER` on the server.
- `SERVER_KNOWN_HOSTS`: pinned SSH host-key entry for the server and port.

Use a dedicated deployment key for `SERVER_SSH_KEY`. Generate the known-hosts entry with `ssh-keyscan -H -p <port> <public-host>` and verify its fingerprint against a trusted source before saving it.

The server must be reachable over SSH from GitHub Actions, and the SSH user must be able to run `git pull` and `docker compose`. You can also start the deploy workflow manually from the Actions tab. The app is available at `http://<server-address>:8088`; host port `8088` maps to container port `8080`, leaving OpenMediaVault's port `80` unchanged.

Submitted files persist in the Compose `submissions` volume. Videos in `public/videos/` are tracked in Git and become available on the server after `git pull`. Compose mounts that directory read-only into the container; videos are excluded from the image itself.