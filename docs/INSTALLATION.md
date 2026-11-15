# Installation, launch and verification — Team 404 V7

This guide covers **two launch modes**. Start in the root folder containing `desktop.py`, `setup_desktop.bat`, `app/` and `apps/web/`. Do not try to launch the source directly from inside the ZIP.

## Option A — Windows desktop (recommended)

### Prerequisites

- Windows 10/11, 64-bit; Python **3.11 or 3.12** (64-bit), with `py` available from Command Prompt.
- Microsoft Edge **WebView2 Runtime** installed. It is often present on current Windows systems. Get it from Microsoft if the native window does not open.
- An internet connection for installing dependencies on first setup (unless you prepare an offline wheelhouse). **Node.js is not required** in desktop mode because `apps/web/dist` is included.

### Setup

1. Download and extract the **entire ZIP** (e.g. into `C:\Projects\Team404`). Avoid opening the `.bat` files from inside the ZIP viewer.
2. In the extracted root, double-click **`setup_desktop.bat`**. It creates `.venv` and installs `requirements-desktop.txt`.
3. Double-click **`start_desktop.bat`**. A native window entitled **404 | Jezero Habitat V7** opens; the local API and bundled frontend start automatically on a loopback port.
4. In the Atlas tab choose a survey circle; press **Run expedition**; switch to Mission 3D for playback.

To run from Command Prompt instead:

```cmd
cd /d C:\Projects\Team404
setup_desktop.bat
start_desktop.bat
```

First-time installation can take several minutes depending on Python wheels/network speed. The project ships terrain assets, models and built frontend; it does **not** bundle Python, pip packages or the WebView2 Runtime.

### Persistent campaign data

The default campaign SQLite database is stored in your user home directory under `MarsHabitat\desktop.sqlite3`; it persists across app restarts. Launching the app does **not** automatically wipe completed expeditions.

To start with a separate database for a demo:

```cmd
set MARS_HABITAT_DB=%USERPROFILE%\MarsHabitat\demo.sqlite3
start_desktop.bat
```

To keep your campaign, back up that SQLite file before reinstalling. To use a truly fresh campaign, choose a **new** `MARS_HABITAT_DB` path. Do not delete your existing database unless you intend to lose the records.

### Optional trusted-LAN crew telemetry

From the habitat Windows PC, set the correct LAN address:

```cmd
start_desktop.bat --listen-lan 192.168.1.10
```

On a trusted device with Python and `crew_link.py`:

```cmd
py -3 crew_link.py 192.168.1.10 --watch
```

Enter the session code shown in the habitat window. This read-only crew feed is plaintext on TCP 4040; use **only on an isolated trusted LAN**. Desktop UI/API remain bound to loopback.

## Option B — Browser and developer mode

### Prerequisites

- Python 3.11 or 3.12, Git (if cloning), Node.js **22.12+** or Node 24, npm.
- Internet for `pip install` / `npm ci`; bundled NASA assets remain local in normal use.

### Windows quick start

Open Command Prompt in the repository root:

```cmd
scripts\setup.bat
scripts\start_all.bat
```

The first command creates `.venv`, installs Python `requirements.txt` and frontend node packages. The second starts the FastAPI backend on **http://127.0.0.1:8000** and Vite frontend on **http://localhost:5173**. Keep that terminal open, then open `http://localhost:5173` in a browser. Press **Ctrl+C** to stop it.

Alternatively, for explicit manual startup:

```cmd
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
npm --prefix apps/web ci
set PYTHON=%CD%\.venv\Scripts\python.exe
npm run dev
```

### Linux or macOS (developer mode)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm --prefix apps/web ci
PYTHON="$PWD/.venv/bin/python" npm run dev
```

Visit `http://localhost:5173`. Native desktop WebView2 launch and Windows batch scripts are Windows-specific; browser/developer mode is the cross-platform route.

### Production frontend build

```cmd
npm run build
```

`npm run build` runs the TypeScript check and Vite production build and writes `apps/web/dist`. The desktop launcher serves the bundled production build; rebuild it after changing `apps/web/src`.

## Testing and basic checks

In a prepared Python environment from the repository root:

```cmd
.venv\Scripts\python.exe -m pytest -q
npm run build
```

On Linux/macOS use `.venv/bin/python -m pytest -q`. The `.venv` directory and `node_modules` are deliberately not committed to Git. Models, source datasets and built desktop assets are packaged.

For backend-only manual testing:

```cmd
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then load `http://127.0.0.1:8000/health`. In browser/developer mode, Vite proxies `/api` and `/health` to that backend.

## Troubleshooting

| Symptom | Check / fix |
| --- | --- |
| `py` is not recognized | Install Python 3.11/3.12 for Windows, enable the launcher or use the full Python executable; reopen Command Prompt. |
| Desktop opens a blank window or WebView2 error | Install/update the Microsoft Edge WebView2 Runtime. Verify `apps/web/dist/index.html` was extracted. |
| Python dependency installation fails | Recheck Python version and internet access. Try `.venv\Scripts\python.exe -m pip install --upgrade pip` then rerun the setup batch file. |
| `npm` is not recognized | Install Node.js 22.12+ or 24, reopen Command Prompt, and use **browser** mode only if you need Node. |
| Browser page opens but API requests fail | Ensure `npm run dev` has not exited, and that port 8000 isn't occupied. Check `http://127.0.0.1:8000/health`. |
| App shows old campaign state | Its local SQLite ledger persists by design. Choose a new `MARS_HABITAT_DB` path for a fresh isolated demonstration. |
| NASA archive refresh fails | This optional lookup needs internet. The bundled historical samples and terrain remain available. |
| `gh` is missing when publishing | The publishing helper offers Windows Package Manager installation; or install [GitHub CLI](https://cli.github.com/) manually. |

## Publishing to GitHub

The ZIP includes `CREATE_AND_PUBLISH_GITHUB.cmd` and `.ps1`. After installing Git for Windows, run the `.cmd` launcher, sign in to GitHub when prompted, and it can create the public repository **`Tidaschandoopasilva/NASASPACEAPPS_404_PATH_NOT_FOUND`** and push the entire project. See [Publishing guide](../GITHUB_PUBLISHING.md). **This is a local script; downloading the ZIP alone does not upload or publish anything.**

## Data and simulation status

NASA/USGS terrain and imagery are cached local observations. EVA scenarios, hazards, temperatures used for stress tests, vehicle motion and consumptions are simulations. Optional historical MEDA archive retrieval is not a live operational forecast. This software is not validated for actual missions or crew safety.
