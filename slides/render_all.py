"""Render every slide HTML in this folder to a 1920x1080 PNG (needs Playwright + Chromium)."""
import glob, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1.5)
    for f in sorted(glob.glob(os.path.join(HERE, "*.html"))):
        pg.goto("file://" + f); pg.wait_for_timeout(300)
        pg.screenshot(path=f[:-5] + ".png"); print("rendered", os.path.basename(f)[:-5] + ".png")
    b.close()
