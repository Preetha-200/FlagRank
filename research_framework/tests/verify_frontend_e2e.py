import os
import sys
import time
import subprocess
import urllib.request
import json
from playwright.sync_api import sync_playwright

ROOT_DIR = r"E:\GitHub\RankingManipulationDetector"
RF_DIR = os.path.join(ROOT_DIR, "research_framework")
RAW_CSV = os.path.join(RF_DIR, "data", "raw", "amazon_search_dataset.csv")

def wait_for_url(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def run_tc10_verification():
    backend_proc = None
    frontend_proc = None
    try:
        print("[TC10] Starting backend (FastAPI on port 8000)...")
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.server:app", "--port", "8000", "--host", "127.0.0.1"],
            cwd=ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("[TC10] Starting frontend (Vite dev server on port 5173)...")
        # On Windows, use shell=True or npx.cmd
        frontend_proc = subprocess.Popen(
            ["cmd.exe", "/c", "npm run dev -- --port 5173 --host 127.0.0.1"],
            cwd=ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("[TC10] Waiting for backend API to be healthy...")
        if not wait_for_url("http://127.0.0.1:8000/api/health", timeout=30):
            raise RuntimeError("Backend failed to start or did not become healthy within 30s")
        print("[TC10] Backend is healthy.")

        print("[TC10] Waiting for frontend Vite server to be ready...")
        if not wait_for_url("http://127.0.0.1:5173", timeout=30):
            raise RuntimeError("Frontend failed to start or did not become ready within 30s")
        print("[TC10] Frontend is ready.")

        with sync_playwright() as p:
            print("[TC10] Launching Chromium browser...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            # 1. Initial State Verification
            print("[TC10] Navigating to http://127.0.0.1:5173/dashboard ...")
            page.goto("http://127.0.0.1:5173/dashboard", wait_until="networkidle")

            # Check heading
            heading = page.locator("h1").inner_text()
            print(f"[TC10] Dashboard Heading: '{heading}'")
            assert "Research Dashboard" in heading, f"Expected 'Research Dashboard', got '{heading}'"

            # Check placeholders
            page_text = page.content()
            assert "--" in page_text, "Expected '--' placeholders in initial state"
            print("[TC10] Initial state confirmed: '--' placeholders are present.")

            # Ensure candidate table is NOT visible initially
            table_count = page.locator("table").count()
            print(f"[TC10] Initial candidate table count: {table_count} (expected 0)")
            assert table_count == 0, f"Expected 0 tables before analysis, found {table_count}"

            # 2. Upload CSV and Run Analysis
            print(f"[TC10] Uploading dataset: {RAW_CSV}")
            file_input = page.locator("input[type='file']")
            file_input.set_input_files(RAW_CSV)

            run_btn = page.locator("button:has-text('Run Analysis')")
            assert run_btn.is_enabled(), "Run Analysis button should be enabled after file selection"
            print("[TC10] Clicking 'Run Analysis'...")
            run_btn.click()

            # Wait for analysis complete (wait up to 90 seconds for 5-fold RF training & scoring)
            print("[TC10] Waiting for analysis streaming and completion...")
            page.wait_for_selector("text=1,094", timeout=90000)
            print("[TC10] Dataset analysis finished. Results populated!")

            # 3. Verify Metrics
            # Wait a moment for chart animations
            page.wait_for_timeout(2000)

            # Check metric card values
            products_text = page.locator("p:has-text('Products')").locator("xpath=preceding-sibling::p").inner_text()
            queries_text = page.locator("p:has-text('Queries')").locator("xpath=preceding-sibling::p").inner_text()
            range_text = page.locator("p:has-text('Search position boundaries')").locator("xpath=preceding-sibling::p").inner_text()
            mae_text = page.locator("p:has-text('MAE')").locator("xpath=preceding-sibling::p").inner_text()
            rmse_text = page.locator("p:has-text('RMSE')").locator("xpath=preceding-sibling::p").inner_text()
            r2_text = page.locator("p:has-text('R² (Variance Explained)')").locator("xpath=preceding-sibling::p").inner_text()

            print(f"[TC10] Metrics: Products={products_text}, Queries={queries_text}, Range={range_text}, MAE={mae_text}, RMSE={rmse_text}, R²={r2_text}")
            assert products_text == "1,094", f"Expected '1,094', got '{products_text}'"
            assert queries_text == "44", f"Expected '44', got '{queries_text}'"
            assert range_text == "1 to 59", f"Expected '1 to 59', got '{range_text}'"
            assert "9.12" in mae_text, f"Expected MAE ~9.12, got '{mae_text}'"
            assert "12.08" in rmse_text, f"Expected RMSE ~12.08, got '{rmse_text}'"
            assert "0.21" in r2_text, f"Expected R² ~0.21, got '{r2_text}'"

            # Check candidate table
            table = page.locator("table")
            assert table.count() == 1, "Candidate table should be rendered after analysis"
            rows = table.locator("tbody tr")
            row_count = rows.count()
            print(f"[TC10] Candidate table rendered {row_count} rows on page 1")
            assert row_count > 0, "Candidate table should have rows"

            first_asin = rows.nth(0).locator("td").nth(0).inner_text().strip()
            first_query = rows.nth(0).locator("td").nth(1).inner_text().strip()
            first_obs_rank = rows.nth(0).locator("td").nth(2).inner_text().strip()
            first_exp_rank = rows.nth(0).locator("td").nth(3).inner_text().strip()
            first_score = rows.nth(0).locator("td").nth(7).inner_text().strip()
            print(f"[TC10] Top Candidate: ASIN={first_asin}, Query={first_query}, ObsRank={first_obs_rank}, ExpRank={first_exp_rank}, Score={first_score}")

            # 4. Test Navigation to Product Analysis
            analyze_btn = rows.nth(0).locator("button:has-text('Analyze')")
            print(f"[TC10] Clicking 'Analyze' button for ASIN {first_asin}...")
            analyze_btn.click()

            page.wait_for_url(f"**/product/{first_asin}*", timeout=15000)
            page.wait_for_timeout(2000)

            product_title_elem = page.locator("h1, h2, h3").filter(has_text=first_asin).or_(page.locator(".font-bold")).first
            page_text_prod = page.content()
            
            # Check for title and no "Unknown" fallback
            print(f"[TC10] Product URL: {page.url}")
            assert first_asin in page.url, f"Expected ASIN {first_asin} in URL"
            assert "Unknown" not in page.locator("h1").inner_text() if page.locator("h1").count() > 0 else True

            # Save screenshot for audit evidence
            screenshot_path = os.path.join(RF_DIR, "reports", "tc10_frontend_verified.png")
            page.screenshot(path=screenshot_path)
            print(f"[TC10] Saved audit screenshot to {screenshot_path}")

            browser.close()
            print("[TC10] All frontend verification steps PASSED successfully!")
            return True

    finally:
        print("[TC10] Cleaning up processes...")
        if frontend_proc:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(frontend_proc.pid)], capture_output=True)
            except Exception as e:
                print(f"Error terminating frontend: {e}")
        if backend_proc:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_proc.pid)], capture_output=True)
            except Exception as e:
                print(f"Error terminating backend: {e}")

if __name__ == "__main__":
    success = run_tc10_verification()
    sys.exit(0 if success else 1)
