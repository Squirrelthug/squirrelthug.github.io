# SPRINT-B08 — GATE: Router Dry-Run (Counterfactual)

**Sprint ID:** BUILD-08  
**Chapter:** CH-08. **Status:** DRAFT 2026-10-23 for coordinator review. BD-033 was decided 2026-10-23 as AD-039 by the manager under the developer's standing autonomous-decisions directive (`docs/decisions/AUTONOMOUS-DECISIONS.md` in the build repo).  
**Prerequisites:** CH-06; CH-07 may run in either order (`BUILD_GUIDE.md` §4). **Law:** `BUILD_SEQUENCING.md` §3, “Experiment 2: Router Dry-Run (Counterfactual Instrumentation)”; `BUILD_GUIDE.md` §2–§3 and §5 CH-08; `s08.html`, `s13.html`, `s14.html`, `s15.html`, `s16.html`; `standards.html`.

## Open decisions

| Brief | Decision required | Blocks |
|:--|:--|:--|
| BD-033 | The law requires a fixture, standalone JSONL “alongside the report,” and a report, but no paths/file names. Choose the immutable fixture, result, and report locations before B08-01 creates them. | B08-01 |

## Goal

Falsifiably measure the two-mode fork against a frozen 100-utterance set. The deterministic fixture/hash, router decision, mechanical verdict derivation, JSONL renderer, table, and rate calculation can run here. One generation per utterance needs the configured full M1 prompt/tool path and a real API for the authoritative batch; a deterministic endpoint is permitted only to validate the harness, not to claim the gate.

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-08)

- [ ] Set frozen and hashed before tuning; procedure, mechanical verdicts, and telemetry events per spec; ≤5 `error` verdicts.
- [ ] Rates reported against the pre-committed gates (`total > 10%` or `misroute_to_conversational > 5%`).
- [ ] **Below thresholds:** two-mode confirmed for v1; fork closed; recorded here. **Above either:** the stream-and-cut single-path design session is scheduled and held *before* CH-09 begins — the triggered review cannot be retroactively cancelled by re-runs.

## Context every agent must have

Read `standards.html`, Law pages, this sprint, and `BUILD_GUIDE.md` §2–§3. Assemble and SHA-256-freeze the set before any rule is tuned against its results. Author labels are diagnostics only; generation-derived fields determine verdicts. During M1 emit JSON-line `router.dryrun.utterance` and `router.dryrun.summary` to the standard dev log because `ucl_db` is deferred (`BUILD_SEQUENCING.md` §3 Experiment 2).

### [B08-01] Author, freeze, and precommit the 100-utterance dataset
**Type:** [IMPLEMENT]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 2 (`Utterance Set`); `s13.html` (`Milestone-1 counterfactual dry-run instrumentation`).  
**Depends on:** CH-06, BD-033

**What to build:** Author exactly 100 realistic developer utterances around the specified 50/50 conversational/artifact stratification guide, including: conversational-form/long-answer photosynthesis; tool-needed wording without tool keywords; short factual questions; dictation/note-taking turns; and `recall_memory` queries. Store diagnostic authored labels, calculate SHA-256, and record it in the report before router-rule tuning. Treat the fixture as immutable thereafter.

**Docs:** fixture/hash record, changelog B08-01, and `tests/README.md` freeze/verify command.

**Acceptance criteria:** reviewer can recompute the SHA-256, count 100, locate every required boundary category, and see timestamp/order evidence that the hash precedes tuning.

### [B08-02] Implement deterministic dry-run collection and verdicting
**Type:** [IMPLEMENT]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 2 (`Procedure`, steps 1–4); `s13.html` (`Pre-committed misroute threshold (quality gate; committed 2026-07-12, before any dry-run data exists):`, `Telemetry:`); `s16.html` (`Event namespaces:`, `Payload Content Boundary:`).  
**Depends on:** B08-01

**What to build:** For each utterance: record router `conversational|artifact` and fired rule; run exactly one full-M1-path generation with `max_tokens >=1024`, `temperature 0`, `recall_memory` available, and no `50`-token cap; record provider `output_tokens`, `tool_call_emitted`, and `cap_truncates_mid_sentence`. The latter is true only when `output_tokens >50` and the stripped decoded 50-token prefix lacks `.`, `!`, or `?`, optionally followed by closing quote/parenthesis; false when `<=50`. Derive `needed_artifact := tool_call_emitted OR output_tokens >50` and the four specified verdicts mechanically. Retry one generation error once; persistent failure is `error`, remains in N, and `>5` invalidates the run.

**Docs:** changelog B08-02; harness format documentation.

**Acceptance criteria:** unit tests cover all four verdict rows, punctuation edge, retry/error denominator, and invalidation at six errors. Deterministic fake-provider test validates collection only; it is not a gate result.

### [B08-03] Emit JSONL, telemetry, findings table, and rates
**Type:** [REPORT]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 2 (`Procedure` step 4, `Metric`, `Report Artifact`); `s13.html` (`Telemetry`).  
**Depends on:** B08-02

**What to build:** Write standalone JSONL alongside the report and one dev-log `router.dryrun.utterance` event per turn with `utterance_id, mode, rule, output_tokens, tool_call_emitted, cap_truncates_mid_sentence, verdict`; write one summary event with `set_sha256, n, misroute_to_artifact_rate, misroute_to_conversational_rate, total_misroute_rate, threshold_crossed`. Render the required per-utterance table and compute all rates with full frozen `N` (nominally 100), including errors.

**Docs:** report artifact and changelog B08-03.

**Acceptance criteria:** JSONL/table/event schema are mutually reconcilable; results prove the three formulas and preserve SHA-256. No utterance text/PII is put in telemetry beyond approved identifiers.

### [B08-04] Execute authoritative first complete batch and enforce the gate
**Type:** [TEST]  
**Law:** `BUILD_SEQUENCING.md` §3 Experiment 2 (`Pre-Committed Threshold`, `Report Artifact`); `BUILD_GUIDE.md` §5 CH-08.  
**Depends on:** B08-03

**What to build:** Run once against the frozen set on the configured real M1 prompt path/API and produce the report. The gates are strictly `total_misroute_rate >10%` or `misroute_to_conversational_rate >5%`; equality does not cross them. Below both, confirm two-mode for v1 and proceed to dogfood numeric hypotheses. Above either, schedule and hold the stream-and-cut single-path design session before CH-09; tuning/re-runs cannot cancel that triggered review. This external/API run is `pending developer-batch` here.

**Docs:** completed report/consequence record and changelog B08-04; otherwise exact pending batch command.

**Acceptance criteria:** first complete frozen-set result identifies below/above gates, errors `<=5`, and reports no false go/no-go based on a mock.

### [B08-05] Gate close audit
**Type:** [AUDIT]  
**Law:** `BUILD_GUIDE.md` §5 CH-08 DoD; `BUILD_GUIDE.md` §7; `BUILD_SEQUENCING.md` §3 Experiment 2.  
**Depends on:** B08-04

**What to build:** Audit fixture freezing order/hash, 100-set composition, raw JSONL, mechanical fields/verdicts, event names, table, error count, all three rates, thresholds, consequence, Docs contributions, and developer-batch status. CH-09 cannot start until this and Experiment 1 resolve.

**Docs:** `docs/audits/CH-08.md`, changelog B08-05, status-line updates.

**Acceptance criteria:** a reviewer can independently recompute every verdict/rate and sees either the confirmed fork or evidence that the mandatory design session occurred before CH-09.

## Sequential order

```text
BD-033 -> B08-01 (freeze/hash) -> B08-02 (harness/verdicts) -> B08-03 (JSONL/report) -> B08-04 (first batch/consequence) -> B08-05 (audit)
```
