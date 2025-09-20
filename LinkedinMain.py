# pip install playwright
# playwright install

import re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from Solver import *

GAME_URL = "https://www.linkedin.com/games/queens/"
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
        if "login" in page.url or "signup" in page.url:
            page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=120_000)
            print("➡️ Log in manually in the opened window. Press Enter here when done...")
            input()

        # Now go to the game
        page.goto(GAME_URL, wait_until="domcontentloaded", timeout=120_000)

        # Cookie banners / modals (best-effort; adjust selectors for your locale)
        for sel in ["button:has-text('Accept')", "button:has-text('Agree')", "[data-testid='cookie-accept-all']"]:
            try:
                page.locator(sel).first.click(timeout=3000)
                break
            except PWTimeout:
                pass


        page.wait_for_selector("#queens-grid", timeout=120_000)

        # Read CSS variables
        rows = page.evaluate("el => getComputedStyle(el).getPropertyValue('--rows')",
                             page.query_selector("#queens-grid")).strip()
        cols = page.evaluate("el => getComputedStyle(el).getPropertyValue('--cols')",
                             page.query_selector("#queens-grid")).strip()
        print(f"Board: {rows} x {cols}")

        cells = page.query_selector_all("#queens-grid .queens-cell-with-border")
        print("Number of cells:", len(cells))

        grid = []
        for r in range(int(rows)):
            row = []
            for c in range(int(cols)):
                cellindex = r * int(cols) + c
                cls = cells[cellindex].get_attribute("class")
                m = re.search(r"cell-color-(\d+)", cls)
                if m:
                    row.append(m.group(1))
            grid.append(row)
        print(grid)


        showsolve(grid)

    except PWTimeout as e:
        page.screenshot(path="nav-timeout.png", full_page=True)
        print("Timed out. Saved screenshot to nav-timeout.png")
        raise
    finally:
        # Keep the context open if you want the session to persist; otherwise close.
        # context.close()
        pass
