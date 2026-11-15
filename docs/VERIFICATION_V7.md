# V7 package verification

Verified on 2026-11-15 in the packaging environment.

- Python source compilation (`python -m compileall -q app desktop.py crew_link.py`): passed.
- Python test suite (`python -m pytest -q`): **43 passed**.
- Three historical SVNet test assertions were adjusted to read the V2 dataset manifest's record/test counts (2,300 scenarios, 6,900 action rows, 300 held-out cases), rather than expecting the old 700/2,100/100 figures. Their behavioral checks remain intact.
- README/image link check: passed. The seven current screenshots are present under `docs/screenshots/`.
- ZIP CRC validation: passed.
- Bundled `apps/web/dist/index.html` and static assets are included. No new frontend production build was needed because only docs, screenshots and test expectations were updated.

**Scope:** These checks do not establish Windows WebView2 launch validation, route performance guarantees, NASA weather accuracy or real-mission safety. See historical `docs/ACCEPTANCE.md` for prior-stage verification.
