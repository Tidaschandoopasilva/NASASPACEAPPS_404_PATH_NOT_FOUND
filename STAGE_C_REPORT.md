> Historical v1 checkpoint. Superseded by STAGE_V2_REPORT.md and current docs/ACCEPTANCE.md.

# Stage C report

Seeded Gaussian observation, Bayesian corridor update, replanning, local kinematic trace and explanatory VoS implemented. VoS and rover traversal approximations documented.

## Files / evidence

See CHANGELOG, DATA_SOURCES, METHODS, ACCEPTANCE, and docs/evidence. Stage files were implemented in one local workspace; commit checkpoints were assembled after checks, not falsely described as sequentially passing all real-data gates.

Commands actually run: `python -m pytest -q` (exit 0); `npm run build` (exit 0). Final exact output in docs/evidence/pytest.txt and build.txt. Experiments command and raw output in docs/evidence/experiment-run.txt. Acquisition bytes and capabilities in data and model node manifests. No screenshots: managed preview failed before browser QA.

## Known issues / not verified

Real DEM not acquired; exact science-stop mapped units unverified. Browser appearance, controls, FPS and Windows launch were not tested in a Windows/browser runtime. See DECISIONS and ACCEPTANCE for all limitations. Do not claim operational validation.

## Windows CMD launch from project root

```cmd
scripts\setup.bat
scripts\start_all.bat
```

Open http://localhost:5173. Separate API: `python -m uvicorn app.main:app --port 8000` after activating the virtual environment. Next manual steps are in docs/SUBMISSION_PACKET.md.
