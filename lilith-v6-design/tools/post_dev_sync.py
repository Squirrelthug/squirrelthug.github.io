#!/usr/bin/env python3
"""Post-development checks for the design site: what an autopilot runs after a LILITH merge.

The law changes only through documented amendments (see README "Amendment convention").  After
an amendment branch lands, or a stack of them, run:

    python3 tools/post_dev_sync.py check            # exits 1 if anything is wrong (CI-shaped)
    python3 tools/post_dev_sync.py build            # regenerate full-document.html, then check
    python3 tools/post_dev_sync.py verify <rev-range>   # every line the [amend] commits added is in the tree

``check`` proves: no merge-conflict markers anywhere under the site; ``full-document.html`` is
exactly what ``build_fulldoc.py`` would write now; each section page that carries an
``Amendment added`` line is represented in the amendments ledger by an entry on or after that
date; the ledger entries are in date order.

``verify`` exists because a stacked merge once resolved a conflict by taking one side of a section
page and silently dropped three amendment bullets (the ledger and the generated document were
intact, so ``check`` alone could not see it).  It replays ``git diff <commit>^ <commit>`` for each
non-merge commit in the range whose subject starts with ``[amend]`` and fails if any added line of
a hand-edited file is absent from the working tree.

Standard library only; run from anywhere.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
MARKERS = re.compile(r"^(<<<<<<< |=======$|>>>>>>> )", re.MULTILINE)
META = re.compile(r"Amendment added: (\d{4}-\d{2}-\d{2})")
LEDGER_DATE = re.compile(r'class="ledger-date">(\d{4}-\d{2}-\d{2})<')
GENERATED = {"lilith-v6-design/full-document.html"}


def _run(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True, cwd=REPO).stdout


def build() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_fulldoc.py")], check=True)


def check() -> list[str]:
    problems: list[str] = []
    for page in sorted(ROOT.rglob("*.html")):
        if "archive" in page.parts or "research" in page.parts:
            continue
        if MARKERS.search(page.read_text(encoding="utf-8")):
            problems.append(f"merge-conflict markers in {page.relative_to(REPO)}")
    target = ROOT / "full-document.html"
    before = target.read_bytes()
    try:
        build()
        if target.read_bytes() != before:
            problems.append("full-document.html is stale: run `post_dev_sync.py build`")
    finally:
        target.write_bytes(before)
    ledger = (ROOT / "amendments.html").read_text(encoding="utf-8")
    dates = LEDGER_DATE.findall(ledger)
    if dates != sorted(dates):
        problems.append("amendments ledger entries are not in date order")
    latest = dates[-1] if dates else ""
    for page in sorted((ROOT / "sections").glob("s*.html")):
        newest = max(META.findall(page.read_text(encoding="utf-8")), default="")
        if newest and newest > latest:
            problems.append(f"{page.name} has an amendment dated {newest} after the last ledger entry")
    return problems


def verify(rev_range: str) -> list[str]:
    problems: list[str] = []
    commits = _run("git", "log", "--no-merges", "--format=%h %s", rev_range).splitlines()
    for line in commits:
        sha, _, subject = line.partition(" ")
        if not subject.startswith("[amend]"):
            continue
        for name in _run("git", "show", sha, "--name-only", "--format=").split():
            path = REPO / name
            if name in GENERATED or not name.endswith((".html", ".md")) or not path.exists():
                continue
            current = path.read_text(encoding="utf-8")
            for added in _run("git", "diff", f"{sha}^", sha, "--", name).splitlines():
                text = added[1:].strip()
                if added.startswith("+") and not added.startswith("+++") and text:
                    if text not in current:
                        problems.append(f"{sha} {name}: missing line {text[:80]!r}")
    return problems


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else "check"
    if command == "build":
        build()
        problems = check()
    elif command == "check":
        problems = check()
    elif command == "verify" and len(argv) > 2:
        problems = verify(argv[2])
    else:
        print(__doc__)
        return 2
    for problem in problems:
        print("FAIL:", problem)
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
