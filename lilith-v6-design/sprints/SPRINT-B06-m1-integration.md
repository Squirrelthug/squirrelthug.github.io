# SPRINT-B06 — Milestone 1 Integration & Dogfood

**Sprint ID:** BUILD-06  
**Chapter:** CH-06, `BUILD_GUIDE.md` §5. **Status:** DRAFT 2026-10-23 for coordinator review. BD-031 was decided 2026-10-23 as AD-039 by the manager under the developer's standing autonomous-decisions directive (`docs/decisions/AUTONOMOUS-DECISIONS.md` in the build repo).  
**Prerequisites:** CH-01 through CH-05 are built and audited. CH-05 leaves the real microphone/speaker, real display/GL, real BYOK, and POSIX runs as `pending developer run` (`docs/audits/CH-05.md` §8).  
**Law for this sprint:** `BUILD_GUIDE.md` §2–§3 and §5 CH-06; `BUILD_SEQUENCING.md` §2–§2.1; §§04–06, §§08–15, §18, §§22–24, §§26–28; `standards.html`.

## Open decisions

| Brief | Decision required | Blocks |
|:--|:--|:--|
| BD-031 | The law requires “a written dogfood setup note” (`BUILD_GUIDE.md` §5 CH-06) but names no documentation page. Choose its home: a new `docs/runbook/dogfood.md`, or an addition to the existing start/stop runbook. | B06-05 |

## Goal

Close only real integration gaps so the M1 objective works: “Mic → VAD → STT → LLM → TTS → Speaker,” exactly one SQLCipher `conversation_db`, and exactly one `recall_memory` FTS5 tool (`BUILD_SEQUENCING.md` §2). A dictated note must later be recallable by voice and spoken aloud. No feature beyond the M1 table enters this sprint.

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-06)

- [ ] The `BUILD_SEQUENCING.md` §2 objective demonstrably works: dictate a note by voice; later ask *"what did I say about …"* by voice; Lilith routes, recalls via FTS5, and answers aloud.
- [ ] Exactly one database (`conversation_db`) and exactly one tool (`recall_memory`) exist.
- [ ] Full-system scope audit against the M1 table: every REQUIRED row's scope note satisfied; every EXCLUDED row still absent.
- [ ] Telemetry events flow to the dev log (`APP_INTERNAL_DIR/logs/dev.log`) as the M1 stand-in for `ucl_db`.
- [ ] The developer has actually used it for at least one real dictate-and-recall session. Dogfooding starts now and continues through all later chapters.

## Context every agent must have

Read `standards.html`, the pages on the task’s **Law** line, this sprint, and `BUILD_GUIDE.md` §2–§3. Excluded means absent: no `ucl_db`, L1/L2, vectors/`memory_db`, sync, contacts, calendar, onboarding, vault/skills, a second database, or a second tool. Tests follow §08: unit tests are isolated; integration tests use real SQLCipher and substituted audio/LLM where allowed. A microphone, speakers, display/GL, model weights, or live API key is always `pending developer run`, never faked.

### [B06-01] Route completed STT transcripts into the existing conversation path
**Type:** [IMPLEMENT]  
**Law:** `s10.html` (`Speech Pipeline Architecture:`, `Output Structure:`), `s13.html` (`Artifact sequence:`), `s26.html` (`UICommandBus:`), `BUILD_GUIDE.md` §5 CH-06.  
**Depends on:** CH-05

**What to build:** Replace the startup pipeline’s discarded transcript callback with a composition-root handoff to the backend-owned `Conversation.respond`; preserve the existing queued bus-only widget rule. Render dictated user/reply text through the existing chat seam, and use the router unchanged so a voice recall query reaches `recall_memory`. Do not add a classifier, tool, database, or UI feature.

**Docs:** changelog B06-01; update the conversational/artifact and voice-pipeline data-flow pages to show STT → backend → existing UI bus.

**Acceptance criteria:** an integration test with substituted capture/VAD/STT emits a dictated note then a voice recall question; it proves persisted turns/FTS5 recall and the artifact narrative route. Unit test covers callback scheduling/error-safe release. No direct worker-thread widget call; real mic run is `pending developer run`.

### [B06-02] Speak voice-originated conversational and recall streams
**Type:** [IMPLEMENT]  
**Law:** `s11.html` (`Playback:`, `Cloud-path input gate (Fool's NC-4):`), `s13.html` (`Artifact sequence:`: acknowledge “<200 ms”, bridge “8 s”), `s14.html` (`Reverse-Substitution Pass:`), `BUILD_SEQUENCING.md` §2 and §2.1 rows §§11, 14, 24.  
**Depends on:** B06-01

**What to build:** At the composition root, feed the already reverse-substituted response stream into the existing TTS sentence/chunk queue and playback pipeline, while retaining GUI streaming. Preserve recall acknowledge/handoff order; do not speak raw tags or bypass the §14 stream filter. Measure/record the existing law values — `<=200 ms` acknowledge and `8 s` bridge — only where the implemented artifact path supports them; report a discovered gap rather than inventing timers.

**Docs:** changelog B06-02; update voice-pipeline and artifact-flow pages with the TTS attachment and PII boundary.

**Acceptance criteria:** substituted TTS/playback integration test proves conversational chunks and recalled text enter the playback queue after reverse substitution, and that recall order is acknowledge then handoff. Unit test proves no text reaches TTS before the filter. Real speaker audibility is `pending developer run`.

### [B06-03] Full offscreen walking-skeleton integration test
**Type:** [TEST]  
**Law:** `s08.html` (`Test Layout Directory Mirroring:`, `No-DB-Mocking Policy:`, `LLM Testing Integration:`, `UCL Telemetry Assertions:`), `BUILD_GUIDE.md` §5 CH-06 DoD 1 and 4.  
**Depends on:** B06-02

**What to build:** Add one offscreen integration test using a real temporary SQLCipher `conversation_db`, substituted deterministic audio components and canned/MockTransport LLM where §08 permits. Exercise Mic fixture → VAD fixture → STT fixture → router → CWM/tokenization → LLM or `recall_memory` → TTS fixture → speaker queue for dictate then voice recall. Assert dot-namespaced events and JSON lines in `APP_INTERNAL_DIR/logs/dev.log`; payloads contain no dictated text, key, or raw PII.

**Docs:** changelog B06-03; update `tests/README.md` with the offscreen command and the developer hardware batch.

**Acceptance criteria:** integration sweep proves the complete two-turn route, real FTS5 lookup, exactly one DB/tool guards, tokenized outbound conversational fixture, and dev-log output. The test is an integration test; the component callback/queue tests are unit tests. Real hardware and a live API are `pending developer run`.

### [B06-04] M1 scope and telemetry audit
**Type:** [AUDIT]  
**Law:** `BUILD_SEQUENCING.md` §2.1 (every REQUIRED and EXCLUDED row), `s04.html` (`platform/paths.py Responsibility:`), `s16.html` (`Event namespaces:`, `Payload Content Boundary:`), `BUILD_GUIDE.md` §5 CH-06 DoD 2–4.  
**Depends on:** B06-03

**What to build:** Audit every §2.1 REQUIRED scope note and every EXCLUDED row with repository commands and results. Confirm `conversation_db` is the sole mounted DB and `recall_memory` the sole shipped tool. Trace a successful end-to-end run’s events to `APP_INTERNAL_DIR/logs/dev.log`, which is the explicit M1 `ucl_db` stand-in. List gaps as follow-up tasks; do not close them by adding scope.

**Docs:** `docs/audits/CH-06.md` working evidence section; changelog B06-04.

**Acceptance criteria:** audit table has every table row, its scope/exclusion evidence, one DB/tool evidence, and dev-log JSONL evidence. No EXCLUDED implementation is credited.

### [B06-05] Publish developer dogfood setup and runbook
**Type:** [REPORT]  
**Law:** `BUILD_GUIDE.md` §5 CH-06 (deliverable and DoD 5), `BUILD_SEQUENCING.md` §2 (`Developer Daily Use Case`), `s05.html` (`Hardware Tier Definitions:`), `s06.html` (`Ten-Phase Startup Sequence (Launch to Audio Ready):`, `Graceful Shutdown Sequence:`), `s08.html` (`Test Layout Directory Mirroring:`).  
**Depends on:** B06-04, BD-031

**What to build:** Write the chosen docs page with bootstrapping, model/API-key prerequisites, launch/stop, one dictated-note and one later voice-recall procedure, expected GUI/audio/log evidence, and a dated developer checklist. Distinguish deterministic/offscreen proof from real microphone, speaker, display, Tier/hardware, and real API runs. The developer must execute and record at least one genuine session; do not fabricate it.

**Docs:** the BD-031-selected dogfood page and changelog B06-05.

**Acceptance criteria:** setup note lets the developer perform the exact M1 daily use case and has an explicit `pending developer run` record until a real session is supplied.

### [B06-06] Chapter close — CH-06 audit
**Type:** [AUDIT]  
**Law:** `BUILD_GUIDE.md` §5 CH-06 Definition of Done; `BUILD_GUIDE.md` §7 (chapter-closing audit); `BUILD_SEQUENCING.md` §2.1.  
**Depends on:** B06-05

**What to build:** Walk every CH-06 checkbox in `docs/audits/CH-06.md`; preserve hardware/API dogfood as `pending developer run`; verify all B06 Docs contributions, architecture status lines, and coordinator-only guide/Kanban close action.

**Docs:** `docs/audits/CH-06.md`, changelog B06-06, docs index/status-line updates.

**Acceptance criteria:** audit has command evidence, scope inventory, carryovers, exact developer commands, and the coordinator close action; no pending real-world claim is marked met.

## Sequential order

```text
B06-01 (STT handoff) -> B06-02 (TTS attachment) -> B06-03 (offscreen E2E) -> B06-04 (scope/log audit) -> B06-05 (dogfood note) -> B06-06 (close)
```
