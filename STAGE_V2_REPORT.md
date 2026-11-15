# V2 delivery report

## Completed

Resolved real DEM acquisition with USGS S3 mirror; downloaded 8,015,040 bytes and produced a 640,983-byte native crop. Reprojected/resampled UI grid using the source standard parallel; real terrain is textured with NASA imagery. Added two real Mastcam-Z context photos.

Generated 700 spatially separated scenarios and 2,100 paired action records. Actually trained 404-SVNet, fitted independent calibration, and evaluated 100 held-out scenarios against seven policy variants. Added live and held-out model console, calibrated outcome cards, feature inspection, domain/return gates, outcome reveal, charts and model-to-route application.

## Verification

Exact executed commands and outputs: docs/evidence/svnet-data.txt, svnet-training.txt, svnet-evaluation.txt, pytest-v2.txt and build-v2.txt. Actual checksums and source metadata in data. Data alignment figure visually inspected. All test/build claims correspond to real logs.

## Remaining limits

Browser preview failed (Node uv_interface_addresses), so UI runtime/Windows launch not verified. PyBullet installation failed in three distinct attempts; no results claimed. Science stop membership is proposed/unverified. SVNet does not exceed the strongest constrained risk-A* baseline in this held-out test. All labels remain simulated.

## Start from Windows CMD

```cmd
scripts\setup.bat
scripts\start_all.bat
```

Open http://localhost:5173. No retraining needed. Optional reproduction: scripts\train_svnet.bat.

Final V2 verification: 36 Python tests passed; TypeScript/Vite production build exited 0. See docs/evidence/pytest-v2.txt and build-v2.txt.
