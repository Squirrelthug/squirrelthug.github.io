#!/usr/bin/env python3
"""Prints vision/index.html to lilith-the-whole-picture.pdf with a headless Chromium browser.

    python3 lilith-v6-design/vision/build_pdf.py

The page's own print stylesheet (light colours, one chapter per page) shapes the PDF, so edit
the page, not the PDF.  Needs Chrome, Chromium or Edge; standard library only.
"""

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "index.html"
OUT = HERE.parent / "lilith-the-whole-picture.pdf"
CANDIDATES = [
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "msedge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def browser() -> str:
    for c in CANDIDATES:
        found = shutil.which(c) or (c if Path(c).exists() else None)
        if found:
            return found
    sys.exit("no Chrome, Chromium or Edge found")


def main() -> None:
    subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT}", PAGE.as_uri()], check=True, capture_output=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
