# SPRINT-B09 — Foundation Hardening & Telemetry

**Sprint ID:** BUILD-09  
**Chapter:** CH-09. **Status:** 2026-10-25, reviewed by the build manager; decisions BD-034…BD-040 taken (design-site PR, not merged).  
**Prerequisites:** CH-01 through CH-08 are built and audited. DS-01 (2026-10-25) concerns hybrid router routing only; it is expressly outside this sprint. **Law:** `BUILD_GUIDE.md` §2–§3 and §5 CH-09; `BUILD_SEQUENCING.md` §4 Phase 2 and §2.1 rows §06, §07, §16; `s16.html`, `s06.html`, `s07.html`, `s04.html`, `s25.html`, `s08.html`, and `standards.html`.

## Decisions (BD-034…BD-040, decided by the build manager under the developer's standing directive; build-repo AD-060…AD-066)

| Brief | Question | Decision | Blocks |
|:--|:--|:--|:--|
| BD-034 | §16 names `lilith.telemetry.ucl.log_event(event_type: str, payload: dict) -> str`; the M1 shim is `lilith.data.ucl.log_event()`. | **Move it to `lilith.telemetry.ucl` and update every caller; no forwarding shim** (excluded means absent). `lilith.telemetry` becomes its own import-linter layer between `lilith.data` and `lilith.platform` (`ui → logic → data → telemetry → platform`), since data writes events. (AD-060) | B09-01 |
| BD-035 | Where event payload declarations live. | **A Python registry beside the UCL code** (`lilith/telemetry/events.py`: event type → allowed field names), checked by `log_event` and by tests; it rejects §16's prohibited catch-all fields. (AD-061) | B09-01, B09-02, B09-06 |
| BD-036 | How the Qt shell presents recovery. | **A modal recovery dialog shown before the main window**, one per affected database, with §25's exact copy; nothing is written, moved or deleted before the user confirms. (AD-062) | B09-04, B09-05 |
| BD-037 | One workflow or several; required checks. | **One `.github/workflows/ci.yml`** with the three-platform matrix and the security jobs as parallel jobs, plus a `schedule` trigger for the weekly full-history gitleaks scan. Making them required checks on `main` is a repository-admin action, listed for the developer. (AD-063) | B09-06 |
| BD-038 | The restore prompt needs "the latest valid atomic backup", but only pre-migration copies exist (`lilith/data/db.py:481-552`); §06 *Automated Backups* (SEC-011) is CH-09's section yet no Phase 2 bullet names it. | **Build §06 atomic backup sets in CH-09 (new task B09-09, before B09-05):** set composition, `backup.manifest.json`, `backups/backup-<timestamp>/`, the daily 03:20 job, the pre-migration trigger, 7-set retention. The optional external mirror (SEC-019 setting) stays out: its Settings surface is §29-reminder scope. (AD-064) | B09-05, B09-07 |
| BD-039 | §06/§25/§08 say "all 6 databases"; at CH-09 only `ucl_db` and `conversation_db` exist (the others arrive with their chapters). | **The set is the databases the build mounts**: composition, completeness check and drill cover every mounted database + `salts.dat`; the manifest lists them, and the code takes the list from one constant, so it grows to six without a format change. No empty placeholder databases. (AD-065) | B09-05, B09-07, B09-09 |
| BD-040 | §07's standard build steps include resource compilation and `pyinstaller lilith.spec --onedir`; no spec file exists. | **B09-06 adds a minimal `lilith.spec` (onedir) bundling the package data `pyproject.toml` already declares** (migrations, prompts, shaders). Resource compilation is that bundling; there are no Qt `.qrc` files to compile. The CI artifact is the onedir build. (AD-066) | B09-06 |

## Goal

Replace Milestone 1’s `APP_INTERNAL_DIR/logs/dev.log` telemetry stand-in with the encrypted UCL; make every remaining plaintext path sanitizer-gated and boundary-checked; recover safely from a dead-PID crash through the §25 state table, quarantine, and informed restore prompt; and put the whole repository through parallel three-platform GitHub Actions. This sprint creates no router work and no deferred app features.

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-09)

- [ ] Phase-2 validation passes as written: clean-VM artificial crash → corrupt DBs quarantined → app prompts restore-from-backup, never silently deletes.
- [ ] Telemetry events migrate from dev-log to `ucl_db`; sanitizer verifiably strips sensitive content from plaintext logs.
- [ ] All three CI platform jobs green on the main branch.

## Context every agent must have

Read `standards.html`, the Law pages in the **Law:** line, this sprint, and `BUILD_GUIDE.md` §2–§3. `BUILD_SEQUENCING.md` §2.1 deferred §07 and §16 in M1: the built `lilith/data/ucl.py` is therefore a JSON-line dev-log shim, not the permanent UCL. The existing `lilith/app.py` already owns startup, the lock, and lifecycle; `lilith/data/db.py` already has the six database-key names; `lilith/platform/paths.py` defines `databases/`, `logs/`, and `backups/`. Build on those seams, citing their current lines in the implementation report.

**Testing:** §08 separates fast isolated `tests/unit/` tests from multi-component `tests/integration/` workflows. Any database test uses real keyed SQLCipher databases and migrations—never a database mock. Tests of every write/state mutation assert the declared dot-namespaced UCL event and payload schema. Windows desktop work may run Windows-safe unit/integration checks; POSIX lock/signal behavior needs the developer’s Linux/macOS machines; the clean-VM crash drill needs a real clean VM; and the `main`-branch CI result is **pending developer merge** because nothing in this sprint is merged to `main` yet. The feature-branch workflow is still run where GitHub Actions permits.

### [B09-01] Mount the SQLCipher UCL and migrate the dev-log telemetry seam
**Type:** [IMPLEMENT]  
**Law:** `s16.html` (`UCL Telemetry` — `Schema:`, `Function:`, `Search:`, `Concurrency:`); `s04.html` (`Cross-Platform Foundations` — `APP_INTERNAL_DIR`, `Plaintext Logs Boundary:`); `BUILD_SEQUENCING.md` §4 (`Phase 2: Foundation Hardening & Telemetry`).  
**Depends on:** BD-034, BD-035 (decided)

**What to build:** Mount `ucl_db` at the §04-named `APP_INTERNAL_DIR / "databases" / "ucl.db"` through `sqlcipher3-wheels==0.5.7`; apply SQLCipher keying, `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000`, and one connection per thread/job. Migrate `log_event()` from the M1 JSON-line `dev.log` stand-in to the §16 encrypted ledger: return a UUIDv7 id; write exactly `ucl_events(id TEXT PRIMARY KEY, event_type TEXT NOT NULL, payload JSON NOT NULL, timestamp REAL NOT NULL, session_id TEXT)`; use UTC Unix seconds with millisecond precision; create the external-content `ucl_events_fts` FTS5 table with `unicode61`; assert `ENABLE_FTS5` from `pragma_compile_options` at startup and CI. Preserve every existing event call while routing it to UCL, and declare each event payload’s allowed fields before implementation. Do not serialize UCL payloads to plaintext logs or add L1/L2 work.

**Docs:** create `docs/architecture/components/ucl-telemetry.md` (mount, schema, event-schema boundary, concurrency, and no-direct-LLM-read rule); update `docs/architecture/01-containers.md`, `docs/architecture/data-flows/startup-sequence.md`, `docs/architecture/data-flows/README.md`, and `docs/CHANGELOG.md` (`B09-01`).

**Acceptance criteria:** real-SQLCipher unit tests prove keyed mount, schema, UUIDv7 return, millisecond UTC timestamp, all named columns, FTS search, WAL, `5000` busy timeout, and startup/CI FTS5 assertion. Integration tests prove existing mutation events enter `ucl_db`, not `dev.log`, and validate declared payload fields; UCL rows contain compact facts/identifiers only. Runs on this Windows desktop except POSIX-only lock assertions.

### [B09-02] Enforce sanitizer-gated plaintext logging
**Type:** [IMPLEMENT]  
**Law:** `s16.html` (`Sanitizer Gate:`, `error.* Payload Rule:`, `Payload Content Boundary:`); `s04.html` (`Plaintext Logs Boundary:`); `standards.html` (`No blind spots`, `Telemetry never crashes the main path`).  
**Depends on:** B09-01, BD-035

**What to build:** Make `lilith.telemetry.sanitize_exception()` the only exception representation accepted by UCL, plaintext logs, recovery logs, and UI recovery text. It must redact 64-character SQLCipher hex keys, `sk-ant-` keys and following token material, `Bearer ` authorization tokens, OAuth refresh tokens, and common provider credential fields. Enforce the §04 plaintext boundary: logs may contain startup markers, health, migration phase names, and sanitizer-confirmed error categories only; they may not contain user text, conversation/retrieved context, prompts/completions, tokens/keys, raw tracebacks/locals, SQL containing key material, or serialized UCL payloads. Keep telemetry failures non-propagating, stderr-sanitized, and counted.

**Docs:** update `docs/architecture/components/ucl-telemetry.md` (sanitizer contract and allowed plaintext fields), `docs/runbook/README.md` (safe log collection), and `docs/CHANGELOG.md` (`B09-02`).

**Acceptance criteria:** unit tests inject each named secret pattern and forbidden content into exceptions/logging paths and prove redaction or rejection; a can-fail test makes an unsanitized exception path fail. Integration tests prove recovery/UI text and failed telemetry writes never expose raw exception text, SQL, user content, or a serialized UCL payload. Runs on this Windows desktop.

### [B09-03] Implement §25 state-table classification after stale-lock crash detection
**Type:** [IMPLEMENT]  
**Law:** `s06.html` (`Crash Recovery & Consensual Restore (SEC-004 / SEC-011):`, `Phase 4 (Salt Loading):`, `Phase 6 (Database Mounting):`); `s25.html` (`Startup sequence routing is governed by a strict state table`, state rows (a)–(f)); `standards.html` (`Recovery flows never delete`).  
**Depends on:** B09-01

**What to build:** After successful OS-lock acquisition finds a dead PID, clean the stale lock and classify database files, `salts.dat`, keychain/onboarding evidence, staging/quarantine leftovers, and integrity/keying result by the §25 state table. Preserve its distinctions: setup interruption is not credential failure; keying failure never touches/deletes databases; structural corruption is separate; missing salts with databases halts with the specified restore-salts direction; absent salts with no databases creates nothing during startup. Emit only declared `error.recovery.*` compact events. Do not implement passphrase rotation journal behavior (CH-10 scope).

**Docs:** update `docs/architecture/data-flows/startup-sequence.md` with the state-table decision flow and evidence links; create `docs/runbook/crash-recovery.md` for the operator-visible classifications; update `docs/CHANGELOG.md` (`B09-03`).

**Acceptance criteria:** real-file/real-SQLCipher integration tests cover dead-PID stale-lock detection, setup-crash classification, missing-salts halt, wrong-passphrase/key failure with byte-identical files, and structural corruption classification; each mutation asserts its UCL event schema. Windows desktop runs the Windows lock/version; Linux/macOS developer runs confirm POSIX `fcntl` behavior.

### [B09-04] Quarantine affected recovery files before any replacement
**Type:** [IMPLEMENT]  
**Law:** `s06.html` (`Quarantine by Default:`, `Recovery Logs:`); `s25.html` (state row (a), state row (c) `No silent/all-six restore.`); `standards.html` (`Recovery flows never delete`).  
**Depends on:** B09-03, BD-036

**What to build:** Implement quarantine moves to `APP_INTERNAL_DIR/databases/quarantine-<timestamp>/` for affected partial databases, salts, and corrupt databases before clean restart or restore. For an interrupted onboarding, show the specified explicit-confirmation question before any action and quarantine first. For corruption, preserve unaffected databases and support the state-table’s per-database path; never overwrite in place or silently delete. Record `error.recovery.onboarding_crash`, `error.recovery.corruption_detected`, and `error.recovery.quarantine_created` with declared non-secret fields only.

**Docs:** update `docs/runbook/crash-recovery.md` (quarantine location, consent and preservation guarantees), `docs/architecture/data-flows/startup-sequence.md`, and `docs/CHANGELOG.md` (`B09-04`).

**Acceptance criteria:** integration tests create partial/corrupt real SQLCipher files, prove affected files are moved—not deleted or overwritten—only after explicit confirmation, and prove unaffected files remain. Tests validate all recovery event payload schemas. Runs on this Windows desktop; a clean-VM filesystem/permissions run remains pending developer.

### [B09-09] Atomic backup sets (§06 Automated Backups)
**Type:** [IMPLEMENT]  
**Law:** `s06.html` (`Automated Backups (SEC-011):` — `Trigger & Schedule:`, `Set Composition:`, `Retention:`); `standards.html` (`Recovery flows never delete`).  
**Depends on:** B09-01, BD-038, BD-039

**What to build:** Create atomic backup sets under `APP_INTERNAL_DIR/backups/backup-<timestamp>/`: every mounted database (BD-039) + the matching `salts.dat` + a non-secret `backup.manifest.json` (set format version, UTC creation timestamp, app version, per-file name/size/SHA-256; never key material). Take a set daily from a background job scheduled at 03:20 and immediately before database migrations (replace the per-database pre-migration copies, keeping their behaviour). A set is valid only when every manifest hash verifies; keep the 7 most recent valid sets and delete older ones. Emit declared UCL events for set created / failed / pruned. The external mirror is out of scope (BD-038).

**Docs:** `docs/runbook/crash-recovery.md` (where sets live, what makes one valid), `docs/architecture/components/ucl-telemetry.md` (backup events), `docs/CHANGELOG.md` (`B09-09`).

**Acceptance criteria:** real-SQLCipher tests prove set composition, manifest fields and hashes, no key material in the manifest, that an interrupted set is never counted valid, retention at 7, the pre-migration trigger, and the scheduler computing the next 03:20 run (clock injected). Runs on this Windows desktop.

### [B09-05] Add the consented restore-from-backup prompt and placement flow
**Type:** [IMPLEMENT]  
**Law:** `s06.html` (`No Silent Restoration:`, `Restore Entry Point (fresh install / reinstall, SEC-019):`); `s25.html` (`Restore from a backup`, `Select:`, `Completeness check:`, `Stage:`, `Place:`, `UCL events:` and state rows (c), (f)); `s08.html` (`Backup→Wipe→Reinstall→Restore Drill (SEC-019, mandatory CI)`).  
**Depends on:** B09-04, B09-09, BD-036, BD-039

**What to build:** Present the latest valid atomic-backup timestamp and per-database data-loss interval; use the exact §25 confirmation form: `Restore [db_name] from backup (<timestamp>)? Approximately [X] hours of data will be lost.` Never silently restore all six. For fresh install/reinstall, accept an exported/mirrored set read-only, validate `backup.manifest.json` (or the listed legacy structural set), stage under `databases/restore-staging-<timestamp>/`, verify every staged SQLCipher database the manifest lists with the supplied passphrase, then quarantine existing partial files and place only the verified batch. Source sets are never modified/deleted. Emit only `error.recovery.restore_started`, `error.recovery.restore_complete`, or `error.recovery.restore_failed` with the enumerated reason/timestamp/duration fields; defer keychain-write-last completion and full onboarding to their named scope.

**Docs:** extend `docs/runbook/crash-recovery.md` (selection, validation, staging, prompt, refusal paths); update `docs/architecture/data-flows/startup-sequence.md`; update `tests/README.md` with the restore drill; update `docs/CHANGELOG.md` (`B09-05`).

**Acceptance criteria:** the required `tests/integration/test_backup_restore_drill.py` uses real SQLCipher files: seed every mounted database (BD-039) plus `salts.dat`, export, wipe `APP_INTERNAL_DIR`, restore into a fresh tree, prove integrity checks, row counts, manifest hashes and byte-identical salts; wrong-passphrase/incomplete sets refuse, preserve the source, and emit the correct reason. This is merge-blocking CI; its Windows-safe deterministic portion runs here, and clean-VM execution is pending developer.

### [B09-06] Add parallel GitHub Actions CI and security gates
**Type:** [IMPLEMENT]  
**Law:** `s07.html` (`Pipeline Triggers:`, `Multi-Platform Runner Matrix:`, `Standard Build Steps (All Jobs):`, `Security Tooling Jobs (mandatory from Sprint 1):`, `Anti-Rot Triage Discipline:`); `s08.html` (`Test Execution Timeouts:`, `Backup→Wipe→Reinstall→Restore Drill (SEC-019, mandatory CI)`).  
**Depends on:** B09-01, B09-02, B09-05, BD-037

**What to build:** Configure GitHub Actions for `push` to `main` and pull requests targeting `main`, with parallel `ubuntu-latest`, `macos-latest`, and `windows-latest` build/test jobs. Every matrix job uses `actions/checkout@v4`, `actions/setup-python@v5` with Python `3.12` and pip cache, `pip install -r requirements.txt` with prefer-binary, `pytest --timeout=60 -v` (hardware-bound audio/keyring tests skipped), resource compilation, `pyinstaller lilith.spec --onedir`, and `actions/upload-artifact@v4`. Add parallel Ubuntu-only required security jobs: bandit (`HIGH` with at least `MEDIUM` confidence), `semgrep ci --config=auto --error`, `pip-audit -r requirements.txt --strict`, and gitleaks (incoming range on push/PR; `--log-opts="--all"` on main/weekly). Use least-privilege `contents: read`, no production credentials/keychain/passphrases/BYOK keys, per-finding justified suppressions only, and include the §08 backup drill as merge-blocking.

**Docs:** create `docs/runbook/ci.md` (jobs, local equivalents, feature-branch evidence versus main status, security suppression audit); update `docs/README.md`, `docs/CHANGELOG.md` (`B09-06`), and `tests/README.md` (CI test inventory).

**Acceptance criteria:** workflow YAML is validated/linted locally where tooling exists; on the feature branch, GitHub Actions runs every available job and artifacts are inspectable. Linux/macOS require hosted runners; Windows can be checked locally plus hosted runner. The three-green-on-`main` DoD box is explicitly **pending developer merge** until this sprint lands on `main`; it is never represented as met before then. Administrator-required branch-protection changes are listed, not presumed.

### [B09-07] Run the Phase-2 artificial-crash validation
**Type:** [TEST]  
**Law:** `BUILD_SEQUENCING.md` §4 (`Phase 2: Foundation Hardening & Telemetry` — `Validation:`); `BUILD_GUIDE.md` §5 (CH-09 Definition of Done, item 1); `s06.html` (`Crash Recovery & Consensual Restore (SEC-004 / SEC-011):`); `s08.html` (`Backup→Wipe→Reinstall→Restore Drill (SEC-019, mandatory CI)`).  
**Depends on:** B09-05, B09-06

**What to build:** Write and execute the reproducible artificial-crash procedure: create a valid store and backup, leave a dead-PID lock and corrupt selected real SQLCipher database files, relaunch, verify quarantine, verify the exact informed restore prompt, refuse or defer until consent, then restore only the selected database from the valid atomic set. Capture the automated drill separately from the clean-VM evidence. Do not call an automated test a clean-VM result.

**Docs:** add the exact clean-VM procedure and evidence checklist to `docs/runbook/crash-recovery.md`; add `docs/CHANGELOG.md` (`B09-07`); publish command/results in the task report.

**Acceptance criteria:** automated real-SQLCipher integration test passes on this Windows desktop and CI. A developer runs the procedure on a real clean VM and records the result; until then this acceptance box is `pending developer clean-VM run`. No source/affected file may disappear before confirmation.

### [B09-08] Chapter close — audit, documentation sweep, and status handoff
**Type:** [AUDIT]  
**Law:** `BUILD_GUIDE.md` §5 (CH-09 Definition of Done) and §7; `BUILD_SEQUENCING.md` §2.1 rows §06/§07/§16 and §4 Phase 2; `s08.html` (`UCL Telemetry Assertions:`, `No-DB-Mocking Policy:`); `standards.html` (`Documentation Standards`, `Recovery flows never delete`).  
**Depends on:** B09-07

**What to build:** Audit every CH-09 DoD checkbox with commands, results, exact test names, payload-schema evidence, and existing-code-to-new-code references in `docs/audits/CH-09.md`. Verify UCL replaces dev-log telemetry without a plaintext payload leak; sanitize every exception/recovery/UI path; inspect all §25 state-table/quarantine/restore paths for no silent delete; check CI triggers, matrix, security jobs, weekly scan behavior, and every suppression. Verify every B09 Docs contribution, sweep architecture/data-flow status lines, and confirm the BD-034…BD-040 decisions were followed. Mark clean VM, developer Linux/macOS, and CI-green-on-`main` honestly as pending where evidence is unavailable; the latter remains pending developer merge until merged.

**Docs:** `docs/audits/CH-09.md`, `docs/README.md` (Chapter audits row), `docs/CHANGELOG.md` (`B09-08`), and status-line updates in all CH-09-touched `docs/architecture/` pages.

**Acceptance criteria:** reviewer can independently trace every DoD item to test/evidence, every Docs field to a landed file, and every external/developer-only check to an exact pending command. The design-site `BUILD_GUIDE.md` §4 status update is a coordinator action after review and is listed as pending—not edited by sprint task agents.

## Sequential order

```text
BD-034, BD-035 -> B09-01 (UCL mount + dev-log migration) -> B09-02 (sanitizer boundary)
                                      -> B09-03 (state classification) -> B09-04 (quarantine; BD-036)
                                      -> B09-09 (atomic backup sets; BD-038/039) -> B09-05 (restore prompt) -> B09-06 (CI; BD-037)
                                      -> B09-07 (artificial crash validation) -> B09-08 (audit)
```

*When B09-08 closes, CH-09 is done only after the clean-VM validation and all three CI jobs are green on `main`; unmerged feature-branch workflow evidence is not a substitute.*
