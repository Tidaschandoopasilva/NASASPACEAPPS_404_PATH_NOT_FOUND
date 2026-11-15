"""Optional local screenshot capture. Start app first. Requires Playwright + Chromium."""
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://localhost:5173');a=p.parse_args()
    try:from playwright.sync_api import sync_playwright
    except ImportError:raise SystemExit('Install: python -m pip install playwright; then python -m playwright install chromium')
    out=ROOT/'docs/evidence';out.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');page.goto(a.url);page.get_by_text('Return included; 20% time reserve enforced',exact=True).wait_for(timeout=30000)
        for label,file in [('MISSION 3D','mission.png'),('ATLAS','atlas.png')]:
            page.get_by_role('button',name=label).click();page.screenshot(path=str(out/file),full_page=True)
        page.get_by_role('button',name='Deploy simulated scout').click();page.get_by_text('Route recalculated after observation.',exact=False).wait_for();page.get_by_role('button',name='Pause',exact=True).click() if page.get_by_role('button',name='Pause',exact=True).count() else None
        page.screenshot(path=str(out/'scout.png'),full_page=True);page.get_by_role('button',name='REWIND').click();page.screenshot(path=str(out/'rewind.png'),full_page=True);browser.close()
if __name__=='__main__':main()
