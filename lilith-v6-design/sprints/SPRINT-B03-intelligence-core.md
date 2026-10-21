# SPRINT-B03 — Intelligence Core

**Sprint ID:** BUILD-03
**Chapter:** CH-03 (see `BUILD_GUIDE.md` §5) · **Kanban:** Issue #3 on Project 46 — Lilith v6 Build
**Status:** Drafted and reviewed 2026-10-20. BD-009…BD-011 resolved by the manager under the developer's standing autonomous-decisions directive (AD-006…AD-008); build proceeds on this text pending the developer's review of this PR.
**Law for this sprint:** §12, §23, §14, §13 (+ §02 credentials / cloud-data boundary, §06 lifecycle ownership, §08 testing conventions, and `standards.html`) — `../sections/s12.html`, `s23.html`, `s14.html`, `s13.html`, `s02.html`, `s06.html`, `s08.html`, and `../standards.html`.
**Prerequisites:** CH-01 is built and audited (`docs/audits/CH-01.md`). CH-02 is built (audit `docs/audits/CH-02.md`; live mic/speaker boxes pending the developer's run); B03 stacks on the CH-02 branch, but this sprint’s required text-only end-to-end test does not require microphone, speaker, model weights, or a live provider call. CH-01’s POSIX/Master fresh-clone closure remains pending. On Windows, `signal.pause()` in `lilith/app.py` is still not a usable Phase-10 wait primitive; do not change it in CH-03 (CH-05 replaces that loop with the PySide6 event loop).

## Open decisions blocking this sprint

| Brief | Decision | Blocks | Status |
|:--|:--|:--|:--|
| BD-009 | Placement and public types for the §12 Anthropic adapter, because §01’s package tree contains `logic/router.py` and `logic/cwm.py` but no provider module; choose a narrow placement that preserves `ui → logic → data → platform` and gives `app.py` a testable text-only composition seam. | B03-01, B03-07 | Resolved 2026-10-20: build-repo `docs/decisions/AUTONOMOUS-DECISIONS.md` AD-006 |
| BD-010 | Concrete, rule-based person-name detector implementation for §14’s best-effort name class. Emails and phones use deterministic patterns; the law names no PII package or name-rule corpus/library. Decide whether the detector is dependency-free or name the law-compatible package, its licence check, and its `pyproject.toml` / uv-compiled `requirements.txt` update. | B03-04 | Resolved 2026-10-20: build-repo `docs/decisions/AUTONOMOUS-DECISIONS.md` AD-007 |
| BD-011 | Exact tokenizer/counting implementation for the §14 `<=1200` volatile-context cap and the unit-test fixture shape for canned Anthropic streaming payloads. The law fixes the cap and canned-fixture testing, but names neither tokenizer nor fixture schema filename. | B03-03, B03-05, B03-07 | Resolved 2026-10-20: build-repo `docs/decisions/AUTONOMOUS-DECISIONS.md` AD-008 |

## Goal

A typed string goes in; a routed, personality-carrying, PII-protected Claude response streams out. Text-only — voice and GUI attach later. At sprint end, the provider adapter uses the existing OS-keyring `anthropic_api_key`, EDICTS and VOICE form the stable cached system prefix, CWM supplies only the CH-03 identity and recent-history surface, cloud payloads substitute the three §14 PII classes, response deltas reverse-substitute before downstream consumers, and the deterministic router selects conversational or artifact mode without implementing tools or an artifact lifecycle.

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-03)

- [ ] Typed input → router decision → CWM-assembled context → streamed Claude reply, end to end.
- [ ] Against a mocked LLM endpoint: no detectable name, email, or phone number appears in any outbound payload; tags map back correctly in responses, including the partial-tag hold and unmapped-tag placeholder paths.
- [ ] Router unit tests demonstrate both routes firing on representative inputs (formal accuracy measurement is CH-08's job, not this one).
- [ ] Prompt caching parameters verified active on the stable system blocks.

---

## Context every agent must have

Each task below is worked by its own isolated agent. An agent receives, at minimum (`BUILD_GUIDE.md` §3):

1. `../standards.html` — read first; every task’s Docs contribution is part of done.
2. The section pages named in its **Law:** line — the frozen law. If task text conflicts with a section, the section wins. A genuine gap stops that task for a documented decision; it does not authorize architecture invention.
3. This header and the task’s own block.

**Ground rules (from `BUILD_GUIDE.md` §2):** only what is written gets built; standards are the floor; excluded means absent; and validation gates are hard gates. For CH-03 this means no Ollama fallback/installer/UI indicator (CH-11/CH-05), no tools or artifact execution (CH-04), no §14 task-owned snapshots/re-lock cancellation/recall-corpus CI gate (CH-10), no §17 refresh or L1/L2 enhancement, and no router dry-run harness (CH-08).

Testing follows §08: default unit tests use canned JSON fixtures matching the provider payload schema and do not call the network; the mocked-endpoint tests are unit tests. A developer may separately run a live Anthropic BYOK smoke call with the key held only in the OS keyring; it is never a default test and is recorded as `pending developer run` at chapter close.

---

### [B03-01] Anthropic BYOK streaming provider adapter
**Type:** [IMPLEMENT]
**Law:** `../sections/s12.html` (`Adapter contract:`, `Anthropic primary:`, `Provider selection:`, `Budgets:`, `Context safety:`, `Telemetry:`), `../sections/s02.html` (`Stored Credentials List & Key Names (Canonical Table):`, `Data Hygiene (SEC-018, Normative):`), `../sections/s08.html` (`LLM Testing Integration:`, `UCL Telemetry Assertions:`), `../standards.html` (dependency and telemetry rules)
**Depends on:** BD-009

**What to build:**
- Add the law-pinned dependency `anthropic==0.112.0` in the placement resolved by BD-009. Perform the licence check required by `standards.html`; under ADR B-002, update `pyproject.toml` and regenerate the uv-compiled `requirements.txt`. Do not add LiteLLM, `openai`, or an Ollama dependency in this chapter.
- Implement the §12 provider contract exactly: `complete(messages: list[dict], system: list[dict], stream: bool = True) -> AsyncIterator[str]`, using Anthropic model `claude-sonnet-4-6`, streaming text deltas, and the existing `lilith.platform.keyring.ANTHROPIC_API_KEY` under service `com.squirrelthug.lilith`.
- Accept only CWM-approved messages/system blocks at this boundary; raw DB rows never reach `complete()`. Apply `cache_control={"type":"ephemeral"}` only to stable EDICTS and VOICE prefix blocks supplied by B03-02, never to volatile context.
- Emit `llm.call.start` with `provider`, `model`, `mode` and `llm.call.complete` with `tokens_in`, `tokens_out`, `latency_ms`, `success`; declare the payload fields before implementation. No event payload or plaintext log includes key material, prompt text, or response text.
- Unit-test the adapter with canned JSON fixtures matching Anthropic’s exact streaming payload schema; no default test may call the network. Add an opt-in developer BYOK smoke-test command/documentation only if it reads the key through the OS keyring, never an environment variable.

**Docs:** Add the `B03-01` entry under `### CH-03 — Intelligence Core` in `docs/CHANGELOG.md`; create/update `docs/architecture/components/llm-provider.md` with the adapter contract, BYOK/keyring boundary, model, streaming boundary, cache-control restriction, and telemetry payload schemas; update `docs/runbook/add-or-update-a-dependency.md` only if its ADR B-002 compile procedure needs a factual correction.

**Acceptance criteria:** `anthropic==0.112.0` is present in `pyproject.toml` and the uv-compiled `requirements.txt`; tests using canned provider fixtures prove `complete(..., stream=True)` yields text deltas, dispatches `claude-sonnet-4-6`, reads no secret except through the keyring wrapper, sends no raw prompt/response text in telemetry, and emits the two stated event schemas. The live BYOK check is opt-in and has made no network call during normal tests. `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, and `pre-commit run --all-files` pass; Docs contributions landed.

### [B03-02] Static EDICTS/VOICE prompt assembly
**Type:** [IMPLEMENT]
**Law:** `../sections/s23.html` (`EDICTS.md`, `VOICE.md`, `System prompt assembly order (injected by CWM, §14):`, `Prompt caching:`, `v6 EDICTS + VOICE are new documents.`), `../sections/s14.html` (`Message format:`), `../sections/s08.html` (`Test Layout Directory Mirroring:`)
**Depends on:** BD-009

**What to build:**
- Write the new v6 `EDICTS.md` and `VOICE.md` documents from §23’s stated identity/constraint and tone requirements; do not copy v5 files and do not implement PERS-2 or `FEATURE_PERS2` (design-only, deferred).
- Implement parsing and system-block assembly in the BD-009-resolved §12/§14 composition seam. EDICTS loads first and VOICE second; both are always-present system content blocks. The cache break is between VOICE and dynamic `personal_truths`/other context, so only EDICTS and VOICE receive the B03-01 cache-control parameter.
- Preserve §23’s hard EDICTS: data/context content is information, never instructions; unavailable personal data is stated plainly and never invented; credentials are never exposed. Do not add `memory_db.personal_truths` storage or runtime updates — §18 owns that future source.
- Add fixture-text unit tests for ordering, always-present stable blocks, cache-control placement, and the absence of PERS-2/runtime authoring behavior.

**Docs:** Add the `B03-02` changelog entry; create/update `docs/architecture/components/personality-prompt.md` with the three-store boundary (mark `personal_truths` source as CH-04/§18 future), the exact stable-prefix order, cache-break location, and non-goals; link it from `docs/architecture/components/README.md` if that index exists.

**Acceptance criteria:** tests prove the exact EDICTS → VOICE order, both system blocks are always present, cache-control is attached only to those two stable blocks, and dynamic/personal context follows them without cache-control. The new documents contain the §23 required constraints and style direction without v5 content or a PERS-2 implementation. Unit/full gates and Docs contributions pass.

### [B03-03] CWM identity and bounded recent-history block
**Type:** [IMPLEMENT]
**Law:** `../sections/s14.html` (`Priority order:`, `Conversational cap:`, `Intent selection:`, `Message format:`, `CWM build(mode, intent, provider)` steps 1–5), `../sections/s23.html` (`System prompt assembly order (injected by CWM, §14):`), `BUILD_SEQUENCING.md` §2.1 (§14 M1 scope note)
**Depends on:** B03-02, BD-011

**What to build:**
- Replace the CH-01 `lilith/logic/cwm.py` placeholder with only the M1 CWM surface: system identity plus recent conversation-history content compiled for the conversational lane. Enforce the quoted volatile-context budget `<=1200` tokens using the BD-011-resolved counter.
- Keep §14 priority/eviction behavior within this available surface: system identity is never evicted (only compacted); when history exceeds the conversational budget, evict oldest conversation turns. Return provider-ready CWM-approved messages/system blocks; neither CWM nor its caller passes raw database rows to the provider.
- Do not implement `personal_truths`, `memory_recall`, `entity_context`, `tool_context`, freshness thresholds, §17 refresh, or absence disclosures: their data/enhancement sources are outside CH-03’s M1 scope. Make their absence explicit in public types/docs rather than creating latent feature stubs.
- Add fixture-text unit tests for identity precedence, token accounting, `<=1200` enforcement, and oldest-history eviction.

**Docs:** Add the `B03-03` changelog entry; create/update `docs/architecture/components/context-window-manager.md` with the CH-03 identity/recent-history scope, cap/counter selected by BD-011, priority/eviction rule, provider-safe output boundary, and explicitly deferred §14 surfaces; update `docs/architecture/data-flows/conversational-path.md` to identify the CWM block before cloud tokenization.

**Acceptance criteria:** CWM unit tests prove only approved assembled blocks reach the provider seam, stable identity remains while excess history loses oldest turns first, and volatile context never exceeds `1200` tokens. There is no implementation of stale refresh, database recall/entity/tool context, or raw-row provider dispatch. Unit/full gates and Docs contributions pass.

### [B03-04] Cloud PII detector and session-scoped substitution map
**Type:** [IMPLEMENT]
**Law:** `../sections/s14.html` (`Cloud PII Tokenization (SEC-018 — v1 detection scope: person names, email addresses, phone numbers):` → `PII Detector (three classes, full v1 scope):`, `Substitution Pass:`, `Ephemeral Mapping Table — Session Scope (SEC-022):`), `../sections/s02.html` (`Data Hygiene (SEC-018, Normative):`), `BUILD_SEQUENCING.md` §2.1 (§14 M1 scope note)
**Depends on:** B03-03, BD-010

**What to build:**
- Implement the cloud-only, in-memory substitution pass after CWM assembly and before B03-01 dispatch. Detect exactly three v1 classes: person names (BD-010’s rule-based, best-effort solution), emails, and phones (deterministic patterns). Do not claim or implement detection of merchant names, monetary amounts, health/relationship details, free-text notes, or non-calendar location text.
- Substitute stable distinct tags exactly as §14 specifies: `<principal_user>` for the user; contacts `<contact_1>`, `<contact_2>`, …; email `<email_1>`, `<email_2>`, …; phone `<phone_1>`, `<phone_2>`, …. Mapping is local volatile session state, starts empty at unlock, has counters that only grow, maps the same value to the same tag for the unlocked session, and is dropped at app exit/re-lock. Coordinate the lifecycle hook with existing `SessionKeyManager` only to clear the session table; do not implement artifact snapshots/re-lock cancellation (CH-10).
- Add fixture-text unit tests proving no detectable name/email/phone remains in an outbound cloud payload, same-session stability, different-session reset, and the stated non-detection boundary. Tests do not call an external API.

**Docs:** Add the `B03-04` changelog entry; extend `context-window-manager.md` with all three scope classes, exact tag families, session lifetime, cloud-only placement, and the privacy claim ceiling; update `docs/architecture/data-flows/conversational-path.md` with CWM → substitution → provider and the explicit non-detection boundary.

**Acceptance criteria:** mocked-provider payload assertions show no detector-positive name, email, or phone in outbound content; session state keeps a value’s tag stable and resets after lifecycle clear; mappings are neither persisted nor emitted to telemetry. The test corpus is fixture text, not the CH-10 merge-blocking §08 recall corpus. Unit/full gates and Docs contributions pass.

### [B03-05] Streaming reverse substitution and partial-tag hold filter
**Type:** [IMPLEMENT]
**Law:** `../sections/s14.html` (`Reverse-Substitution Pass:`, `Unmapped-Tag Handling (SEC-022):`, `Streaming Reconciliation — Partial-Tag Hold Rule (Fool's NC-4):`), `../sections/s13.html` (`Tokenization latency accounting (SEC-022 / Fool's NC-4):`), `../sections/s11.html` (`Cloud-path input gate (Fool's NC-4):`), `../sections/s08.html` (`LLM Testing Integration:`)
**Depends on:** B03-01, B03-04, BD-011

**What to build:**
- Put a deterministic, single-pass O(stream length) reverse-substitution filter between the cloud response stream and every downstream consumer. It runs exactly once and yields only post-substitution text; B02’s sentence/clause chunker is downstream.
- Enforce the partial-tag hold rule exactly: after `<` starts a candidate, withhold its characters until it closes as `<(principal_user|contact_N|email_N|phone_N)>` (`N` decimal), is proven non-tag by a character outside `[a-z0-9_]`, closes without matching, exceeds 16 characters without closing, or reaches end-of-stream. Release every non-tag candidate verbatim; substitute every valid mapped tag.
- Replace unmapped tags with the required neutral text: contact → `a contact`, email → `an email address`, phone → `a phone number`, principal user → `the user`. Emit `context.token.unmapped` with only `tag`, `tag_family`, `turn_id or task_id`, and `consumer`; never release a literal unmapped tag to TTS, UI, memory, or database. Artifact snapshot/re-lock paths remain CH-10 and are absent.
- Use canned streamed-provider fixtures to unit-test tag boundaries across chunks, malformed/overlong/end-of-stream candidates, mapped tags, all unmapped placeholders, and telemetry. No network test is permitted by default.

**Docs:** Add the `B03-05` changelog entry; extend `context-window-manager.md` and `conversational-path.md` with the response-stream placement, all partial-tag resolution cases, the 16-character bound, unmapped placeholders, and the downstream-consumer guarantee.

**Acceptance criteria:** fixture-driven tests demonstrate an open tag is never released before resolution, each valid tag reverses correctly even when split across chunks, every enumerated not-a-tag case is released verbatim, and fabricated unmapped tags become the correct neutral placeholders with `context.token.unmapped` emitted. Unit/full gates and Docs contributions pass.

### [B03-06] Deterministic conversational/artifact rule router
**Type:** [IMPLEMENT]
**Law:** `../sections/s13.html` (`Classifier:`, `Conversational mode:`, `Artifact mode:`, `Latency budget stance:`), `../sections/s12.html` (`Budgets:`), `BUILD_SEQUENCING.md` §2.1 (§13 M1 scope note)
**Depends on:** B03-03

**What to build:**
- Replace the `lilith/logic/router.py` placeholder with the deterministic keyword/intent and endpoint-capability classifier: no LLM classifier. Its output selects conversational only when expected output is `<=50` tokens, no tool is required, endpoint supports voice response, and CWM fits `<=1200` context tokens; otherwise it selects artifact for the §13 stated conditions.
- Keep the router’s CH-03 artifact result as a decision only. Do not implement tools, acknowledge/bridge/handoff narratives, background tasks, skill injection, endpoint policy UI, latency bridge UI, or dry-run instrumentation; they belong to later scoped chapters/gates.
- Emit the CH-03-applicable `router.classify` event with `mode`, `reason`, `endpoint_id`, `endpoint_type`, with a declared schema and no user text. Add representative unit inputs that fire both routes; CH-08 alone measures formal accuracy and counterfactuals.

**Docs:** Add the `B03-06` changelog entry; create/update `docs/architecture/components/router.md` with the deterministic decision contract, the `50`/`1200` working hypotheses, event schema, and an explicit deferred-surface list; update `docs/architecture/data-flows/conversational-path.md` and `artifact-path.md` to show classification but mark artifact execution as CH-04 future work.

**Acceptance criteria:** router unit tests prove representative small conversational input selects conversational and tool/long/multi-source/non-inline/over-budget input selects artifact, with a reason and a schema-valid `router.classify` event. No LLM classification, tool runner, skill, UI, or CH-08 dry-run code exists. Unit/full gates and Docs contributions pass.

### [B03-07] Text-only routed streaming composition
**Type:** [IMPLEMENT]
**Law:** `BUILD_GUIDE.md` §5 (CH-03 `Goal:` and first Definition-of-Done item), `../sections/s12.html` (`Adapter contract:`, `Budgets:`, `Context safety:`), `../sections/s13.html` (`Classifier:`, `Conversational mode:`, `Tokenization latency accounting (SEC-022 / Fool's NC-4):`), `../sections/s14.html` (`CWM build(mode, intent, provider)`), `../sections/s23.html` (`System prompt assembly order (injected by CWM, §14):`), `../sections/s08.html` (`LLM Testing Integration:`)
**Depends on:** B03-01, B03-02, B03-03, B03-04, B03-05, B03-06, BD-009, BD-011

**What to build:**
- Add the smallest text-only composition seam resolved by BD-009: typed `str` input → router decision → CWM-approved system/messages → cloud substitution → Anthropic streaming adapter → reverse-substitution stream → text consumer. Artifact decisions must return the router decision without inventing an artifact executor.
- Pass conversational output cap `<=50` and volatile context cap `<=1200` as the §12/§13 working-hypothesis limits through the provider request shape selected by BD-009; do not add unspecified timeout, retry, chunk-size, or sampling values.
- Use a mocked/canned Anthropic endpoint fixture for an end-to-end unit/integration test. Assert the outbound provider payload contains no detectable PII, its stable EDICTS/VOICE blocks carry cache-control, and split response tags emerge de-tokenized to the text consumer. No default test calls Anthropic.
- Do not alter startup Phase 8/10, scheduler ownership, `signal.pause()`, Phase 9 audio wiring, or GUI wiring. Those are not CH-03 scope.

**Docs:** Add the `B03-07` changelog entry; update `docs/architecture/data-flows/conversational-path.md` with a Mermaid flowchart naming concrete router/CWM/tokenizer/provider/reverse-filter components and their text-only status; update `docs/architecture/00-system-context.md` and `docs/architecture/01-containers.md` to mark CH-03 intelligence-core components built while retaining later artifact/UI scope as future.

**Acceptance criteria:** one fixture-driven test proves typed string → conversational router decision → CWM assembly → PII-safe mocked outbound payload → streamed reverse-substituted reply; a representative artifact route stops at its decision boundary. The test has no network dependency, and no startup/audio/UI behavior changes. Unit/full gates and Docs contributions pass.

### [B03-08] Chapter close — audit, live-API handoff, documentation sweep, guide
**Type:** [AUDIT]
**Law:** CH-03 Definition of Done (`BUILD_GUIDE.md` §5), M1 scope/exclusions (`BUILD_SEQUENCING.md` §2.1), `../sections/s08.html` (`LLM Testing Integration:`, `PII Detector Recall Corpus (SEC-018, mandatory CI):`), `../standards.html` (`Documentation Standards`)
**Depends on:** B03-07

**What to build:**
1. Walk every CH-03 Definition-of-Done checkbox with commands and evidence in `docs/audits/CH-03.md`. The mocked-endpoint PII box must show no detectable name/email/phone outbound plus correct mapped, partial-tag-hold, and unmapped-placeholder results. Mark the optional real-Claude BYOK call **`pending developer run`** until the developer runs it with `anthropic_api_key` stored in the OS keyring; it is not a prerequisite for unit gates.
2. Scope-audit that the chapter includes only the §12 Anthropic BYOK adapter/caching, §23 static prompt, §14 M1 identity/recent-history plus conversational PII pass, and §13 deterministic classifier. Verify absence of §12 Ollama fallback/installer/UI indicator; §14 artifact snapshots/re-lock cancellation and recall-corpus CI gate; §15 tools; §17 enhancement/refresh; §18 schema; §22/§26 GUI; and CH-08 dry-run harness.
3. Verify every B03-01…B03-07 **Docs:** contribution landed; update all affected `docs/architecture/` status lines and `docs/README.md` with the CH-03 audit; confirm the CH-03 changelog section is complete.
4. After all DoD boxes that do not require the developer are met and the developer has recorded the optional live call if desired, update the CH-03 Kanban/checklist status and `BUILD_GUIDE.md` §4 in the design-site repository through the normal reviewed close process.
5. Carry forward CH-01’s pending POSIX/Master fresh-clone verification and the Windows `signal.pause()` limitation as open cross-chapter facts; do not claim they are fixed by CH-03.

**Docs:** `docs/audits/CH-03.md`, `docs/CHANGELOG.md` (`B03-08` entry), `docs/README.md` (Chapter audits row), and status-line updates in all CH-03-touched `docs/architecture/` component/data-flow pages.

**Acceptance criteria:** `docs/audits/CH-03.md` contains evidence for every DoD box, clearly labels a live Claude check `pending developer run` until run, records the M1 scope inventory and every Docs contribution, and preserves the CH-01 carryovers. Architecture/data-flow status lines describe built CH-03 reality; no excluded feature is credited as built.

---

## Sequential order

```text
BD-009 ──┬──> B03-01 (§12 Anthropic adapter) ───────────────────────┐
         └──> B03-02 (§23 static prompt) ─> B03-03 (§14 CWM) ──────┼──> B03-07 (text-only composition) ─> B03-08 (audit)
BD-011 ────────────────────────────────────────────────┘           │
BD-010 ─> B03-04 (§14 substitution map) ─> B03-05 (§14 stream filter) ┘
B03-03 ───────────────────────────────────────> B03-06 (§13 router) ─┘
```

- BD-009 resolves the only new-module/composition placement before adapter or final wiring begins.
- B03-01 and B03-02 may proceed after BD-009; B03-03 makes their stable prompt/CWM contract concrete.
- B03-04 and B03-05 are sequential because the stream filter consumes the session map; B03-06 is independent once CWM can report context fit.
- B03-07 is deliberately last: it proves the exact first DoD path and does not grow an artifact executor.

*When B03-08 closes, CH-03 is done. Next: author `SPRINT-B04-memory-first-tool.md` from `BUILD_GUIDE.md` CH-04 + §18/§15/§24, per the working loop.*
