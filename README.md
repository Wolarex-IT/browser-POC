# Quick browser POC (Proof of Concept)

The goal of the project is to quickly write a POC in the form of  a minimal FastAPI service that will accept a
website URL and return its rendered HTML using [CloakBrowser](https://github.com/CloakHQ/CloakBrowser).

## Usage

1. Build & Run FastAPI application and CloakBrowser using Docker Compose.
```bash
docker compose up -d
```

2. Test on `http://127.0.0.1:8000/docs` or via curl.

```bash
curl -X POST "http://127.0.0.1:8000/" \
     -H "Content-Type: application/json" \
     -d '"https://example.com"'
```

### Available endpoints

- `POST /` - Parse a URL (passed as a raw JSON string in the request body) and return its rendered HTML
(as a plain text string).
