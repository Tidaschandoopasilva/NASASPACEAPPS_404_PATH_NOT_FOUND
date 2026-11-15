# Frontend — Jezero Habitat V7

This is the React/TypeScript frontend using Vite, Three.js and OpenLayers. The **built** frontend is in `dist/` and is included with the GitHub-ready release so `start_desktop.bat` can run without Node.js.

From the repository root:

```cmd
scripts\setup.bat
scripts\start_all.bat
```

For frontend-only dependency setup and rebuild:

```cmd
npm --prefix apps/web ci
npm run build
```

The developer UI is at `http://localhost:5173`. The Vite proxy sends `/api` and `/health` to the FastAPI service on port 8000; start the backend too. See [installation details](../../docs/INSTALLATION.md).

The imagery, models, DEM and built map datasets under `public/` and `dist/` are locally cached source/context assets. Simulated campaign outcomes are served by the Python API; they are not live satellite feeds.
