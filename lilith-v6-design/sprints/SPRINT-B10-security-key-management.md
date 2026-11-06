# SPRINT-B10 — Security & Key Management

**Sprint ID:** BUILD-10  
**Chapter:** CH-10. **Status:** DRAFT 2026-10-26 for coordinator review.  
**Prerequisites:** CH-01 through CH-09 are built and audited; the CH-08 hybrid-router gate passed. **Law:** `BUILD_GUIDE.md` §2-§3 and §5 CH-10; `BUILD_SEQUENCING.md` §4, `Phase 3: Security & Key Management Expansion`; `s02.html`, `s03.html`, `s06.html`, `s08.html`, `s14.html`, `s16.html`, `s25.html`, and `standards.html`.

## Open decisions

| Brief | Value the law leaves open; options it permits | Blocks |
|:--|:--|:--|
| BD-044 | `rotation.journal` must record a staging-directory name, per-database staging progress, and a phase, but the JSON representation is not prescribed. Choose a per-file object keyed by logical database name, or an ordered list carrying database-name records; either must support idempotent resume and contain no secrets. | B10-01, B10-02 |
| BD-045 | The rotation preflight requires free space of the combined live-database size plus 20%, but does not prescribe whether sidecar files are counted. Choose database main files only, or main files plus existing WAL/SHM sidecars; either measurement must retain the stated 20% margin. | B10-01 |
| BD-046 | The law requires an in-flight artifact task to be cancelled at relock and its late response discarded, but does not prescribe the cancellation primitive. Choose a task-registry cancellation token, or cancellation of a registered async task/future; either must clear every snapshot before return from relock. | B10-03, B10-04 |
| BD-047 | The recall corpus fixes annotated positive spans and recall thresholds, but not the span-match rule. Choose exact normalized span matching, or a documented overlap rule; it must calculate each class only over its annotated positive spans and preserve the stated thresholds. | B10-06 |

## Goal

Complete the credential lifecycle and the deliberately deferred §14 PII lifecycle surface: crash-resumable passphrase rotation, explicit relock/unlock control, task-owned artifact mapping snapshots that fail closed at relock, UCL-backed unmapped-tag telemetry, and the §08 merge gate for detector recall. This sprint creates no onboarding flow, new tool, local provider, external sync, or database-mocking test path.

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-10)

- [ ] Phase-3 validation passes as written: mocked endpoint shows no PII outbound; correct tag mapping including the unmapped-tag placeholder path; in-flight artifact task across a re-lock is cancelled fail-closed with its late response discarded.
- [ ] Recall-corpus gate is live in CI and demonstrably blocks a merge on regression.
- [ ] Passphrase rotation completes on a populated database without data loss.

The CI check above is **pending developer (Actions billing)** until Actions can run. The gate itself is a local script and a CI workflow step; no task may represent a hosted merge block as already demonstrated without the developer's Actions result.

## Context every agent must have

Read `standards.html`, the Law pages in the Law line, this sprint, and `BUILD_GUIDE.md` §2-§3. Tests use real SQLCipher databases and migrations, never database mocks. Existing seams: `lilith/data/db.py:84` currently centralizes the mounted-database inventory and `lilith/data/db.py:157-244` supplies `SessionKeyManager`, registered connections, and relock hooks; `lilith/data/ucl.py:15-35` mounts UCL and unmounts it at relock; `lilith/logic/cwm.py:205-275` owns the volatile PII session and clears it through that hook; `lilith/logic/cwm.py:385-480` has the conversational reverse filter and its `context.token.unmapped` call; `lilith/app.py:691-724` is the shutdown lifecycle seam. `lilith/data/backup.py:39-113` supplies an atomic backup set, and `.github/workflows/ci.yml` is the existing CI entry point. Reconcile the six-database wording in §02/§03/§06 with the mounted inventory only through a decided BD/AD; do not create empty databases merely to make a rotation test look complete.

Local Linux checks: the recall-gate script, real-SQLCipher unit/integration rotation and relock tests, payload-schema checks, and workflow syntax/assertion tests. Developer checks: Settings/tray interaction on a desktop, interrupted-rotation crash/resume on Linux/macOS, and hosted CI merge blocking. GitHub Actions cannot run because of billing; mark its DoD status exactly **pending developer (Actions billing)**.

### [B10-01] Stage passphrase rotation with journal and preflight backup
**Type:** [IMPLEMENT]  
**Law:** `s02.html` (`Passphrase Change & Key Rotation (SEC-009, Normative):` — `Verify:`, `Collect:`, `Preflight:`, `Stage:`); `s03.html` (`Key Rotation Mechanics (SEC-009):`); `s06.html` (`Passphrase Rotation Journal & Crash Resume (SEC-009):` — `Journal:`, `UCL events (security.rekey.*, §16):`, `Backups Across Rotation (SEC-009):`); `s25.html` (`Crash recovery & Prior-install detection:` — rotation-journal precedence); `s16.html` (`Event namespaces:`, `error.* Payload Rule:`, `Payload Content Boundary:`).  
**Depends on:** BD-044, BD-045

**What to build:** Implement the guarded foreground verify/collect/preflight/stage half of rotation. Verify the typed current passphrase against every applicable database before changes; apply the existing onboarding minimum-length, confirmation-match, strength, and blocklist rules to the twice-entered new passphrase. Pause database-requiring scheduled work, confirm free space at least combined database size plus 20%, and create a fresh integrity-checked `pre_rotation` backup before staging. Create `databases/rotation-<timestamp>/`, regenerate all six 32-byte salts into staged `salts.dat`, derive a new manager, and export each live SQLCipher database into the staged location with `ATTACH` plus `sqlcipher_export()`; integrity-check every staged copy. Maintain `databases/rotation.journal` through `verify -> preflight -> stage -> commit -> finalize`, atomically write-then-rename and fsync each transition, recording only staging name/progress/phase. Emit only declared `security.rekey.start`, `security.rekey.backup_created`, and `security.rekey.export_complete` operational payloads; never emit a passphrase, salt, key, PRAGMA, or database content.

**Docs:** create `docs/architecture/components/key-management.md` (rotation preflight, staging, journal secrecy, and backup relationship); update `docs/runbook/crash-recovery.md` (pre-commit rollback operator outcome), `tests/README.md` (real-SQLCipher rotation fixtures), and `docs/CHANGELOG.md` (`B10-01`).

**Acceptance criteria:** real keyed SQLCipher tests seed populated databases, prove old live files remain readable and byte-identical until commit, staged copies open only under new salts/passphrase and pass integrity checks, and journal files contain none of the prohibited secret material. Tests prove the 20% preflight refusal, paused backup work, fresh pre-rotation set, event-schema fields, and a staging failure leaves the live store untouched. Run on Linux locally; desktop UI confirmation remains developer verification.

### [B10-02] Commit, finalize, and recover an interrupted rotation
**Type:** [IMPLEMENT]  
**Law:** `s02.html` (`Passphrase Change & Key Rotation (SEC-009, Normative):` — `Commit:`, `Finalize:`, `Master Passphrase Write Path (Normative):`); `s03.html` (`Key Rotation Mechanics (SEC-009):`); `s06.html` (`Passphrase Rotation Journal & Crash Resume (SEC-009):` — `Commit point:`, `Startup resolution (Phase 4 pre-step):`, `Cleanup:`, `UCL events (security.rekey.*, §16):`, `Backups Across Rotation (SEC-009):`); `s25.html` (`Interrupted Passphrase Rotation — Pre-Commit`, `Interrupted Passphrase Rotation — Post-Commit`).  
**Depends on:** B10-01, BD-044

**What to build:** Add the Settings passphrase-change progress hook and perform commit/finalize exactly after staging. Close all connections; write the `commit` journal phase as the point of no return; rename old database files and `salts.dat` into `quarantine-rotation-<timestamp>/`, then place all staged files as the committed batch using per-file, idempotent journal records. Construct a fresh `SessionKeyManager`, reopen and verify every rotated database, then and only then update `master_passphrase` in convenience mode. Take the post-rotation backup, resume the paused backup schedule, emit the remaining declared `security.rekey.*` events, remove the journal, and delete old-key quarantine files only after successful finalize. At Phase 4 before all other classification, deterministically delete only pre-commit staging/journal or roll forward a commit-or-later journal; an unreadable journal routes to explicit recovery untouched. Preserve the exact §06/§25 user messages and new-passphrase prompt; never use `PRAGMA rekey` or offer a keychain-only master-passphrase update.

**Docs:** extend `docs/architecture/components/key-management.md` (commit point, keychain-last invariant, resume paths); update `docs/runbook/crash-recovery.md` (rows d/e exact outcomes), `docs/architecture/data-flows/startup-sequence.md`, and `docs/CHANGELOG.md` (`B10-02`).

**Acceptance criteria:** real populated SQLCipher tests prove successful rotation has no row loss, old passphrase refusal/new passphrase success, new manager construction, post-rotation backup, and keychain update only after reopen verification. Crash-injection tests at every pre-commit phase prove deterministic rollback; every commit-or-later rename interruption resumes idempotently and demands the new passphrase; unreadable journal preserves journal/staging/quarantine. Test the keychain-last ordering and all declared event payloads. Linux local crash tests are required; macOS/Settings-progress UI is pending developer.

### [B10-03] Add explicit relock and unlock lifecycle wrappers
**Type:** [IMPLEMENT]  
**Law:** `s02.html` (`Explicit Re-Lock (Normative):`); `s03.html` (`Relock Support:`); `s06.html` (`Graceful Shutdown Sequence:`); `s16.html` (`Event namespaces:`, `Write rule:`).  
**Depends on:** B10-02, BD-046

**What to build:** Build one lifecycle wrapper used by both Settings and tray `Lock Lilith` actions. It stops voice capture, pauses scheduler jobs requiring database access, closes connections/WAL through `SessionKeyManager.relock()`, drops all derived keys and attached PII state, moves the UI to its locked screen, and writes `security.relock`. Build the corresponding locked-screen unlock path: prompt mode requires typed passphrase; convenience mode offers the keychain unlock; a new manager derives keys and mounts databases before UI/activity resumes, then writes `security.unlock`. Do not implement idle auto-relock. Register the wrapper in the existing lifecycle rather than duplicating key/connection cleanup, and preserve no-key/no-plaintext fallback behavior when UCL is unavailable during the swap boundary.

**Docs:** extend `docs/architecture/components/key-management.md` (wrapper order and threat boundary); update `docs/architecture/data-flows/startup-sequence.md`, `docs/runbook/README.md` (manual lock/unlock), and `docs/CHANGELOG.md` (`B10-03`).

**Acceptance criteria:** real SQLCipher lifecycle tests prove manual relock closes registered connections, subsequent keying fails until a fresh unlock, PII session data is cleared, database scheduler jobs and voice capture stop, and correct `security.relock`/`security.unlock` schemas are emitted when UCL is available. UI tests expose both specified actions and a locked screen. Linux local tests cover wrapper order; desktop Settings/tray behavior is pending developer.

### [B10-04] Give artifact tasks immutable PII snapshots and fail closed at relock
**Type:** [IMPLEMENT]  
**Law:** `s14.html` (`Cloud PII Tokenization (SEC-018 — v1 detection scope: person names, email addresses, phone numbers):` — `Ephemeral Mapping Table — Session Scope (SEC-022):`, `Reverse-Substitution Pass:`, `Task-Owned Mappings for Artifact Tasks (SEC-022):`, `Unmapped-Tag Handling (SEC-022):`); `s02.html` (`Explicit Re-Lock (Normative):`); `s15.html` (`Tool System` — `failure` narrative); `s16.html` (`Event namespaces:`, `Payload Content Boundary:`).  
**Depends on:** B10-03, BD-046

**What to build:** At cloud artifact dispatch, capture an immutable mapping snapshot containing exactly the mappings substituted into that artifact payload; reverse-substitute its response only from that snapshot. Track cancellable in-flight artifact work with task id/tool name but never persist mapping values. Make the relock wrapper cancel all in-flight artifact work, drop every snapshot, emit `error.artifact.relock_cancelled` with exactly `task_id` and `tool_name`, and discard every late response before reverse substitution, TTS, UI, memory, or any database write. After the next unlock, report the cancelled task through its §15 failure narrative. A response tag absent from the snapshot follows the existing neutral placeholder path; no identity mapping may survive relock.

**Docs:** update `docs/architecture/components/context-window-manager.md` (snapshot ownership and cancellation boundary), `docs/architecture/data-flows/artifact-lane.md` (dispatch/relock sequence), `docs/runbook/README.md` (lock during a task), and `docs/CHANGELOG.md` (`B10-04`).

**Acceptance criteria:** integration tests dispatch a real artifact-path request with PII, assert the outbound payload has tags and its snapshot alone restores mapped output, then relock before a delayed response. They prove cancellation, empty session/task mappings, exact cancel event schema, failure narrative, and no late text reaches TTS/UI/memory/database. A fabricated absent snapshot tag produces its neutral placeholder and event. Run against real SQLCipher stores on Linux; no database mock is permitted.

### [B10-05] Complete unmapped-tag UCL telemetry for both consumers
**Type:** [IMPLEMENT]  
**Law:** `s14.html` (`Unmapped-Tag Handling (SEC-022):`, `Telemetry:`); `s16.html` (`UCL Telemetry` — `Event namespaces:`, `Function:`, `Payload Content Boundary:`); `s08.html` (`UCL Telemetry Assertions:`, `Payload Schema Review:`).  
**Depends on:** B10-04

**What to build:** Register and enforce `context.token.unmapped` in the UCL event schema with the §14 fields: anonymous literal `tag`, `tag_family`, `turn_id or task_id`, and `consumer`. Keep the existing conversational path routed through mounted `ucl_db`; add the artifact `task_id`/`consumer="artifact"` path. Validate that every replacement happens upstream of all consumers, including TTS, chat UI, memory, and database writes, and that a literal tag never escapes. Do not add free text, mapping values, or catch-all payload fields.

**Docs:** update `docs/architecture/components/ucl-telemetry.md` (declared event schema) and `docs/architecture/components/context-window-manager.md` (consumer correlation); update `docs/CHANGELOG.md` (`B10-05`).

**Acceptance criteria:** unit tests feed invented, previous-session, and missing-snapshot tags through split streaming chunks for all four families; they prove the exact neutral strings, UCL rows in real `ucl_db`, declared payload validation, correct turn/task correlation, and absence of literals/PII from downstream text and persisted rows. Runs locally on Linux with real SQLCipher.

### [B10-06] Make the recall corpus a local and CI merge gate
**Type:** [IMPLEMENT]  
**Law:** `s08.html` (`PII Detector Recall Corpus (SEC-018, mandatory CI):`, `No-DB-Mocking Policy:`, `Test Execution Timeouts:`); `s14.html` (`Recall Done-Criterion (merge-blocking, see §08):`, `PII Detector (three classes, full v1 scope):`); `s07.html` (`Pipeline Triggers:`, `Standard Build Steps (All Jobs):`, `Anti-Rot Triage Discipline:`).  
**Depends on:** B10-05, BD-047

**What to build:** Add `tests/unit/fixtures/pii_corpus.json`, `tests/unit/test_pii_detector_recall.py`, and a directly runnable local gate script that evaluates annotated positive spans by class. Include unusual names, nicknames, possessives, quoted-name text, international/separator/extension phones, and plus-addressed/subdomained emails. Fail unless name recall is `>= 95%`, email recall is `100%`, and phone recall is `100%`; precision is reported but not gated. Add the same script/test as a blocking step in the existing workflow, following current triggers and permissions. Document the dogfooding corpus-growth rule: a recall failure adds the failing case or anonymized equivalent and must restore thresholds before merge. The gate must exercise the actual detector and real SQLCipher fixture/migration conventions for any database-touching test; do not mock a database.

**Docs:** create `docs/runbook/pii-recall-gate.md` (local command, thresholds, annotation/scoring choice, corpus growth, CI status); update `tests/README.md`, `docs/runbook/ci.md`, and `docs/CHANGELOG.md` (`B10-06`).

**Acceptance criteria:** the local Linux command passes on the committed corpus and mutation checks (remove a true detection or add a missed annotated span) fail. Tests prove class-separated denominator math, exact threshold boundaries, named corpus cases, and no network. Workflow inspection proves the gate runs for the configured PR/push paths. Hosted execution and proof that it blocks a merge are **pending developer (Actions billing)**; do not mark that DoD box complete until Actions billing permits it.

### [B10-07] Execute the Phase-3 PII, relock, and rotation validation
**Type:** [TEST]  
**Law:** `BUILD_SEQUENCING.md` §4 (`Phase 3: Security & Key Management Expansion` — `Validation:`); `BUILD_GUIDE.md` §5 (CH-10 Definition of Done, item 1 and item 3); `s02.html` (`Passphrase Change & Key Rotation (SEC-009, Normative):`, `Explicit Re-Lock (Normative):`); `s14.html` (`Unmapped-Tag Handling (SEC-022):`, `Task-Owned Mappings for Artifact Tasks (SEC-022):`); `s08.html` (`No-DB-Mocking Policy:`).  
**Depends on:** B10-02, B10-04, B10-05, B10-06

**What to build:** Write and run a reproducible Phase-3 validation against canned provider-schema fixtures: send names, email addresses, phone numbers, and the sequencing-required calendar names/addresses through the cloud path; assert outbound payloads contain no detected PII and correct mapped text returns. Feed a fabricated unmapped tag and prove neutral per-family text, not a literal tag, reaches TTS, UI, and persistence. Start an artifact task, relock while its response is delayed, and prove its response is discarded and it receives the failure narrative. Rotate a populated real SQLCipher store and prove data loss does not occur. Capture the local command and immutable fixture/result evidence; distinguish it from the hosted CI result.

**Docs:** add the exact Phase-3 procedure/results/evidence checklist to `docs/audits/CH-10.md`; update `tests/README.md` and `docs/CHANGELOG.md` (`B10-07`).

**Acceptance criteria:** one real-SQLCipher integration test suite passes on Linux and independently demonstrates every first and third DoD condition. It uses canned provider JSON fixtures, not a live cloud call, and no database mock. The corpus workflow merge-block result remains **pending developer (Actions billing)**.

### [B10-08] Chapter close — audit, documentation sweep, and status handoff
**Type:** [AUDIT]  
**Law:** `BUILD_GUIDE.md` §5 (CH-10 Definition of Done) and §7; `BUILD_SEQUENCING.md` §4 (`Phase 3: Security & Key Management Expansion`); `s02.html` (`Passphrase Change & Key Rotation (SEC-009, Normative):`, `Explicit Re-Lock (Normative):`); `s03.html` (`Key Rotation Mechanics (SEC-009):`, `Relock Support:`); `s08.html` (`PII Detector Recall Corpus (SEC-018, mandatory CI):`, `No-DB-Mocking Policy:`); `s14.html` (`Task-Owned Mappings for Artifact Tasks (SEC-022):`); `standards.html` (`Documentation Standards`, `No blind spots`).  
**Depends on:** B10-07

**What to build:** Audit all CH-10 DoD boxes with exact commands, test names, UCL rows/payload schemas, journal/resume evidence, and file-to-feature references in `docs/audits/CH-10.md`. Review the rotation journal for secret absence; preflight, commit, keychain-last, backup pause/post-backup, six-database inventory decision, crash rollback/roll-forward, and unreadable-journal preservation. Review manual relock/unlock ordering, every snapshot cancellation/late-response sink, unmapped tag consumer, corpus corpus-growth rule, thresholds, script, and workflow wiring. Verify all named Docs contributions, sweep affected `docs/architecture/` status lines, and list every local versus developer-only command. Update BUILD_GUIDE §4 status only after review as coordinator work, not as a build-task edit.

**Docs:** `docs/audits/CH-10.md`, `docs/README.md` (chapter-audit row), `docs/CHANGELOG.md` (`B10-08`), and status-line updates in every CH-10-touched `docs/architecture/` page.

**Acceptance criteria:** a reviewer can trace each DoD item to reproducible evidence and each Docs field to a landed file; all database tests use real SQLCipher; every named event has schema evidence; no secrets appear in journal/events/logs; and encoding sweep reports no mojibake. The recall gate's hosted merge proof is explicitly **pending developer (Actions billing)** until Actions executes it.

## Sequential order

```text
BD-044, BD-045 -> B10-01 (journal + staging) -> B10-02 (commit + finalize + Settings hook)
                                                -> B10-03 (explicit relock/unlock; BD-046)
                                                -> B10-04 (artifact snapshots + fail-closed cancel)
                                                -> B10-05 (unmapped-token UCL)
BD-047 ------------------------------------------------> B10-06 (recall corpus + local/CI gate)
B10-02, B10-04, B10-05, B10-06 -> B10-07 (Phase-3 validation) -> B10-08 (audit)
```

*When B10-08 closes, CH-10 is done only when the Phase-3 validation and populated-store rotation evidence pass, and the recall-corpus gate has hosted proof of merge blocking. Until Actions can run, that latter DoD remains **pending developer (Actions billing)**.*
