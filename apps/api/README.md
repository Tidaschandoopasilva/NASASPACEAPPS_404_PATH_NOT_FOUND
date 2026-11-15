# API — Team 404 V7

The FastAPI application lives in the root [`app/`](../../app) package rather than being duplicated here. From the project root, after installing `requirements.txt`, run:

```cmd
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health check: `http://127.0.0.1:8000/health`.

The Windows desktop launcher starts the API internally on a loopback port and serves the bundled `apps/web/dist` files from the same process. Browser/developer mode uses Vite on port 5173. See [installation guide](../../docs/INSTALLATION.md).
