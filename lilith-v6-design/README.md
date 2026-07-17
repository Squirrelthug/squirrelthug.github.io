# Lilith v6 — Design Document Site

This folder is the complete, self-contained design record for **Lilith v6**, a
voice-first personal AI assistant. It is both a human-readable website (open
`index.html`) and the canonical reference an LLM agent reads before doing any
design or build work on this project.

**Status:** design FROZEN 2026-06-29 · three adversarial review rounds passed ·
CLEARED FOR BUILD 2026-07-17 · build phase not yet started.

## What is law

The 29 section pages in `sections/` (s01–s29) are **the law**. They were split
verbatim from the original single-file design document; agents implement
against them *exactly as written*. No architectural decision is made during
build without a documented design session, and no section text changes outside
one.

Priority order when reading:

1. `sections/sNN.html` — the section(s) relevant to your task (each section's
   sprints must guarantee that section is complete)
2. `standards.html` — non-negotiable standards; read at the start of every
   agent session; the floor below which code does not ship
3. `BUILD_SEQUENCING.md` — milestone plan: Milestone 1 (walking-skeleton voice
   loop + two de-risking experiments), then Phases 2–7 in dependency order
4. `full-document.html` — all 29 sections in one file, if you need the whole
   document in context

## Site map

| File / dir | What it is |
|---|---|
| `index.html` | Overview home: status, locked decisions, progress, section directory |
| `sections/s01.html` … `s29.html` | **The law.** One page per section, verbatim, grouped by layer |
| `full-document.html` | All 29 sections in one page — *generated*, do not edit directly |
| `checklist.html` | Design checklist mirror — every item resolved, backlinks per section |
| `standards.html` | Non-negotiable standards (updated 2026-07-17 against the frozen doc) |
| `systems.html` | Visual system architecture map (June 2026 companion; the document wins on conflict) |
| `amendments.html` | Canonical amendment ledger, verbatim, one entry per design session |
| `BUILD_SEQUENCING.md` | Build milestone plan + Experiments 1–2 specs + parked post-v1 scope |
| `assets/site.css` | Shared styles + nav (presentation only) |
| `tools/build_fulldoc.py` | Regenerates `full-document.html` from `sections/` + `amendments.html` |

## Amendment convention

Amendments happen only through a documented design session. One amendment =

1. Edit the section text **in place** on each touched `sections/sNN.html` page
2. Add an `s-meta` line inside each touched section:
   `<div class="s-meta">Amendment added: YYYY-MM-DD · Touches: §xx …</div>`
3. Append one verbatim entry to the ledger in `amendments.html`
4. Run `python3 tools/build_fulldoc.py` to regenerate `full-document.html`
5. Update the touched sections' resolved-banner text in `checklist.html` if the
   resolution summary changed

Committed working hypotheses (tunable only via the convention above): router
misroute-to-conversational ≤5% over a SHA-256-frozen 100-utterance set with
stream-and-cut single-path as the named fallback; PII recall gates ≥95% names /
100% emails / 100% phones (merge-blocking CI); skill-injection cap 8192 bytes
(reject, never truncate); staleness-refresh budgets ~1000 ms conversational /
10 s artifact; external backups default `~/Documents/Lilith Backups/`.

## History / provenance

The design phase's inputs and working records live outside this site in
`~/Desktop/lilith-v6-preliminary/`: the research reports and planning tree
(`research/`), all three review rounds' prompts, reports, ADRs, and session
logs (`archive/`), the design-phase sprint spec (`SPRINT_DESIGN_PHASE.md`),
and the byte-exact pre-split snapshot of the original single-file document
(`index-original-2026-07-17.html`). Lilith v6 supersedes a working-but-
hardcoded v5; the research folder documents why v6 was redesigned from scratch.
