# V2 implementation decisions

- Real elevation blocker resolved using the public USGS S3 archive mirror discovered through source records. Downloaded only the crop's TIFF strips (8,015,040 bytes), preserving native values and metadata.
- Working UI projection uses the source standard parallel 18.4663°, rather than assuming Earth coordinates or the previous synthetic fixture's equatorial local scale. Longitude conversion and tests updated accordingly.
- Real CTX relief and NASA HiRISE imagery now share a georeferenced ROI in 3D. Grey imagery is tinted only by the material/lighting; it is not presented as a true-color observation.
- Added actual CPU training and calibration, not placeholder model files. Model selection uses validation, calibration a separate region, and held-out policy evaluation the fourth region.
- Added return-constrained baseline comparisons after recognizing that abstention can inflate comparisons against forced-launch policies. Both forced and constraint-matched results remain visible. Constrained risk A* beats the learned model on mean utility in this test.
- The live learned decision uses one uncertain corridor and excludes waypoints from its mask, matching the training task. Legacy UI's three-corridor analytic demo remains separate and labelled.
- Added real NASA context photographs. No claim that they depict the exact proposed stop coordinates.
- PyBullet unavailable after three distinct installation attempts; optional executable stress script supplied and no validation numbers invented.
- Managed browser preview failed again with Node uv_interface_addresses. Browser/Windows QA is not claimed; code build, API tests and scientific figure inspection ran.
