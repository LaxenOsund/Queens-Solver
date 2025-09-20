# pip install playwright
# playwright install

import re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from Solver import *

GAME_URL = "https://queensgame.vercel.app/level/11"
PROFILE_DIR = "user-data"  # will store cookies/session so you don't log in every time

with sync_playwright() as p:
    # Use a persistent context so your LinkedIn login is remembered
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = context.new_page()

    try:
        # First time only: go to login and sign in manually in the opened browser window
        # (2FA etc.). After that, your session stays in user-data.
        # Now go to the game
        page.goto(GAME_URL, wait_until="domcontentloaded", timeout=120_000)

        # Cookie banners / modals (best-effort; adjust selectors for your locale)
        for sel in ["button:has-text('Accept')", "button:has-text('Agree')", "[data-testid='cookie-accept-all']"]:
            try:
                page.locator(sel).first.click(timeout=3000)
                break
            except PWTimeout:
                pass


        page.wait_for_selector(".board", timeout=120_000)
        def parse_repeat(s):
            if not s:
                return None
            s = s.strip()
            m = re.match(r"repeat\((\d+),", s)
            if m:
                return int(m.group(1)) if m else None
            parts = [p for p in re.split(r"\s+", s) if p and p != '/']
            return len(parts) if parts else None


        # Read CSS variables
        rows = parse_repeat(page.evaluate("el => getComputedStyle(el).getPropertyValue('grid-template-rows')",
                             page.query_selector(".board")).strip())
        cols = parse_repeat(page.evaluate("el => getComputedStyle(el).getPropertyValue('grid-template-columns')",
                             page.query_selector(".board")).strip())
        print(f"Board: {rows} x {cols}")

        


        cells = page.query_selector_all(".board .square")
        print("Number of cells:", len(cells))

        grid = []
        for r in range(int(rows)):
            row = []
            for c in range(int(cols)):
                cellindex = r * int(cols) + c
                rgb = page.evaluate("el => getComputedStyle(el).getPropertyValue('background-color')",
                    cells[cellindex])
                row.append(rgb)
            grid.append(row)


        showsolve(grid)

    except PWTimeout as e:
        page.screenshot(path="nav-timeout.png", full_page=True)
        print("Timed out. Saved screenshot to nav-timeout.png")
        raise
    finally:
        # Keep the context open if you want the session to persist; otherwise close.
        # context.close()
        pass
