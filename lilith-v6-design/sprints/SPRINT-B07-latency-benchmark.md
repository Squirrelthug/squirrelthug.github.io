# SPRINT-B07 — GATE: Walking-Skeleton Latency Benchmark

**Sprint ID:** BUILD-07  
**Chapter:** CH-07. **Status:** DRAFT 2026-10-23 for coordinator review. BD-032 was decided 2026-10-23 as AD-038 by the manager under the developer's standing autonomous-decisions directive (`docs/decisions/AUTONOMOUS-DECISIONS.md` in the build repo).  
**Prerequisites:** CH-06 closed or its developer batch explicitly pending. **Law:** `BUILD_SEQUENCING.md` §3, “Experiment 1: Walking-Skeleton Latency Benchmark”; `BUILD_GUIDE.md` §2–§3 and §5 CH-07; `s05.html`, `s08.html`, `s11.html`, `s13.html`, `s14.html`, `s16.html`; `standards.html`.

## Open decisions

| Brief | Decision required | Blocks |
|:--|:--|:--|
| BD-032 | Experiment 1 names a “test script” and “written report artifact” but no repository paths or simulated-network mechanism. Choose report/fixture/harness paths under the build repo and an allowed reproducible network simulation; Tier 0 real-network execution remains the authority. | B07-01, B07-03 |

## Goal

Run the frozen Experiment 1 exactly: 50 typical voice queries twice, from VAD voice offset to first synthesized audio chunk, with §14 tokenization enabled and disabled. The enabled p90 bar is “under 3.5 seconds”; the §13 working target is “<=3 s”; record p50/p90 on/off deltas with no independent delta bar (`BUILD_SEQUENCING.md` §3, Experiment 1).

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-07)

- [ ] Both runs executed per the spec's procedure, query set meeting its PII/echo-back requirements.
- [ ] Report records p90 (tokenization enabled) against the 3.5 s bar, both deltas, and the verdict.
- [ ] **Pass:** gate closed, result logged here. **Fail:** the spec's fallback ladder is followed in order (detector optimization → stream-and-cut → soft token cap), each step documented, before this gate may close.

## Context every agent must have

Read `standards.html`, the Law pages, this sprint, and `BUILD_GUIDE.md` §2–§3. This is a gate, not permission for new features. The harness and dry validation can run on Windows using substituted audio and a mocked endpoint; the authoritative two 50-query measurements need the developer’s Tier 0 hardware, voice/TTS model assets, simulated average network connection, and real cloud API key, and are `pending developer-batch` until performed.

### [B07-01] Build the reproducible latency harness and query fixture
**Type:** [IMPLEMENT]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 1 (`Procedure`, `Pass Criteria`); `s13.html` (`Tokenization latency accounting`); `s14.html` (substitution/reverse-substitution and partial-tag hold); `s08.html` (test conventions).  
**Depends on:** CH-06, BD-032

**What to build:** Create the chosen harness/fixture. It executes exactly 50 typical voice queries per run and timestamps VAD voice offset through the first synthesized audio chunk. Supply two complete configurations: §14 tokenization shipping-enabled and disabled. Fixture context must contain detectable names, emails, and phone numbers; expected replies must echo tags, including a partial-tag-hold exercise. Persist per-query enabled/off timings and enough non-secret run metadata to reproduce results; never log PII.

**Docs:** changelog B07-01; `tests/README.md` exact dry-validation and developer-batch commands; chosen artifact README/location.

**Acceptance criteria:** dry validation on this Windows machine runs both modes against substituted audio/LLM and proves 50 records/mode, timer boundaries, PII-tag/reverse-substitution/hold coverage, and no live network. It is validation only, not a Tier 0 verdict.

### [B07-02] Calculate statistics and render the benchmark report
**Type:** [REPORT]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 1 (`Procedure`, `Pass Criteria`); `BUILD_GUIDE.md` §5 CH-07.  
**Depends on:** B07-01

**What to build:** Generate the report artifact from raw per-query data: each timing, enabled p50/p90, disabled p50/p90, `tokenization_delta_p50`, `tokenization_delta_p90`, enabled p90 versus the “under 3.5 seconds” gate, and pass/fail verdict. State that the “<=3 s” figure is a §13 working hypothesis, not this experiment’s pass threshold. Quote all values with their locations.

**Docs:** report artifact and changelog B07-02.

**Acceptance criteria:** deterministic fixture results yield reproducible statistics; report refuses an incomplete/other-than-50-query mode as a gate verdict.

### [B07-03] Developer Tier 0 benchmark batch
**Type:** [TEST]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 1 (`Assumption Tested`, `Procedure`, `Pass Criteria`).  
**Depends on:** B07-02

**What to build:** Execute both full runs on developer Tier 0 hardware with CPU VAD/STT/TTS, cloud LLM, simulated average network, real API credential, and the real pipeline. Preserve raw records and render the report. This task is `pending developer-batch` on this desktop; no mocked endpoint result can be substituted for the verdict.

**Docs:** completed report artifact and changelog B07-03; otherwise the pending checklist/command.

**Acceptance criteria:** exactly two 50-query runs; enabled p90 is compared to `<3.5 s`; both deltas are reported. `p90 < 3.5 s` passes; otherwise B07-04 is mandatory.

### [B07-04] Conditional fallback ladder on enabled-run failure
**Type:** [IMPLEMENT]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 1 (`Architectural Fallback`); `s13.html` (`Named fallback`).  
**Depends on:** B07-03

**What to build:** Only if enabled p90 exceeds `3.5 s`: first inspect recorded on/off delta; if it accounts for the overrun, optimize the §14 detector/scanner while retaining single-pass O(context length). Then replace pre-classification blocking flow with stream-and-cut. Then implement the soft token cap that lets Claude finish a sentence instead of hard truncating at `50` tokens. Document and remeasure every ordered step; do not skip/reorder it or declare the gate closed early.

**Docs:** fallback evidence/report updates and changelog B07-04.

**Acceptance criteria:** conditional task either records “not triggered” with source report evidence, or has evidence for every ordered action and rerun before gate close.

### [B07-05] Gate close audit
**Type:** [AUDIT]  
**Law:** `BUILD_GUIDE.md` §5 CH-07 DoD; `BUILD_GUIDE.md` §7; `BUILD_SEQUENCING.md` §3 Experiment 1.  
**Depends on:** B07-03, B07-04

**What to build:** Verify query count, PII/echo-back coverage, raw timings, statistics, p90 verdict, fallback status, Docs contributions, and all pending developer-batch facts. Update coordinator-only chapter status only after valid pass or fully documented fallback.

**Docs:** `docs/audits/CH-07.md`, changelog B07-05, architecture/status-line updates.

**Acceptance criteria:** audit makes the gate result independently checkable and never treats the Windows mock dry run as the Tier 0 result.

## Sequential order

```text
BD-032 -> B07-01 (harness/fixture) -> B07-02 (statistics/report) -> B07-03 (Tier 0 batch) -> B07-04 (only on failure) -> B07-05 (audit)
```
