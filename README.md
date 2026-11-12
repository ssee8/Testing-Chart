# Testing Chart Portal

A lightweight, responsive placeholder portal for the testing chart. The chart area is ready to be updated once the chart and its data are available.

## Run with Docker Compose

From this directory, build and start the portal:

```sh
docker compose up --build -d
```

Open [http://localhost:8080](http://localhost:8080). To stop it:

```sh
docker compose down
```

The portal is a static site served by Nginx; no application dependencies or environment variables are required.
