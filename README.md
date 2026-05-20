# Quick browser POC (Proof of Concept)

The goal of the project is to quickly write a POC in the form of  a minimal FastAPI service that will accept a
website URL and return its rendered HTML using [CloakBrowser](https://github.com/CloakHQ/CloakBrowser).

## Usage

1. Install the dependencies (recommended to use a virtual environment).
```bash
pip install -r requirements.txt
```

2. Run the server in development mode.
```bash
fastapi dev main.py
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
