# Lilith v6 — Build Guide

**Sprint ID:** BUILD-00
**Status:** Active — this is the master roadmap for the entire build phase
**Prerequisites:** Design frozen 2026-06-29 · cleared for build 2026-07-17 · `BUILD_SEQUENCING.md` current
**Supersedes nothing. Subordinate to:** `../sections/` (the law), `../standards.html`, `../BUILD_SEQUENCING.md`

---

## 1. What this document is

The design is done. This guide converts the frozen 29-section design document into a **sequential table of contents for building it**: fourteen chapters, in dependency order, each written up like a task a developer would be handed — goal, scope, deliverables, and an explicit Definition of Done.

There is no calendar. Chapters are finished whenever they are finished, in order. Progress is position in the sequence, not a date.

**One chapter = one future sprint document.** This guide deliberately does *not* contain the task-by-task breakdown for every chapter. Detailed sprints are authored **just-in-time**: when a chapter's Definition of Done is met, the next chapter's sprint is written (see §3). That way each sprint is authored with full knowledge of what the codebase actually looks like, instead of guessed months ahead.

## 2. Ground rules (inherited, non-negotiable)

1. **Only what is written gets built.** The section pages `../sections/s01.html`–`s29.html` are the law, implemented exactly as written. No architectural decision is made during build without a documented design session, and no section text changes outside one (amendment convention in `../README.md`).
2. **Standards are the floor.** `../standards.html` is read at the start of every agent session. Code below that floor does not ship.
3. **Excluded means absent.** When a chapter marks a design section EXCLUDED or DEFERRED, no partial version, stub-with-logic, or "while I'm here" implementation of it may appear. Deferred scope arrives in its named chapter and nowhere earlier.
4. **Validation gates are hard gates.** Experiments 1–2 (Chapters 7–8) must pass — or their named fallback consequence must be executed — before any Phase 2+ chapter begins. Experiment 3 is a floating gate (§6).

## 3. The working loop

Every chapter runs the same cycle:

```
┌─► Author the sprint document for the next chapter
│     sprints/SPRINT-B<NN>-<slug>.md — from this guide + BUILD_SEQUENCING.md
│     + the chapter's design sections. Task format per §7. Every task
│     gets an explicit Docs: field naming its exact documentation
│     contributions (standards page, Documentation Standards) — a task
│     is not done until its named docs contribution has landed.
│
├─► Work the sprint task by task
│     Each agent session receives: (a) ../standards.html,
│     (b) the sNN.html sections named by its task, (c) the task write-up itself.
│     The developer monitors the build closely and adjusts task order/content
│     as reality demands — but never scope beyond the design sections.
│
├─► Close the chapter
│     Verify every item in the chapter's Definition of Done below.
│     Update the status table in §4 of this guide.
│
└─► Repeat for the next chapter
```

**Agent context contract** — any agent working a sprint task must be given, at minimum:
1. `../standards.html` — the non-negotiable floor
2. The `../sections/sNN.html` pages listed in its task (the law for that task)
3. The task write-up from the current sprint document
4. This guide's ground rules (§2) — or a verbatim copy of them in the sprint header

If build work exposes a genuine gap or contradiction in the design, the agent **stops and reports**; the developer resolves it through a documented design session (amendment convention), never by improvising in code.

## 4. Table of contents — chapter status

| # | Chapter | Covers | Status |
|:--|:--|:--|:--|
| CH-01 | Foundation & Skeleton | §01 §02 §03 §04 §06 §08 | Not started |
| CH-02 | Voice I/O Pipeline | §05 §09 §10 §11 | Not started |
| CH-03 | Intelligence Core | §12 §23 §14 §13 | Not started |
| CH-04 | Memory & the First Tool | §18 §15 §24 | Not started |
| CH-05 | Frontend Shell | §26 §22 §27 §28 | Not started |
| CH-06 | Milestone 1 Integration & Dogfood | all M1 sections, end-to-end | Not started |
| CH-07 | GATE — Experiment 1: Latency Benchmark | BUILD_SEQUENCING §3, Exp 1 | Not started |
| CH-08 | GATE — Experiment 2: Router Dry-Run | BUILD_SEQUENCING §3, Exp 2 | Not started |
| CH-09 | Phase 2 — Foundation Hardening & Telemetry | §16 §06 §07 | Not started |
| CH-10 | Phase 3 — Security & Key Management | §02 §03 §14 §08 | Not started |
| CH-11 | Phase 4 — Local Intelligence & Fallbacks | §12 §05 | Not started |
| CH-12 | Phase 5 — Custodian App Suite | §19 §20 §28 | Not started |
| CH-13 | Phase 6 — Calendar App | §21 §26 §28 | Not started |
| CH-14 | Phase 7 — Onboarding, Extension & Final Freeze | §25 §27 §29 | Not started |
| EXP-3 | Floating gate — Encrypted Vector Feasibility | §18 Recall Roadmap | Not started (may run any time before any vector dependency ships) |

Chapters CH-01 → CH-06 together produce **Milestone 1** exactly as scoped by the table in `../BUILD_SEQUENCING.md` §2.1. Sections that table marks EXCLUDED (§07 CI/CD, §16 UCL DB, §17 L1/L2, §19 sync, §20 contacts, §21 calendar, §25 onboarding, §29 vault) stay absent through CH-06 (ground rule 3); the M1 table's per-section scope notes are the authoritative in/out line for every M1 chapter below. CH-07/CH-08 may run in either order; both must resolve before CH-09.

---

## 5. The chapters

### CH-01 — Foundation & Skeleton

**Design sections (the law for this chapter):** §01 Project Structure · §02 Security & Credentials · §03 SQLCipher · §04 Cross-Platform Foundations · §06 Process Lifecycle · §08 Testing Standards

**Goal:** A repository that starts, opens one encrypted database, shuts down cleanly, and has a working test harness — the skeleton every later chapter hangs code on.

**Scope (per the M1 table):**
- §01 — directory layout, module boundaries, standard imports, `pathlib.Path` defaults.
- §02 — `python-keyring` with `master_passphrase` and the Anthropic API key; insecure-fallback checks active.
- §03 — key and mount **exactly one** database, `conversation_db`, via the `SessionKeyManager` PRAGMA hex-key wrapper. (Schema content lands in CH-04; this chapter proves keyed open/close.)
- §04 — `platform/paths.py`, Linux defaults. Native Windows/macOS packaging deferred.
- §06 — single-instance `lilith.lock`; graceful shutdown closing the audio stream slot and the single DB. (Lockfile state table / quarantine logic is CH-09 scope.)
- §08 — pytest harness and conventions established; real-SQLCipher test fixtures working.

**Out of scope:** every EXCLUDED section; any second database; CI/CD (§07 is CH-09).

**Deliverables:** initialized build repo laid out per §01; credential bootstrap per §02; `conversation_db` opening under SQLCipher per §03; path module per §04; lock + shutdown per §06; test scaffold per §08.

**Definition of Done:**
- [ ] Fresh checkout on the MASTER machine: documented setup steps → app process starts, keys and opens `conversation_db`, exits cleanly on signal.
- [ ] A second concurrent launch refuses to start (lock respected).
- [ ] No credential exists anywhere except the OS keyring; the §02 insecure-fallback checks demonstrably fire when the keyring is unavailable.
- [ ] Test suite runs green locally and includes at least one real-SQLCipher round-trip test.
- [ ] Every §-scope item above is implemented as written, and a scope audit confirms nothing from an EXCLUDED section exists in the repo.

---

### CH-02 — Voice I/O Pipeline

**Design sections:** §05 Hardware Detection & Tiers · §09 Audio I/O · §10 STT · §11 TTS

**Goal:** Sound in, text out; text in, sound out — both halves of the voice loop working independently on the dev machine, before any intelligence sits between them.

**Scope (per the M1 table):**
- §05 — capability query deciding Whisper execution mode (CPU vs GPU fallbacks).
- §09 — `sounddevice` input/output streams: mono 16 kHz capture; output chunk queues for Kokoro audio.
- §10 — `faster-whisper` + Silero VAD; silence thresholds and VAD onset/offset operational.
- §11 — `kokoro-onnx` on CPU; playback queues handling streamed chunks.

**Out of scope:** router, LLM, GUI; secondary endpoints (parked, post-v1).

**Deliverables:** hardware-tier module; capture and playback streams; VAD-gated transcription path; streaming TTS path — each per its section.

**Definition of Done:**
- [ ] Speaking into the mic produces a correct transcript through the VAD→STT path (verified on real hardware, not only fixtures).
- [ ] An arbitrary text string is synthesized and audibly played through the chunk-queue path without underruns.
- [ ] Hardware detection returns the correct tier/mode on the dev machine and the CPU fallback path is exercised in tests.
- [ ] Unit tests cover the audio stream, Whisper inference, and Kokoro inference per §08 conventions.

---

### CH-03 — Intelligence Core

**Design sections:** §12 LLM Integration · §23 Personality & System Prompt · §14 Context Window Manager · §13 Two-Mode Router

**Goal:** A typed string goes in; a routed, personality-carrying, PII-protected Claude response streams out. Text-only — voice and GUI attach later.

**Scope (per the M1 table):**
- §12 — thin Anthropic provider adapter (BYOK), caching parameters enabled.
- §23 — static `EDICTS.md` / `VOICE.md` parsed into the prompt. Local PERS-2 model deferred.
- §14 — system identity block + recent-history block (≤1,200 tokens), **plus the full conversational-path cloud PII tokenization pass**: detector, session-scoped substitution, streaming reverse-substitution with the partial-tag hold rule and unmapped-tag placeholders. (Task-owned artifact mapping snapshots, re-lock cancellation wiring, and the §08 recall-corpus CI gate are CH-10 scope, as amended 2026-07-12.)
- §13 — deterministic keyword/intent rule classifier splitting conversational vs artifact routes.

**Out of scope:** tools (CH-04), local LLM providers (CH-11), the §14 artifact-lifecycle surface named above.

**Deliverables:** provider adapter; prompt assembly; CWM with tokenization pipeline; rule router — each per its section.

**Definition of Done:**
- [ ] Typed input → router decision → CWM-assembled context → streamed Claude reply, end to end.
- [ ] Against a mocked LLM endpoint: no detectable name, email, or phone number appears in any outbound payload; tags map back correctly in responses, including the partial-tag hold and unmapped-tag placeholder paths.
- [ ] Router unit tests demonstrate both routes firing on representative inputs (formal accuracy measurement is CH-08's job, not this one).
- [ ] Prompt caching parameters verified active on the stable system blocks.

---

### CH-04 — Memory & the First Tool

**Design sections:** §18 Memory System · §15 Tool System · §24 Narrative Layer

**Goal:** Lilith remembers. Conversation turns persist, and the one Milestone-1 tool — `recall_memory` — retrieves them through the tool runner with its spoken narratives.

**Scope (per the M1 table):**
- §18 — `conversation_db` schema (`turns`, `sessions`) + SQLite FTS5 index. Vector embeddings / `memory_db` deferred per the §18 Recall Roadmap — gated by EXP-3, not this chapter.
- §15 — core runner wrapper executing **exactly one** tool: `recall_memory`.
- §24 — `recall_memory`'s `tool.yaml` narratives: acknowledge, handoff template, failure.

**Out of scope:** any embedding dependency, vector extension, or `memory_embeddings` table (ground rule 4 / EXP-3); any second tool.

**Deliverables:** schema + FTS5 migration; tool runner + `recall_memory`; narrative wiring — each per its section.

**Definition of Done:**
- [ ] Conversation turns from the CH-03 pipeline persist to `turns`/`sessions` and are FTS5-indexed.
- [ ] A recall query routes to the artifact lane, executes `recall_memory`, and returns a response built from real stored dictations, with acknowledge/handoff narratives firing in order and the failure narrative firing on a forced error.
- [ ] `pip`/lock-file audit: no vector or embedding dependency present.
- [ ] Integration test covers dictate → persist → recall round-trip per §08.

---

### CH-05 — Frontend Shell

**Design sections:** §26 Frontend Framework & Shell · §22 Conversation/Chat App · §27 The Orb · §28 Screen Architecture

**Goal:** The pipeline gets a face: a PySide6 window with chat bubbles, a typed input box, a voice-reactive orb, and a stub settings screen.

**Scope (per the M1 table):**
- §26 — PySide6 application shell; thread-safe `UICommandBus` dispatching events to the GUI.
- §22 — minimal chat window: conversational bubbles, tool panels, typed text input.
- §27 — simplified ModernGL orb widget: basic idle + voice-reactive pulsing. Advanced state migrations deferred to CH-14.
- §28 — `Chat` screen plus a basic stubbed `Settings` screen (API key entry) only.

**Out of scope:** onboarding UI (CH-14), contacts/calendar screens (CH-12/CH-13), full orb state machine (CH-14).

**Deliverables:** app shell + command bus; chat screen; orb widget; settings stub — each per its section.

**Definition of Done:**
- [ ] GUI launches from the app entry point; typed input flows through the CH-03/CH-04 pipeline and renders as bubbles and tool panels.
- [ ] Orb renders, idles, and visibly reacts to live audio amplitude.
- [ ] API key entered in Settings lands in the OS keyring per §02 and is used on the next LLM call.
- [ ] UI events cross threads only via `UICommandBus`; no direct cross-thread widget calls (code-review check).

---

### CH-06 — Milestone 1 Integration & Dogfood

**Design sections:** every M1-REQUIRED section (§01–§06, §08–§15, §18, §22–§24, §26–§28) — this chapter closes them *as a system*.

**Goal:** The walking skeleton, whole: Mic → VAD → STT → Router → CWM → LLM → TTS → Speaker, with GUI, memory, and the `recall_memory` tool — usable for real daily note-taking and voice retrieval.

**Scope:** integration, wiring, and gap-closing only. No new features; any discovered design gap goes through §3's stop-and-report path.

**Deliverables:** the end-to-end voice loop; a written dogfood setup note (how the developer starts and uses it daily).

**Definition of Done:**
- [ ] The `BUILD_SEQUENCING.md` §2 objective demonstrably works: dictate a note by voice; later ask *"what did I say about …"* by voice; Lilith routes, recalls via FTS5, and answers aloud.
- [ ] Exactly one database (`conversation_db`) and exactly one tool (`recall_memory`) exist.
- [ ] Full-system scope audit against the M1 table: every REQUIRED row's scope note satisfied; every EXCLUDED row still absent.
- [ ] Telemetry events flow to the dev log (`APP_INTERNAL_DIR/logs/dev.log`) as the M1 stand-in for `ucl_db`.
- [ ] The developer has actually used it for at least one real dictate-and-recall session. Dogfooding starts now and continues through all later chapters.

---

### CH-07 — GATE · Experiment 1: Walking-Skeleton Latency Benchmark

**Spec (the law for this chapter):** `../BUILD_SEQUENCING.md` §3, Experiment 1 — executed exactly as written.

**Goal:** Validate the ≤3 s conversational latency bet on Tier 0 hardware **with the §14 tokenization pipeline in place**.

**Deliverables:** the benchmark harness; two full 50-query runs (tokenization on / off); per-query timings; `tokenization_delta_p50` / `tokenization_delta_p90`; a written report artifact.

**Definition of Done:**
- [ ] Both runs executed per the spec's procedure, query set meeting its PII/echo-back requirements.
- [ ] Report records p90 (tokenization enabled) against the 3.5 s bar, both deltas, and the verdict.
- [ ] **Pass:** gate closed, result logged here. **Fail:** the spec's fallback ladder is followed in order (detector optimization → stream-and-cut → soft token cap), each step documented, before this gate may close.

---

### CH-08 — GATE · Experiment 2: Router Dry-Run (Counterfactual)

**Spec:** `../BUILD_SEQUENCING.md` §3, Experiment 2 — executed exactly as written, including the pre-committed thresholds.

**Goal:** Falsifiably test the two-mode fork: rule-router decisions vs what a single always-streaming path would have observed, over a frozen 100-utterance set.

**Deliverables:** the frozen utterance set (SHA-256 recorded **before** any rule tuning); dry-run harness; per-utterance verdict table; JSONL results file; report with the three misroute rates and the go/no-go consequence.

**Definition of Done:**
- [ ] Set frozen and hashed before tuning; procedure, mechanical verdicts, and telemetry events per spec; ≤5 `error` verdicts.
- [ ] Rates reported against the pre-committed gates (`total > 10%` or `misroute_to_conversational > 5%`).
- [ ] **Below thresholds:** two-mode confirmed for v1; fork closed; recorded here. **Above either:** the stream-and-cut single-path design session is scheduled and held *before* CH-09 begins — the triggered review cannot be retroactively cancelled by re-runs.

---

### CH-09 — Phase 2: Foundation Hardening & Telemetry

**Design sections:** §16 UCL Telemetry · §06 (state table, crash recovery, quarantine) · §07 CI/CD — deliverables and validation per `../BUILD_SEQUENCING.md` §4, Phase 2.

**Goal:** Real telemetry database, sanitized logging, crash-safe recovery, and cross-platform CI — the structural hardening dogfooding now depends on.

**Deliverables:** `ucl_db` mounted (§16); logging sanitizer + strict plaintext-logs boundary; lockfile state table, crash recovery, quarantine logic (§06); parallel GitHub Actions CI for Linux/macOS/Windows (§07).

**Definition of Done:**
- [ ] Phase-2 validation passes as written: clean-VM artificial crash → corrupt DBs quarantined → app prompts restore-from-backup, never silently deletes.
- [ ] Telemetry events migrate from dev-log to `ucl_db`; sanitizer verifiably strips sensitive content from plaintext logs.
- [ ] All three CI platform jobs green on the main branch.

---

### CH-10 — Phase 3: Security & Key Management Expansion

**Design sections:** §02 §03 (rotation/relock) · §14 (artifact lifecycle surface) · §08 (recall-corpus gate) — per `../BUILD_SEQUENCING.md` §4, Phase 3.

**Goal:** Complete the credential lifecycle and finish the §14 PII surface that CH-03 deliberately deferred.

**Deliverables:** passphrase rotation + database relocking wrappers; task-owned artifact mapping snapshots with fail-closed cancellation at re-lock (`error.artifact.relock_cancelled`); `context.token.unmapped` wired into `ucl_db`; the merge-blocking §08 recall-corpus CI gate (≥95% names / 100% emails / 100% phones).

**Definition of Done:**
- [ ] Phase-3 validation passes as written: mocked endpoint shows no PII outbound; correct tag mapping including the unmapped-tag placeholder path; in-flight artifact task across a re-lock is cancelled fail-closed with its late response discarded.
- [ ] Recall-corpus gate is live in CI and demonstrably blocks a merge on regression.
- [ ] Passphrase rotation completes on a populated database without data loss.

---

### CH-11 — Phase 4: Local Intelligence & Fallbacks

**Design sections:** §12 (Ollama backend) · §05 (tier gates) — per `../BUILD_SEQUENCING.md` §4, Phase 4.

**Goal:** Tier 1/2 machines get local inference: Ollama adapter, automated installer, and provider status surfaced.

**Deliverables:** local Ollama provider adapter; automated Ollama installer + GPU detection hooks; system-tray provider status indicator.

**Definition of Done:**
- [ ] Phase-4 validation passes as written: on a Tier 1 machine with no Anthropic key, the app detects/installs Ollama, warms the 8B model, and answers queries locally.
- [ ] Provider selection follows §05/§12 tier rules; status indicator reflects the active provider truthfully.

---

### CH-12 — Phase 5: The Custodian App Suite

**Design sections:** §19 Data Sync · §20 Contacts/People App · §28 (deep-links) — per `../BUILD_SEQUENCING.md` §4, Phase 5.

**Goal:** First external data: Google OAuth, contacts + calendar sync mirrors, the people tools, and deep-link navigation.

**Deliverables:** OAuth 2.0 system-browser flow + keyring token storage (§19); `contacts_db`, Google Contacts sync, CSV/vCard importers (§20); `people_search` and `person_detail` tools (§20); `calendar_db` + Google Calendar sync; Chat deep-link navigation and element highlighting (§28).

**Definition of Done:**
- [ ] Phase-5 validation passes as written: test Google account syncs contacts and calendar; naming a contact in a query triggers §14 context-block injection.
- [ ] Import paths (CSV/vCard) round-trip correctly; both people tools work end-to-end through the artifact lane with narratives.
- [ ] Read-only boundary audited: no write scope requested from Google.

---

### CH-13 — Phase 6: Calendar App Integration

**Design sections:** §21 Calendar App (amended 2026-07-27) · §26/§28 (calendar screen) — per `../BUILD_SEQUENCING.md` §4, Phase 6, and `../specs/calendar-app.spec.md`.

**Goal:** Lilith's own calendar on top of the sync mirror: two event stores, echo detection, scoped tools, the ICS feed, and the calendar screen.

**Deliverables:** `synced_events` mirror (+ `echo_of_lilith_event_id`) and `lilith_events` with UID/SEQUENCE/STATUS semantics; L1 echo-detection + conflict-flagging job; template L2 agenda summaries; `agenda`/`event_lookup` and `calendar_event_create`/`update`/`cancel` tools with their §21 guardrails; local read-only ICS feed (unguessable token, loopback default); `"calendar"` screen.

**Definition of Done:**
- [ ] Phase-6 validation passes as written: external client subscribes and sees Lilith events; cancellation propagates (`STATUS:CANCELLED`, incremented `SEQUENCE`); simulated echo loop tags the echo, shows it once, flags no self-conflict.
- [ ] Audit: no Google Calendar write scope; no tool mutates the mirror; cancel never deletes.

---

### CH-14 — Phase 7: Onboarding, Extension & Final Freeze

**Design sections:** §25 Onboarding · §29 Vault & Custodian (skills enrollment) · §27 (full orb) — per `../BUILD_SEQUENCING.md` §4, Phase 7.

**Goal:** The finished product: guided first-run, the skills directory with its enrollment friction, the complete orb, and the v1 freeze.

**Deliverables:** PySide6 onboarding wizard (§25); `APP_INTERNAL_DIR/skills/` with SHA-256 manifest validation and CLI enrollment friction, injection cap 8192 bytes reject-never-truncate (§29); full orb state machine rendering and transition curves (§27).

**Definition of Done:**
- [ ] Phase-7 validation passes as written: clean install guides through passphrase entry, hardware detection, optional Google sign-in, and first voice conversation.
- [ ] Skills enrollment rejects tampered manifests and over-cap injections.
- [ ] Full-project scope audit: everything in `../BUILD_SEQUENCING.md` §5 (parked/post-v1) is verifiably absent; every design section either fully built or formally parked.
- [ ] v1 declared: tag, release artifacts per §07, and a closing entry in this guide.

---

## 6. Floating gate — Experiment 3: Encrypted Vector Feasibility

**Spec:** `../BUILD_SEQUENCING.md` §3, Experiment 3. Not a numbered chapter: it may run at any point, but **must pass before any embedding dependency, vector extension, or `memory_embeddings` table enters the codebase**. Until it passes, §18's v1 recall (recency + FTS5) is the only recall. Its pass/fail consequences (artifact-lane-only adoption, or the sidecar-index design session) are executed exactly as the spec states. Natural earliest slot: any time after CH-04 exists to test against.

## 7. Sprint document template

Each chapter's sprint file (`SPRINT-B<NN>-<slug>.md`) follows the format proven by the design-phase sprint (`SPRINT_DESIGN_PHASE.md`): a header (sprint ID, prerequisites, goal, agent context contract), then numbered tasks. Every task carries:

```
### [B<NN>-<TT>] <short title>
**Type:** [IMPLEMENT] | [TEST] | [AUDIT] | [REPORT]
**Law:** ../sections/sNN.html (+ others the task touches)
**Depends on:** <prior task IDs>

**What to build:** exact, specific instructions — package names,
function signatures, thresholds — drawn from the section text.
Nothing the section doesn't say.

**Docs:** the task's exact documentation contributions — which
docs/ pages it creates or updates and what they must contain
(minimum: its changelog entry). Named here so there is no guesswork
and documentation stays consistent across isolated agents. Part of
the task's acceptance: code merged without the named docs
contribution is not done.

**Acceptance criteria:** the observable condition under which this
task is done. Tests named. A reviewer can check it without asking
questions.
```

Sprint tasks end with a chapter-closing `[AUDIT]` task that walks this guide's Definition of Done checklist for the chapter, verifies every task's **Docs:** contribution landed, sweeps the `docs/architecture/` status lines to match built reality, and updates the §4 status table.

---

*BUILD-00 ends when CH-14's Definition of Done is checked. The next document to write is `SPRINT-B01-foundation.md`.*
