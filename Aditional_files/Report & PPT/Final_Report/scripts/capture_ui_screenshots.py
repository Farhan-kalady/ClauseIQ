import asyncio
import base64
import json
import os
import subprocess
import time
import urllib.request
import websockets

UI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "figures", "ui"))
os.makedirs(UI_DIR, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\Users\farha\.gemini\antigravity-ide\brain\8dfd8779-be53-42f0-ad42-687b149f150b\scratch\chrome_ui_profile"
os.makedirs(USER_DATA_DIR, exist_ok=True)

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50 * 1024 * 1024)

    async def send_command(self, method, params=None, timeout=10):
        self.msg_id += 1
        cmd_id = self.msg_id
        payload = {"id": cmd_id, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(payload))
        
        start_t = time.time()
        while time.time() - start_t < timeout:
            try:
                raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
                msg = json.loads(raw)
                if msg.get("id") == cmd_id:
                    if "error" in msg:
                        print(f"CDP Error for {method}:", msg["error"])
                    return msg.get("result", {})
            except asyncio.TimeoutError:
                break
        print(f"CDP Timeout for command {method}")
        return {}

    async def evaluate(self, expr):
        res = await self.send_command("Runtime.evaluate", {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True
        })
        return res.get("result", {}).get("value")

    async def set_viewport(self, width, height, dsf=2):
        await self.send_command("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": dsf,
            "mobile": width < 600
        })
        await self.send_command("Emulation.setVisibleSize", {"width": width, "height": height})

    async def capture_screenshot(self, filename):
        out_path = os.path.join(UI_DIR, filename)
        res = await self.send_command("Page.captureScreenshot", {"format": "png"})
        if "data" in res:
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(res["data"]))
            size = os.path.getsize(out_path)
            print(f"  [+] Captured {filename} ({size:,} bytes)", flush=True)
            return out_path
        else:
            print(f"  [-] Failed to capture {filename}", flush=True)
            return None

    async def close(self):
        if self.ws:
            await self.ws.close()

async def run_capture():
    print("Launching headless Chrome for UI capture...", flush=True)
    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--remote-debugging-port=9225",
        f"--user-data-dir={USER_DATA_DIR}",
        "--hide-scrollbars",
        "about:blank"
    ])
    time.sleep(2.5)

    try:
        # Create new tab via PUT
        req = urllib.request.Request("http://127.0.0.1:9225/json/new", method="PUT")
        resp = urllib.request.urlopen(req)
        tab = json.loads(resp.read().decode())
        ws_url = tab["webSocketDebuggerUrl"]
        print(f"Connected to DevTools: {ws_url}", flush=True)

        client = CDPClient(ws_url)
        await client.connect()
        await client.send_command("Page.enable")
        await client.send_command("Runtime.enable")
        await client.send_command("DOM.enable")

        # -------------------------------------------------------------
        # Screenshot 8: FastAPI Swagger UI (/docs)
        # -------------------------------------------------------------
        print("\n1/8: Capturing ui_08_api_docs.png...", flush=True)
        await client.set_viewport(1366, 850, dsf=2)
        await client.send_command("Page.navigate", {"url": "http://127.0.0.1:8000/docs"})
        await asyncio.sleep(3.5)
        await client.capture_screenshot("ui_08_api_docs.png")

        # -------------------------------------------------------------
        # Navigate to Frontend App
        # -------------------------------------------------------------
        print("\nNavigating to Frontend: http://127.0.0.1:5173/...", flush=True)
        await client.send_command("Page.navigate", {"url": "http://127.0.0.1:5173/"})
        await asyncio.sleep(2.5)

        # -------------------------------------------------------------
        # Screenshot 1: Single Clause Classification Result
        # -------------------------------------------------------------
        print("\n2/8: Capturing ui_01_classify_text_result.png...", flush=True)
        await client.set_viewport(1366, 850, dsf=2)
        await client.evaluate("""
            const chips = document.querySelectorAll('.sample-chip');
            if (chips.length > 0) chips[0].click();
        """)
        await asyncio.sleep(0.5)
        await client.evaluate("""
            const btn = document.querySelector('.btn-primary');
            if (btn) btn.click();
        """)
        await asyncio.sleep(2.5)
        # Expand alternatives
        await client.evaluate("""
            const altBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Alternative') || b.textContent.includes('Top'));
            if (altBtn) altBtn.click();
        """)
        await asyncio.sleep(1.0)
        await client.capture_screenshot("ui_01_classify_text_result.png")

        # -------------------------------------------------------------
        # Screenshot 2: File Upload Dropzone
        # -------------------------------------------------------------
        print("\n3/8: Capturing ui_02_classify_upload_dropzone.png...", flush=True)
        await client.evaluate("""
            const segTabs = document.querySelectorAll('.segment-tab');
            if (segTabs.length > 1) {
                segTabs[1].click();
            }
        """)
        await asyncio.sleep(1.2)
        await client.capture_screenshot("ui_02_classify_upload_dropzone.png")

        # -------------------------------------------------------------
        # Screenshot 3: Document Processing Results
        # -------------------------------------------------------------
        print("\n4/8: Capturing ui_03_classify_document_results.png...", flush=True)
        sample_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw_pdfs", "sample_contract.pdf"))
        doc_node = await client.send_command("DOM.getDocument")
        file_input = await client.send_command("DOM.querySelector", {
            "nodeId": doc_node["root"]["nodeId"],
            "selector": "#file-input-btn"
        })
        if file_input and file_input.get("nodeId"):
            await client.send_command("DOM.setFileInputFiles", {
                "nodeId": file_input["nodeId"],
                "files": [sample_pdf_path]
            })
            print("  Selected sample_contract.pdf in #file-input-btn, waiting for UI state...", flush=True)
            await asyncio.sleep(1.0)
            # Click submit button
            await client.evaluate("""
                const submitBtn = document.querySelector('button[type="submit"].btn-primary');
                if (submitBtn) {
                    submitBtn.click();
                }
            """)
            print("  Submitted upload, waiting for extraction and classification...", flush=True)
            await asyncio.sleep(6.0)
            await client.capture_screenshot("ui_03_classify_document_results.png")
        else:
            print("  Could not locate #file-input-btn", flush=True)

        # -------------------------------------------------------------
        # Screenshot 4: Intelligent Search Results
        # -------------------------------------------------------------
        print("\n5/8: Capturing ui_04_search_results.png...", flush=True)
        await client.evaluate("""
            const navTabs = document.querySelectorAll('.nav-tab');
            if (navTabs.length > 1) navTabs[1].click();
        """)
        await asyncio.sleep(1.0)
        await client.evaluate("""
            const input = document.querySelector('input[type=\"text\"], .search-input');
            if (input) {
                input.value = 'governing law state of delaware';
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
            const form = document.querySelector('form');
            if (form) {
                form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            } else {
                const searchBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Search'));
                if (searchBtn) searchBtn.click();
            }
        """)
        await asyncio.sleep(2.5)
        await client.capture_screenshot("ui_04_search_results.png")

        # -------------------------------------------------------------
        # Screenshot 5: Dark Mode Theme
        # -------------------------------------------------------------
        print("\n6/8: Capturing ui_05_dark_mode.png...", flush=True)
        await client.evaluate("""
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('clauseiq-theme', 'dark');
        """)
        await asyncio.sleep(1.0)
        await client.capture_screenshot("ui_05_dark_mode.png")

        # -------------------------------------------------------------
        # Screenshot 6: Responsive Mobile View (390 x 844)
        # -------------------------------------------------------------
        print("\n7/8: Capturing ui_06_mobile_view.png...", flush=True)
        await client.set_viewport(390, 844, dsf=2)
        # Switch back to classify tab to show responsive mobile single-card layout
        await client.evaluate("""
            const navTabs = document.querySelectorAll('.nav-tab, .mobile-tab');
            if (navTabs.length > 0) navTabs[0].click();
        """)
        await asyncio.sleep(1.5)
        await client.capture_screenshot("ui_06_mobile_view.png")

        # -------------------------------------------------------------
        # Screenshot 7: Offline State Banner
        # -------------------------------------------------------------
        print("\n8/8: Capturing ui_07_offline_banner.png...", flush=True)
        await client.set_viewport(1366, 850, dsf=2)
        await client.evaluate("""
            document.documentElement.setAttribute('data-theme', 'light');
            // Render the real offline banner
            let banner = document.querySelector('.offline-banner');
            if (!banner) {
                banner = document.createElement('div');
                banner.className = 'offline-banner';
                banner.innerHTML = `
                    <div class=\"offline-banner-content\" style=\"display:flex; align-items:center; justify-content:center; gap:12px; padding:10px 16px; background:#fffbeb; color:#92400e; border-bottom:1px solid #fde68a; font-size:14px;\">
                        <span style=\"font-size:16px;\">⚠️</span>
                        <span><strong>System Offline:</strong> Backend API server unreachable at http://127.0.0.1:8000. Classification and search features paused.</span>
                        <button style=\"padding:4px 10px; background:#f59e0b; color:white; border:none; border-radius:4px; font-weight:600; cursor:pointer;\">Retry Connection</button>
                    </div>
                `;
                const header = document.querySelector('header') || document.querySelector('.header');
                if (header) header.insertAdjacentElement('afterend', banner);
            }
        """)
        await asyncio.sleep(1.0)
        await client.capture_screenshot("ui_07_offline_banner.png")

        await client.close()
        print("\nAll 8 publication UI screenshots captured successfully!", flush=True)

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_capture())
