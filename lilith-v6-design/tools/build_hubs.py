#!/usr/bin/env python3
"""Generates the design site's navigation hubs: index.html and the sub-hubs below it.

    python3 lilith-v6-design/tools/build_hubs.py          # write the hub pages
    python3 lilith-v6-design/tools/build_hubs.py --check  # exit 1 if a hub is stale or a link is dead

The hubs are the only pages this writes: index.html, law/index.html, research/index.html,
build/index.html, future/index.html and archive/index.html.  To add a page to the site, add one
card to the tables below and rerun; a card that points at a file that does not exist fails the
build, so a hub can never advertise a dead link.  No law text lives here: the section pages,
standards, ledger and full document are linked, never copied.  Standard library only.
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = "https://github.com/Squirrelthug"
LILITH = f"{GH}/LILITH/blob/main"
SITE_SRC = f"{GH}/squirrelthug.github.io/blob/main/lilith-v6-design"


def card(title, desc, href, *, icon="", color="teal", chip="", num="", go="Open"):
    return dict(title=title, desc=desc, href=href, icon=icon, color=color, chip=chip, num=num, go=go)


# ---------------------------------------------------------------- the law
LAYERS = [
    ("Foundation: how it is built and kept safe", "purple", [
        ("01", "Project Structure & Conventions", "The layout of the code and the house rules every change must follow."),
        ("02", "Security & Credential Management", "Your passphrase, the system keychain, and where secrets are allowed to live."),
        ("03", "Encryption at Rest (SQLCipher)", "How every database on your disk is locked."),
        ("04", "Cross-Platform Foundations", "Making one app behave the same on Windows, macOS and Linux."),
    ]),
    ("Infrastructure: running reliably", "grey", [
        ("05", "Hardware Detection & Capability Tiers", "Working out what your computer can run, including a local model."),
        ("06", "Process Lifecycle & Recovery", "Starting, stopping, and recovering safely from a crash."),
        ("07", "CI/CD Pipeline", "Automated builds and checks on every change."),
        ("08", "Testing Standards", "What must be tested, and how, before anything ships."),
    ]),
    ("Voice: hearing and speaking", "green", [
        ("09", "Audio I/O & Platform Audio APIs", "Microphone and speakers on each system."),
        ("10", "Speech-to-Text (STT)", "Turning what you say into text, on your own computer."),
        ("11", "Text-to-Speech (TTS)", "Turning her replies into a voice."),
    ]),
    ("Intelligence: deciding and thinking", "blue", [
        ("12", "LLM Integration & Provider Abstraction", "Talking to the cloud model or the local one."),
        ("13", "Two-Mode Router", "Deciding whether a request gets a quick answer or a longer piece of work."),
        ("14", "Context Window Manager", "Choosing exactly what the model is shown, and hiding personal details."),
        ("15", "Tool System", "How she does things: the tools she can run."),
    ]),
    ("Data: what she knows and remembers", "aqua", [
        ("16", "UCL Telemetry", "Her private activity log, kept on your computer."),
        ("17", "Enhancement Layers (L1/L2)", "Background summaries of your data, ready when needed."),
        ("18", "Memory System", "What she remembers and how she finds it again."),
        ("19", "Data Sync Pipeline", "Copying in your calendar and contacts."),
    ]),
    ("Apps: the things you use", "orange", [
        ("20", "Contacts / People App", "The people she knows about."),
        ("21", "Calendar App", "Her own calendar."),
        ("22", "Conversation / Chat App", "The chat, and how replies appear."),
    ]),
    ("Personality: who she is", "pink", [
        ("23", "Personality System & System Prompt", "Her character and how she speaks."),
        ("24", "Narrative Layer", "How results become words."),
        ("25", "Onboarding Flow", "The first-run setup."),
    ]),
    ("Frontend: what you see", "amber", [
        ("26", "Frontend Framework & Application Shell", "The window and the app around the chat."),
        ("27", "The Orb", "Her animated face."),
        ("28", "Screen Architecture & Navigation", "The screens and how you move between them."),
    ]),
    ("Amendment: owning your data", "aqua", [
        ("29", "Vault Architecture & Data Ownership", "Your files stay yours; backups and restoring."),
    ]),
]

READING_THE_LAW = [
    card("Full document", "All 29 sections in one long page. Best for searching, or for handing to an agent.", "../full-document.html", icon="📖", color="blue", chip="generated"),
    card("Non-negotiable standards", "The floor below which nothing ships. Read at the start of every build session.", "../standards.html", icon="⚖", color="amber"),
    card("Amendment ledger", "Every change made to the law since it froze, one entry per design session.", "../amendments.html", icon="📜", color="purple", chip="{ledger} entries"),
    card("Design checklist", "Every design question, resolved, with links back to its section.", "../checklist.html", icon="☑", color="green"),
    card("Systems map", "A picture of how the parts fit together.", "../systems.html", icon="🗺", color="aqua"),
]

# ---------------------------------------------------------------- research
WAVE1 = [
    ("00", "Summary", "The ten findings that matter most for building Lilith.", "00-summary.html"),
    ("01", "Assistants through history", "Scribes to chiefs of staff: what separated excellent from adequate.", "01-historical-roles.html"),
    ("02", "The recurring principles", "What holds across professions, ranked by strength of evidence.", "02-principles.html"),
    ("03", "Trust and the first weeks", "A phase model of the relationship, and what should be explicit.", "03-trust-and-onboarding.html"),
    ("04", "What digital assistants teach", "Siri, Alexa, Clippy, companions, AI gadgets, LLM memory.", "04-digital-assistants-evidence.html"),
    ("05", "Adapting to the user", "Reading a person's level without talking down to them.", "05-adaptation-and-accessibility.html"),
    ("06", "Pitfalls", "How this goes wrong, how badly, and what practitioners do.", "06-pitfalls.html"),
    ("07", "Knowing what she can do", "Showing capability, and handing over to a specialist.", "07-capability-awareness-and-handoff.html"),
    ("08", "Questions you did not ask", "What an expert would raise that the brief missed.", "08-questions-you-didnt-ask.html"),
    ("09", "Implications for Lilith", "Design hypotheses and questions for the design session.", "09-implications-for-lilith.html"),
]
WAVE2 = [
    ("00", "Summary", "Ten findings for a whole-life conversational assistant.", "00-summary.html"),
    ("01", "Whole-life management", "Track A: schedules, money, people and responsibilities.", "01-whole-life-management.html"),
    ("02", "The plumber test", "Track B: does it help someone who is not a power user?", "02-the-plumber-test.html"),
    ("03", "Cross-domain synthesis and proactivity", "Track C: what joining domains adds, and when to speak first.", "03-cross-domain-synthesis-and-proactivity.html"),
    ("04", "The conversational lane", "Track D: everyday talk as the main interface.", "04-the-conversational-lane.html"),
    ("05", "Landscape, data and risk", "Track E: the 2024 to 2026 landscape and what can go wrong.", "05-landscape-data-and-risk.html"),
    ("06", "Cross-track synthesis", "Where the tracks disagree, and why it matters.", "06-cross-track-synthesis.html"),
    ("07", "Implications for Lilith", "Hypotheses and design-session questions.", "07-implications-for-lilith.html"),
    ("08", "Questions you did not ask", "What the brief missed.", "08-questions-you-didnt-ask.html"),
]

# ---------------------------------------------------------------- build
SPRINTS = [
    ("B01", "Foundation & Skeleton", "SPRINT-B01-foundation.md"),
    ("B02", "Voice I/O Pipeline", "SPRINT-B02-voice-io.md"),
    ("B03", "Intelligence Core", "SPRINT-B03-intelligence-core.md"),
    ("B04", "Memory & the First Tool", "SPRINT-B04-memory-tool.md"),
    ("B05", "Frontend Shell", "SPRINT-B05-frontend-shell.md"),
    ("B06", "Milestone 1 Integration & Dogfood", "SPRINT-B06-m1-integration.md"),
    ("B07", "Gate: Walking-Skeleton Latency Benchmark", "SPRINT-B07-latency-benchmark.md"),
    ("B08", "Gate: Router Dry-Run", "SPRINT-B08-router-dry-run.md"),
    ("B09", "Foundation Hardening & Telemetry", "SPRINT-B09-foundation-hardening.md"),
]
REPORTS = [
    ("R00", "Introduction", "How we got here, and what we are actually building.", "R00-introduction.md"),
    ("R01", "Foundation and a Voice", "Chapters 1 and 2.", "R01-foundation-and-a-voice.md"),
    ("R02", "A Mind and a Memory", "Chapters 3 and 4.", "R02-a-mind-and-a-memory.md"),
    ("R03", "A Face and First Breath", "Chapters 5 and 6.", "R03-a-face-and-first-breath.md"),
    ("R04", "Proving the Bets", "Chapters 7 and 8, and Experiment 3.", "R04-proving-the-bets.md"),
    ("R05", "Hardening and Trust", "Chapters 9 and 10.", "R05-hardening-and-trust.md"),
    ("R06", "Independence and First Real Data", "Chapters 11 and 12.", "R06-independence-and-first-real-data.md"),
    ("R07", "A Calendar of Her Own, and a Front Door", "Chapters 13 and 14.", "R07-a-calendar-of-her-own-and-a-front-door.md"),
]


# ---------------------------------------------------------------- rendering
def e(s):
    return html.escape(s, quote=True)


def render_card(c, size="", base=""):
    href = c["href"] if c["href"].startswith("http") else base + c["href"]
    ext = " target=\"_blank\" rel=\"noopener\"" if c["href"].startswith("http") else ""
    if size == "small":
        return (f'<a class="card c-{c["color"]}" href="{e(href)}"{ext}><span class="num">{e(c["num"])}</span>'
                f'<span class="body"><span class="title">{e(c["title"])}</span><span class="desc">{e(c["desc"])}</span></span></a>')
    icon = f'<div class="icon" aria-hidden="true">{c["icon"]}</div>' if c["icon"] else ""
    chip = f'<span class="chip">{e(c["chip"])}</span>' if c["chip"] else "<span></span>"
    return (f'<a class="card c-{c["color"]}" href="{e(href)}"{ext}>{icon}<div class="title">{e(c["title"])}</div>'
            f'<div class="desc">{e(c["desc"])}</div><div class="foot">{chip}<span class="go">{e(c["go"])} →</span></div></a>')


def group(title, cards, size="", note="", base=""):
    note_html = f'<p class="group-note">{note}</p>' if note else ""
    inner = "\n".join(render_card(c, size, base) for c in cards)
    cls = {"big": "cards big", "small": "cards small"}.get(size, "cards")
    return f'<div class="group-title">{e(title)}</div>{note_html}\n<div class="{cls}">\n{inner}\n</div>'


def page(title, h1, lede, body, *, depth, crumbs=None, status=""):
    up = "../" * depth
    trail = ""
    if crumbs:
        trail = '<div class="crumbs">' + " › ".join(
            f'<a href="{up}{href}">{e(text)}</a>' for text, href in crumbs) + f" › {e(h1)}</div>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<link rel="stylesheet" href="{up}assets/site.css">
<link rel="stylesheet" href="{up}assets/hub.css">
</head>
<body class="hub">
{trail}
<h1>{e(h1)}</h1>
<p class="hub-lede">{lede}</p>
{status}
{body}
<div class="hub-foot">Generated by <code>tools/build_hubs.py</code>: add a card there, not here. <a href="{up}index.html">Design home</a> · <a href="https://squirrelthug.github.io/">squirrelthug.github.io</a></div>
</body>
</html>
"""


def build_pages():
    ledger = len(re.findall(r'class="ledger-date"', (ROOT / "amendments.html").read_text(encoding="utf-8")))
    pages = {}
    back = [("Design home", "index.html")]

    # ---- law
    law_groups = [group("How to read it", [dict(c, chip=c["chip"].format(ledger=ledger)) for c in READING_THE_LAW], "", base="")]
    for name, color, items in LAYERS:
        cs = [card(f"{t}", d, f"../sections/s{n}.html", color=color, num=f"§{n}") for n, t, d in items]
        law_groups.append(group(name, cs, "small"))
    pages["law/index.html"] = page(
        "Lilith v6: The Design (the law)", "The Design",
        "The frozen design document: 29 sections, split by layer. <strong>This is the law.</strong> It was frozen on 2026-06-29 and changes only through a documented design session, recorded in the amendment ledger.",
        "\n".join(law_groups), depth=1, crumbs=back)

    # ---- research
    r1 = [card(t, d, f"{f}", color="blue", num=n) for n, t, d, f in WAVE1]
    r2 = [card(t, d, f"whole-life/{f}", color="purple", num=n) for n, t, d, f in WAVE2]
    pages["research/index.html"] = page(
        "Lilith v6: Research", "Research",
        "What makes a good assistant, gathered by AI agents and checked by script. <strong>Not law.</strong> Links and quotations were checked; the underlying claims were not. Treat it as leads that feed the next design session.",
        "\n".join([
            group("Start here", [
                card("Spoken guide, wave 1", "The research told as one long piece you can copy into text-to-speech.", "narrative.html", icon="🎧", color="blue", chip="listen"),
                card("Spoken guide, wave 2", "The whole-life assistant research, told the same way.", "whole-life/narrative.html", icon="🎧", color="purple", chip="listen"),
                card("How far to trust it", "What was checked, how, and what failed (wave 1).", "verification.html", icon="🔎", color="amber"),
            ], "big"),
            group("Wave 1: what makes a good assistant", r1 + [card("Sources", "154 numbered sources with the link check.", "sources.html", color="grey", num="··")], "small"),
            group("Wave 2: the whole-life assistant", r2 + [
                card("Wave 2 overview", "The landing page for this wave.", "whole-life/index.html", color="purple", num="··"),
                card("Sources", "The wave 2 source list.", "whole-life/sources.html", color="grey", num="··"),
                card("Verification report", "What was checked in wave 2.", "whole-life/verification.html", color="amber", num="··"),
            ], "small"),
        ]), depth=1, crumbs=back)

    # ---- build
    pages["build/index.html"] = page(
        "Lilith v6: Build and progress", "Build & Progress",
        "How the design becomes software: the plan, the sprints, the story of each stretch of chapters, and where the build stands right now.",
        "\n".join([
            group("Where it stands now", [
                card("Handoff: the present state", "What is built, what is verified and what to do next. Rewritten at the end of every working session.", f"{LILITH}/HANDOFF.md", icon="📍", color="green", chip="GitHub"),
                card("Kanban board", "One card per chapter, with its definition of done.", f"{GH.replace('github.com/', 'github.com/users/')}/projects/46", icon="🗂", color="blue", chip="GitHub"),
                card("Build journal", "An append-only diary of every session, with the lessons learned.", f"{LILITH}/docs/journal/README.md", icon="📓", color="purple", chip="GitHub"),
                card("The code", "The Lilith v6 repository.", f"{GH}/LILITH", icon="💻", color="aqua", chip="GitHub"),
            ], "big"),
            group("The plan", [
                card("Build sequencing", "The milestone plan, the two de-risking experiments, and what is parked beyond v1.", "../BUILD_SEQUENCING.md", icon="🧭", color="amber", chip="Markdown"),
                card("Build guide", "Fourteen sequential chapters and the experiment gates.", "../sprints/BUILD_GUIDE.md", icon="🛠", color="orange", chip="Markdown"),
                card("Future design sessions", "Ideas that are part of the intent but not in v1: the tool bridge, proactive help, cost ledger, more devices.", "../sprints/FUTURE_DESIGN_SESSIONS.md", icon="🔮", color="purple", chip="Markdown"),
                card("Calendar app spec", "A worked feature specification (§21).", "../specs/calendar-app.spec.md", icon="📅", color="aqua", chip="Markdown"),
            ], "big", note="Markdown pages open as plain text in the browser."),
            group("Sprints", [card(t, "", f"../sprints/{f}", color="orange", num=n) for n, t, f in SPRINTS]
                  , "small"),
            group("Chapter reports: the story in plain English", [card(t, d, f"../reports/{f}", color="blue", num=n) for n, t, d, f in REPORTS], "small"),
        ]), depth=1, crumbs=back)

    # ---- future
    pages["future/index.html"] = page(
        "Lilith v6: Beyond version 1", "Beyond v1",
        "Where Lilith is going. <strong>Nothing here is built, and none of it is law.</strong> Each idea becomes real only through a design session.",
        "\n".join([
            group("The big idea", [
                card("Nexus: Lilith plus your other tools", "Lilith as the coordinator that lets separate devices and services work as one system, such as a smart home, over a shared tool standard (MCP). Conceptual: the last chapter of the plain-words guide.", "../lilith-for-everyone.pdf", icon="🔗", color="purple", chip="PDF, chapter 7"),
                card("Future design sessions", "The parking list: tool bridge, proactive help, more models, cost ledger, installers, storage tiers, many devices.", "../sprints/FUTURE_DESIGN_SESSIONS.md", icon="🔮", color="amber", chip="Markdown"),
            ], "big"),
            group("Decided next, in the build repository", [
                card("Design sessions DS-0 to DS-5", "The briefs behind writing, reminders, weather, first run, and relationship cards.", f"{LILITH}/docs/design-sessions/README.md", icon="🗒", color="blue", chip="GitHub"),
                card("Autopilot plan P01", "The next 27 tasks: places, an app launcher, web search, first run. A draft awaiting approval.", f"{LILITH}/tasks/P01-sprint-draft.md", icon="🚀", color="green", chip="GitHub"),
                card("Multiple devices (v7)", "One Lilith across several computers. Decided as a v7 job, because the security work is large.", "../sprints/FUTURE_DESIGN_SESSIONS.md", icon="🖥", color="grey", chip="Markdown"),
            ], "big"),
        ]), depth=1, crumbs=back)

    # ---- archive
    pages["archive/index.html"] = page(
        "Lilith v6: Archive and history", "Archive & History",
        "How the project got here. Kept intact for reference; nothing here is current.",
        "\n".join([
            group("Earlier versions of this site", [
                card("Overview, build phase", "The previous home page: status, locked decisions and the section directory.", "overview-build-phase.html", icon="🗄", color="grey"),
            ], "big"),
            group("Writing about the project", [
                card("The blog", "Posts on why Lilith started, why it started over, and what was learned.", "../../blog.html", icon="✍", color="pink"),
                card("Design history", "The research, ADRs and design-phase records that produced the frozen design.", f"{LILITH.replace('/blob/main', '/tree/design-history')}", icon="📚", color="blue", chip="GitHub branch"),
                card("Version 5", "The earlier build, kept for lessons only. No code crosses into v6.", f"{GH}/lilith-v5", icon="🕰", color="grey", chip="GitHub"),
            ], "big"),
        ]), depth=1, crumbs=back)

    # ---- home
    status = ('<div class="hub-status"><span><strong>Where it stands:</strong> build phase, now being used by its builder</span>'
              '<span>Design frozen 2026-06-29 · cleared for build 2026-07-17</span>'
              f'<span><a href="{LILITH}/HANDOFF.md" target="_blank" rel="noopener">Current state in detail →</a></span></div>')
    top = [
        card("Lilith in plain words", "An eight-page guide for anyone: what she does today, what is already decided, why she costs less, how she protects your information, and where Nexus could take her.", "lilith-for-everyone.pdf", icon="🌟", color="teal", chip="PDF · 8 pages", go="Read"),
        card("The Design", "The frozen design document: 29 sections by layer, the standards, and every amendment. This is the law.", "law/index.html", icon="📖", color="blue", chip="Law · 29 sections"),
        card("Build & Progress", "The plan, the sprints, the chapter reports, and where the build stands right now.", "build/index.html", icon="🛠", color="green", chip="9 sprints · 8 reports"),
        card("Research", "What makes a good assistant, in two waves. Gathered by agents and checked by script. Leads, not law.", "research/index.html", icon="🔬", color="purple", chip="Not law · 2 waves"),
        card("Beyond v1", "Nexus, proactive help, more devices and the other ideas that are not built yet.", "future/index.html", icon="🔮", color="amber", chip="Ideas"),
        card("Archive & History", "Earlier home pages, the blog, the design-phase records, and version 5.", "archive/index.html", icon="🗄", color="grey", chip="Reference"),
    ]
    quick = [
        card("Full document", "All 29 sections on one page.", "full-document.html", color="blue", num="📖"),
        card("Standards", "The floor nothing ships below.", "standards.html", color="amber", num="⚖"),
        card("Amendment ledger", f"{ledger} recorded changes.", "amendments.html", color="purple", num="📜"),
        card("Spoken research guide", "Copy it into text-to-speech.", "research/narrative.html", color="blue", num="🎧"),
    ]
    pages["index.html"] = page(
        "Lilith v6: Design Home", "Lilith v6",
        "A personal assistant that lives on your own computer, built so that she costs less to run and keeps your information at home. Choose a card to go in; every page below can be reached from here.",
        "\n".join([group("Explore", top, "big"), group("Jump straight to", quick, "small")]), depth=0, status=status)
    return pages


def check_links(pages):
    bad = []
    for rel, text in pages.items():
        base = (ROOT / rel).parent
        for href in re.findall(r'href="([^"#]+)"', text):
            if href.startswith(("http", "mailto:")):
                continue
            target = (base / href).resolve()
            if not target.exists() and str(target.relative_to(ROOT)) not in pages:
                bad.append(f"{rel}: dead link {href}")
    return bad


def main(argv):
    pages = build_pages()
    problems = check_links(pages)
    for rel, text in pages.items():
        path = ROOT / rel
        if "--check" in argv:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                problems.append(f"{rel} is stale: run build_hubs.py")
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    for p in problems:
        print("FAIL:", p)
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
