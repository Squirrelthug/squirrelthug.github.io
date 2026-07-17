#!/usr/bin/env python3
"""Regenerate full-document.html from the per-section pages + amendments.html.

Run this after ANY amendment to a section page or the ledger:

    python3 tools/build_fulldoc.py

Source of truth:
  - sections/s01.html .. s29.html   -> the 29 <details> blocks (the law)
  - amendments.html                 -> the footer ledger
  - tools/fulldoc_template.html     -> page chrome (header, nav, status banner,
                                       locked decisions, how-to)

The script inverts the section pages' two mechanical transforms (the `open`
attribute and the ../-relative link paths) so the assembled document reads
exactly like the original single-file design document, with root-relative
links. It aborts if a section page is missing, malformed, or out of order.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ROOT / "sections"
OUT = ROOT / "full-document.html"

# section-page href prefix -> full-document (root) href
HREF_MAP = [
    ('href="../checklist.html', 'href="checklist.html'),
    ('href="../standards.html', 'href="standards.html'),
    ('href="../BUILD_SEQUENCING.md"', 'href="BUILD_SEQUENCING.md"'),
    ('href="../SPRINT_DESIGN_PHASE.md"', 'href="SPRINT_DESIGN_PHASE.md"'),
]

blocks = []
layers = []  # (layer_class, layer_name) per section, to re-emit dividers on change
for n in range(1, 30):
    page_path = SECTIONS / f"s{n:02d}.html"
    if not page_path.exists():
        sys.exit(f"FATAL: missing {page_path}")
    page = page_path.read_text(encoding="utf-8")
    m = re.search(r'<details id="s(\d+)" open>.*?</details>', page, re.S)
    if not m or int(m.group(1)) != n:
        sys.exit(f"FATAL: {page_path.name}: details block missing or id mismatch")
    block = m.group(0).replace(f'<details id="s{n}" open>', f'<details id="s{n}">', 1)
    for a, b in HREF_MAP:
        block = block.replace(a, b)
    blocks.append(block)
    lm = re.search(r'<div class="layer (l-\w+)">([^<]+)</div>', page)
    if not lm:
        sys.exit(f"FATAL: {page_path.name}: layer divider missing")
    layers.append((lm.group(1), lm.group(2)))

parts = []
prev_layer = None
for (lcls, lname), block in zip(layers, blocks):
    if (lcls, lname) != prev_layer:
        parts.append(f'<div class="layer {lcls}">{lname}</div>\n')
        prev_layer = (lcls, lname)
    parts.append(block + "\n")
sections_html = "\n".join(parts)

# ledger from amendments.html
amend = (ROOT / "amendments.html").read_text(encoding="utf-8")
hm = re.search(r'<div class="ledger-header">(.*?)</div>', amend, re.S)
entries = [m.group(1) for m in re.finditer(r'<span class="ledger-text">(.*?)</span></li>', amend, re.S)]
if not hm or not entries:
    sys.exit("FATAL: could not parse ledger from amendments.html")
ledger = hm.group(1) + "".join(" · " + e for e in entries)

template = (ROOT / "tools" / "fulldoc_template.html").read_text(encoding="utf-8")
OUT.write_text(
    template.replace("{SECTIONS}", sections_html).replace("{LEDGER}", ledger),
    encoding="utf-8",
)
print(f"full-document.html: {len(blocks)} sections, {len(entries)} ledger entries")
