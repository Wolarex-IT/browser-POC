# Quick browser POC (Proof of Concept)

The goal of the project is to quickly write a POC in the form of  a minimal FastAPI service that will accept a
website URL and return its rendered HTML using [CloakBrowser](https://github.com/CloakHQ/CloakBrowser).

## Usage

The app drives the host Docker daemon (via the mounted `/var/run/docker.sock`) to
spawn CloakBrowser, so **Docker must be installed and running** on your machine.

1. Create your `.env` from the example and set `DOCKER_GID` so the non-root
container user can access the Docker socket.
```bash
cp .env.example .env
```
- Linux (native Docker Engine): `getent group docker | cut -d: -f3` and put that value in `DOCKER_GID` (often `999`).
- Docker Desktop (macOS/Windows): the mounted socket is owned by root, so set `DOCKER_GID=0`.

2. Build & Run FastAPI application and CloakBrowser using Docker Compose.
```bash
docker compose up -d
```

3. Test on `http://127.0.0.1:8000/docs` or via curl.

```bash
curl -X POST "http://127.0.0.1:8000/" \
     -H "Content-Type: application/json" \
     -d '"https://example.com"'
```

### Available endpoints

- `POST /` - Parse a URL (passed as a raw JSON string in the request body) and return its rendered HTML
(as a plain text string).

## Progress

Milestones, the achievement of which will help us better understand how to work with a browser:

- [x] Build a FastAPI app to use the CloakBrowser locally
- [x] Create a separate container with CloakBrowser and use it via the Playwright API over CDP
- [x] Create a container with CloakBrowser dynamically using the Docker SDK
([DooD](https://www.google.com/search?q=Docker+outside+of+Docker))
