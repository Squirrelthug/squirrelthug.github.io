# SPRINT-B01 — Foundation & Skeleton

**Sprint ID:** BUILD-01
**Chapter:** CH-01 (see `BUILD_GUIDE.md` §5) · **Kanban:** [Issue #1](https://github.com/Squirrelthug/squirrelthug.github.io/issues/1) on [Project 46 — Lilith v6 Build](https://github.com/users/Squirrelthug/projects/46)
**Status:** Blocked on four open decisions (see below) — Ready once they are made
**Law for this sprint:** §01, §02, §03, §04, §06, §08 — https://squirrelthug.github.io/lilith-v6-design/sections/s01.html (…s02, s03, s04, s06, s08)
**Prerequisites:** none — this is the first code of v6.

## Open decisions blocking this sprint (added 2026-08-06)

Four choices below are assumed by tasks in this sprint but are **not made by the frozen law**. Each has a researched decision brief in `docs/decisions/` on the build repo and a kanban sub-issue on [#1](https://github.com/Squirrelthug/squirrelthug.github.io/issues/1). Until a brief is resolved, the task that depends on it must not be started — an agent hitting the gap will either guess or stop and report, and both cost more than deciding first.

| Brief | Decision | Blocks | Kanban |
|:--|:--|:--|:--|
| BD-001 | Lint, format & type-check toolchain | B01-01, all later tasks | [#16](https://github.com/Squirrelthug/squirrelthug.github.io/issues/16) |
| BD-002 | Dependency pinning & `requirements.txt` regeneration | B01-01, CH-09 CI gate | [#17](https://github.com/Squirrelthug/squirrelthug.github.io/issues/17) |
| BD-003 | Exception hierarchy & error taxonomy | B01-04, B01-05, B01-06 | [#18](https://github.com/Squirrelthug/squirrelthug.github.io/issues/18) |
| BD-004 | Migration manager shape across six databases | B01-05 (+ CH-04/09/12/13) | [#19](https://github.com/Squirrelthug/squirrelthug.github.io/issues/19) |

When a decision is made, its build ADR is written **and the affected task text below is edited to state the decision as instruction** — so no later agent re-derives it. That edit is part of the decision, not a follow-up.

---

## Goal

A repository that starts, opens one encrypted database, shuts down cleanly, and has a working test harness. At sprint end the app does almost nothing — and does it perfectly: single-instance lock, secure-keyring-only credentials, Argon2id→SQLCipher key path through a `SessionKeyManager`, `conversation_db` mounting and migrating, ordered startup and shutdown, and tests against real encrypted databases.

## Context every agent must have

Each task below is worked by its own isolated agent. An agent receives, at minimum:

1. **The Non-Negotiable Standards** — https://squirrelthug.github.io/lilith-v6-design/standards.html — read first, every session. The floor below which code does not ship.
2. **The law sections listed on its task** — https://squirrelthug.github.io/lilith-v6-design/sections/sNN.html — implemented *exactly as written*. If the task text and a section conflict, the section wins; if build work exposes a genuine gap or contradiction in the law, **stop and report** — the developer resolves it through a documented design session. Never improvise architecture in code.
3. **This file's header + its own task block.**

**Ground rules (from `BUILD_GUIDE.md` §2):** only what is written gets built; excluded means absent — no stubs-with-logic or "while I'm here" implementations of any section outside this sprint's law; standards are the floor.

**Documentation is part of done (never broken):** the build repo carries a version-controlled `docs/` tree — the lens map is `docs/README.md` (architecture maps, data flows, developer guide, user guide, runbook, ADRs, changelog). Every task below has a **Docs:** field naming its exact contributions; the task is not done until they land in the same PR. Minimum for any task: its `docs/CHANGELOG.md` entry under the CH-01 heading. If your implementation (within the law) differs from what an existing diagram or guide page shows, fixing that page is part of your task. `docs/` is committed and pushed like code — only generated renders (`docs/_rendered/`) stay out of git.

### The build repository

- **The v6 repo is the existing private repo `Squirrelthug/LILITH`** — reset to a clean slate on 2026-08-03 (tracked files: `.gitignore`, `CLAUDE.md`, `bin/lilith` only; read `CLAUDE.md` first, it carries the repo's standing rules). v5 is archived at `Squirrelthug/lilith-v5` and at tag `v5-final` in this repo's history — reference only, **no v5 code crosses**. Do not create a new repository.
- **Working clone:** `~/projects/lilith/` on the Linux MASTER machine (clone `Squirrelthug/LILITH` there if absent).
- **Workflow (§01, law):** `feature/*` or `bugfix/*` branches, **mandatory PRs** to `main`, commit messages prefixed `[scope]:` (e.g. `[data]: add migration manager`). CI does not exist until CH-09 (§07 is excluded from Milestone 1), so M1 PRs are merged after the developer's review and a green local `timeout 180 pytest`.
- **Root package layout (§01, law — build it exactly):**

```
lilith/                    (root package)
├── app.py                 # Application entrypoint & Qt initialization
├── config.py              # Config loader/migrator & global constants
├── platform/              # OS Abstractions
│   ├── paths.py           # OS-specific base directories
│   ├── keyring.py         # Wrapper for OS-level secure keyring
│   └── audio.py           # PortAudio stream management (placeholder until CH-02)
├── data/                  # Persistence Layer
│   ├── db.py              # SQLCipher connection lifecycle & pool
│   ├── ucl.py             # UCL writing/reading (M1: dev-log shim, see stand-ins)
│   └── conversation.py    # Chat & session DB interface (schema lands in CH-04)
├── logic/                 # Domain Layer (placeholders until CH-03: router.py, stt.py, tts.py, cwm.py)
└── ui/                    # Presentation Layer (placeholders until CH-05: bus.py, screens/, widgets/, shaders/)
```

Dependency direction (law, enforced with import-linter): `ui → logic → data → platform`, downwards only.

### Locked decisions inherited by every task (from the law — do not re-litigate)

- **Python 3.12**, enforced via `.python-version` + `pyproject.toml` (§01).
- **pip + requirements.txt** generated from `pyproject.toml` — reproducible, deterministic installs (§01). *(Note: an older design-phase draft said uv; the frozen law says pip. The law wins.)*
- **`pathlib.Path` everywhere** — no `os.path.join`, no string concatenation, no hardcoded separators (§01, standards).
- **Keychain service namespace:** `"com.squirrelthug.lilith"`; Linux backend `SecretServiceKeyring`; startup refuses to boot on insecure/failed backends (§02).
- **`salts.dat`:** exactly **192 bytes** — six contiguous 32-byte salts in fixed index order `ucl_db, calendar_db, contacts_db, finance_db, memory_db, conversation_db` (§02). All six salts are provisioned even though M1 mounts only `conversation_db`.
- **Argon2id:** `time_cost=3, memory_cost=65536 KiB, parallelism=2`, 32-byte output → 64-char hex → `PRAGMA key = "x'<hex>'"` (§03).
- **`sqlcipher3-wheels`** as the database engine package (§03).
- **`APP_INTERNAL_DIR`** (Linux): `Path.home() / ".local/share/lilith"`, children `databases/ logs/ models/ cache/ backups/ skills/`; POSIX perms 0700 dirs / 0600 files, verified at startup (§04).
- **Naming:** snake_case files/tables, PascalCase classes, UPPER_SNAKE constants, dot.namespaced event types (§01).
- **Plaintext logs boundary (§04):** `logs/` receives operational facts only — never user content, prompts/completions, tokens/keys, raw tracebacks, SQL with key material.
- **Telemetry never crashes the main path**; `log_event()` on every write/state-mutation success path (standards).

### Milestone-1 stand-ins (explicit, sanctioned by the M1 table in `BUILD_SEQUENCING.md` §2.1)

- **No §25 onboarding UI.** Setup (passphrase entry, salt generation, first database creation) happens via a **local dev CLI command** (task B01-06). It must follow §02/§06's salt-origin rules exactly: `salts.dat` is generated via `os.urandom(192)` *only when no database files exist*; if databases exist but salts are missing, startup halts with the recovery error — never regenerate.
- **No §16 `ucl_db`.** `log_event(event_type: str, payload: dict)` ships now with its permanent signature, but writes JSON lines to `APP_INTERNAL_DIR/logs/dev.log`. The §16 event-payload hygiene and the plaintext-logs boundary apply *by discipline* now (the enforcement sanitizer machinery is CH-09 scope): payloads carry compact operational facts and non-secret identifiers only.
- **The 10-phase §06 startup sequence is built as its M1 subset:** Phase 1 (hardware) is a stub returning a placeholder tier until CH-02; Phases 8–9 (scheduler, voice) are no-ops until their chapters; Phase 10 renders no window until CH-05 — "active" means the process is up and idle. The *ordering and structure* of the sequence is law and is built now.

### Kanban protocol (revised 2026-08-06)

**One board carries the whole development cycle.** [Project 46](https://github.com/users/Squirrelthug/projects/46) holds the 15 chapter/gate cards *and* the finer-grained work beneath them, using GitHub sub-issues so each chapter card shows its own progress (e.g. `3/13`).

- **Decision briefs** (BD-NNN) and **sprint tasks** (B01-NN) are each their own issue in `Squirrelthug/squirrelthug.github.io`, added to Project 46 and registered as **sub-issues of the chapter card** they belong to — for this sprint, issue [#1](https://github.com/Squirrelthug/squirrelthug.github.io/issues/1).
- **Working a task:** move its card to **In Progress** when you start, **Done** when its acceptance criteria *and* its `Docs:` contribution have both landed. The task issue is the unit an agent is pointed at.
- **The chapter card** sits in **In Progress** for the duration of the sprint and shows sub-issue progress automatically.
- **Sprint close (B01-09):** the closing agent ticks the Definition-of-Done checkboxes on issue #1, confirms every sub-issue is closed, moves the chapter card to **Done**, and updates `BUILD_GUIDE.md` §4 (CH-01 → Done).

*This supersedes the original protocol ("tick nothing on the board; task tracking lives in this file / PRs"), which kept task-level progress invisible. The sprint document remains the authoritative task **specification**; the board is the authoritative task **status**.*

---

## Tasks

---

### [B01-01] Repository bootstrap & project skeleton
**Type:** [IMPLEMENT]
**Law:** §01 (primary), §08 (test layout), §04 (single-repo rationale)
**Depends on:** —

**What to build:**
- Clone `Squirrelthug/LILITH` (the v6 clean slate — see the build-repository note in this sprint's header) to `~/projects/lilith/`. All work lands via PR per the §01 workflow — practice starts at commit one. Keep the existing `.gitignore`, `CLAUDE.md`, and `bin/lilith`; extend `.gitignore` as needed rather than replacing it.
- `.python-version` → `3.12`. `pyproject.toml` declaring the project, Python `>=3.12`, and dependencies as they're introduced by later tasks (start minimal: `pytest`, `import-linter`; add `sqlcipher3-wheels`, `argon2-cffi`, `keyring`, `psutil` in their tasks). `requirements.txt` generated from `pyproject.toml`; document the regeneration command in the file header.
- The §01 package layout exactly as shown in this sprint's header. Modules whose content belongs to later chapters are **docstring-only placeholders** stating which chapter fills them (e.g. `logic/router.py` → "CH-03, §13") — no speculative logic.
- `import-linter` configured with the layered contract `ui → logic → data → platform`; add a `lint` section to the README describing how to run it (it joins CI in CH-09).
- Pathlib lint rule: configure the linter (ruff — dev tooling choice, not law) to flag `os.path` usage; `pathlib.Path` is the only path API.
- `tests/unit/` and `tests/integration/` mirroring the source layout (§08), with one trivial passing test each so the timeout conventions (`timeout 60 pytest tests/unit/`, `timeout 180 pytest`) are exercised from day one.
- `.gitignore`: `.env` (never committed, §02/standards), `__pycache__`, virtualenvs. `README.md` stub pointing at the design site and `docs/SETUP.md` (B01-08).

**Docs:** `docs/CHANGELOG.md` entry (CH-01 section). Verify `docs/DEVELOPER.md` §3 against what you actually configured — exact linter names, install and sweep commands — and correct any drift.

**Acceptance criteria:** Fresh clone + `pip install -r requirements.txt` succeeds on Linux; both pytest sweeps pass inside their timeouts; `import-linter` passes; the tree matches the §01 layout byte-for-name; no `os.path` anywhere; first PR merged with `[scope]:`-prefixed commits; Docs contributions landed.

---

### [B01-02] `platform/paths.py`, platform detection & config loader
**Type:** [IMPLEMENT]
**Law:** §04 (primary), §01 (config management)
**Depends on:** B01-01

**What to build:**
- `platform/paths.py` as the **single source of truth for all paths** (§04): `APP_INTERNAL_DIR` per-OS (Linux `~/.local/share/lilith`, macOS `~/Library/Application Support/Lilith`, Windows `%LOCALAPPDATA%\Lilith` — all three mappings now, even though only Linux runs in M1), and derived `DB_DIR, LOG_DIR, MODELS_DIR, CACHE_DIR, BACKUP_DIR, SKILLS_DIR`. `EXTERNAL_BACKUP_DIR` defaults per §04 (`~/Documents/Lilith Backups`), overridable via `config.json` key `backup.external_destination`, which **must resolve outside `APP_INTERNAL_DIR`** — reject at entry otherwise.
- Directory creation helper: creates the `APP_INTERNAL_DIR` tree with 0700 (dirs) / 0600 (files) on POSIX; a verify-and-tighten function for startup (§02/§04).
- Platform detection **once** via `sys.platform` → `IS_LINUX, IS_MAC, IS_WINDOWS` flags in `lilith.platform` (§04). No ad-hoc environment checks in feature code.
- `config.py`: loads/creates `config.json` in `APP_INTERNAL_DIR`, with a programmatic schema-migration hook run at startup (§01). Keep v1 schema minimal (config schema version + `backup.external_destination`); later chapters add keys.

**Docs:** `docs/CHANGELOG.md` entry. Update `docs/architecture/01-containers.md` if any module/path name in the diagram differs from what you built (the diagram must name real modules).

**Acceptance criteria:** Unit tests (monkeypatched home dir) assert all Linux paths and the derived children; permission bits asserted 0700/0600 after creation and after tighten-on-startup; an `EXTERNAL_BACKUP_DIR` override inside `APP_INTERNAL_DIR` is rejected; a repo-wide grep shows no path construction outside `paths.py`; config round-trips and migrates a deliberately old schema version; Docs contributions landed.

---

### [B01-03] Keyring wrapper & secure-backend verification
**Type:** [IMPLEMENT]
**Law:** §02 (primary)
**Depends on:** B01-01

**What to build:**
- `platform/keyring.py` wrapping `python-keyring` under the canonical service namespace `"com.squirrelthug.lilith"`. Expose typed get/set/delete for the §02 canonical key names as constants: `master_passphrase`, `install_sentinel`, `security_tier`, `anthropic_api_key` (the others in the §02 table are later-chapter writers, but the constants exist now so no string literals ever appear at call sites).
- **Startup security verification (§02):** check `keyring.get_keyring()` returns a secure backend; if an insecure plaintext fallback (`keyrings.alt`-class) or a fail backend is detected, raise an unrecoverable security exception — the app refuses to boot. Keyring *unavailable/error* is a distinct halt with the §02 recovery message: `"OS secure keychain is unavailable. Please verify your system's keyring daemon is running."`
- **No keyring operations are logged** (§02) — no `log_event`, no debug lines, nothing, to prevent timing/leak vulnerabilities.

**Docs:** `docs/CHANGELOG.md` entry. Verify the keychain reflexes in `docs/DEVELOPER.md` §4 match implemented behavior (service name, refusal semantics) and correct any drift.

**Acceptance criteria:** Unit tests with substituted backends: a secure backend passes verification; a `keyrings.alt`-style backend and a fail-backend each cause boot refusal with the correct exception type and message; get/set/delete round-trip against the test backend; a log-capture fixture proves zero log emissions from any keyring code path; Docs contributions landed.

---

### [B01-04] Key derivation, `salts.dat` handling & `SessionKeyManager`
**Type:** [IMPLEMENT]
**Law:** §03 (primary), §02 (salt file rules)
**Depends on:** B01-02, B01-03

**What to build:**
- Salt file I/O (§02): read `DB_DIR / "salts.dat"` via `Path.read_bytes()`; validate **exactly 192 bytes**; slice into six 32-byte salts under the fixed index order `ucl_db=0, calendar_db=1, contacts_db=2, finance_db=3, memory_db=4, conversation_db=5` (a module-level constant). Reading is this task; *generation* belongs only to the B01-06 bootstrap CLI (§02's three-origins rule — never generate here).
- Argon2id derivation via `argon2-cffi`: `time_cost=3, memory_cost=65536, parallelism=2`, 32-byte raw output per database from (master passphrase, that database's salt) (§03).
- `SessionKeyManager` (§03): derives all keys **once per unlocked session**, holds them privately; `apply_sqlcipher_key(conn, db_name)` executes `PRAGMA key = "x'<64 hex>'"` in a narrow internal scope; **any** exception while applying/verifying raises generic `DatabaseKeyingFailed` carrying database identity and recovery category only — no key material, PRAGMA text, locals, raw driver text, or tracebacks in message or `__cause__`. `__repr__`/`__str__` return a constant redacted value (`<SessionKeyManager redacted>`). `relock()` closes registered connections and drops key material; post-relock keying requests raise `DatabaseKeyingFailed` until a new unlock.

**Docs:** `docs/CHANGELOG.md` entry. Update `docs/architecture/data-flows/key-derivation.md`: name the actual modules/classes you built in the diagram and prose, and correct any within-the-law detail that differs from the seeded version.

**Acceptance criteria:** Known-vector test: same passphrase+salt reproduces the same 64-char hex across runs; wrong-size salt files (191, 193, 0 bytes) rejected with a recovery-category error; `repr`/`str` leak nothing under direct call and inside f-strings/tracebacks; a forced keying failure's exception chain is scanned by the test for absence of hex/PRAGMA/passphrase substrings; `relock()` behavior verified; Docs contributions landed.

---

### [B01-05] SQLCipher connection lifecycle, migration manager & `conversation_db` mount
**Type:** [IMPLEMENT]
**Law:** §03 (primary)
**Depends on:** B01-04

**What to build:**
- `data/db.py`: connection factory implementing the §03 sequence verbatim —

  ```python
  conn = sqlcipher3.connect(str(db_path))
  key_manager.apply_sqlcipher_key(conn, db_name)
  conn.execute("PRAGMA journal_mode = WAL;")
  conn.execute("PRAGMA synchronous = NORMAL;")
  conn.execute("PRAGMA busy_timeout = 5000;")
  conn.execute("PRAGMA foreign_keys = ON;")
  conn.execute("SELECT count(*) FROM sqlite_master;")  # Lazy eval verify
  ```

  Connection-per-thread discipline (§03): the factory hands each thread/job its own connection; no sharing across threads. Registration with the `SessionKeyManager` so `relock()` can close them.
- Custom migration manager (§03): numbered SQL scripts (`0001_init.sql`, …) run sequentially at startup, idempotent, inside a transaction, tracked in a `schema_version` (or equivalent meta) table. M1 mounts **exactly one** database: `conversation_db`. Its `0001_init.sql` creates only the migration-tracking meta table — the `turns`/`sessions` schema is CH-04 scope (§18) and must not appear here.
- `log_event()` M1 shim in `data/ucl.py` (permanent signature `log_event(event_type: str, payload: dict)`): JSON lines to `LOG_DIR / "dev.log"`; catches its own exceptions (telemetry never crashes the main path — standards); payload discipline per the plaintext-logs boundary.

**Docs:** `docs/CHANGELOG.md` entry. Update the connection-sequence portion of `docs/architecture/data-flows/key-derivation.md` and the `data/` layer names in `docs/architecture/01-containers.md` to match the real modules.

**Acceptance criteria:** Real-SQLCipher tests (no mocks, §08): create → key → open → verify succeeds; wrong passphrase surfaces as `DatabaseKeyingFailed` (and the file is untouched); `PRAGMA journal_mode` returns WAL; migration runner applied twice is a no-op the second time; a cross-thread connection-sharing attempt is caught by the discipline (factory API makes it structurally awkward and tests document the rule); `log_event` writes valid JSON lines and survives an unwritable log dir without raising; Docs contributions landed.

---

### [B01-06] Dev bootstrap CLI & process lifecycle (startup/shutdown/lock)
**Type:** [IMPLEMENT]
**Law:** §06 (primary), §02 (salt origins, unlock modes), §03 (mounting), §04 (permission verify)
**Depends on:** B01-05

**What to build:**
- **Dev bootstrap CLI** (M1 stand-in for §25 clean install; e.g. `python -m lilith.bootstrap`): interactively collects a passphrase (twice, minimum 12 chars), then — *only if no database files exist in `DB_DIR`* — generates `salts.dat` via `os.urandom(192)`, stores `master_passphrase` in the keyring (convenience mode; also write `security_tier="convenience"`), creates and migrates `conversation_db`, and prints next steps. If databases exist, it refuses with the recovery guidance (§02/§06: never regenerate salts over live data).
- **Startup sequence** in `app.py`, as the §06 10-phase structure with M1 stubs: 1 hardware-profile stub → 2 acquire `APP_INTERNAL_DIR/lilith.lock` via `fcntl.flock` exclusive lock, write PID, verify 0700/0600 permissions → 3 keyring verification (B01-03) → 4 load `salts.dat` (halt with `"Salts missing — restore salts.dat from backup to recover access"` if databases exist without it; if neither exists, direct the user to the bootstrap CLI — the M1 analogue of §25 classification) → 5 unlock resolution (convenience: read `master_passphrase` from keychain; missing passphrase with existing databases is credential recovery, not first-run) → 6 mount `conversation_db` (keying failure: halt and prompt guidance, never delete) → 7 run migrations → 8–9 no-op stubs → 10 process active (idle loop; no window until CH-05). Lock-acquisition failure: print/dialog `"Lilith is already running"` and exit immediately — the flock result alone gates the refusal; the stored PID is read via `psutil` only to enrich the message (§06).
- **Stale-lock handling (§06):** lockfile exists with a dead PID → assume crash, clean the lock, proceed; emit `error.crash_recovery` via `log_event`. (Full state-machine gating and quarantine are CH-09 scope.)
- **Graceful shutdown** (§06 order, M1 subset): stop audio streams (stub) → scheduler shutdown (stub) → abort in-flight LLM calls (stub) → close all DB connections flushing WAL → release and delete `lilith.lock` → exit 0. Wired to SIGTERM and SIGINT.

**Docs:** `docs/CHANGELOG.md` entry. Update the status line of `docs/architecture/data-flows/startup-sequence.md` (built-subset state). Write the first three runbook procedures in `docs/runbook/` per its writing rule (numbered steps, exact commands, expected outcomes, telemetry events emitted): *bootstrap a fresh machine*, *start / stop / verify*, *second-instance & stale-lock behavior*.

**Acceptance criteria:** Scripted end-to-end on Linux: bootstrap → start → phase log shows the ordered sequence → SIGTERM → exit code 0, lock removed, WAL flushed; second concurrent start refused with the exact §06 message while the first keeps running; kill -9 then restart cleans the stale lock and logs `error.crash_recovery`; bootstrap refuses when a database exists; salts-missing-with-databases halts with the §06 recovery message; startup with no salts and no databases points to the bootstrap CLI and touches nothing; Docs contributions landed.

---

### [B01-07] Test-harness hardening & seam tests
**Type:** [TEST]
**Law:** §08 (primary)
**Depends on:** B01-06

**What to build:**
- `tests/unit/conftest.py` (§08): fixture creating an **in-memory real SQLCipher database**, keyed with the fixed test passphrase, migrations applied, torn down per test. `mock_ucl`-style fixture capturing `log_event` emissions with a `has_event(event_type, payload_subset)` assertion helper matching the §08 example. `tests/unit/fixtures/` directory established for future canned LLM payloads.
- `tests/integration/conftest.py`: temp-file databases through the real bootstrap path, keyring substituted per §08 integration conventions.
- **Seam tests** (the places the happy path hides bugs): full lifecycle round-trip (bootstrap → start → write a meta row → clean shutdown → restart → row still present, key still works); double-instance refusal; keyring-unavailable and insecure-backend boot refusals; permission verify-and-tighten after deliberately loosening a directory; wrong-passphrase mount failure leaving files untouched.
- Wire a coverage run and record the number: the §01 done-criteria floor is **80%+ excluding hardware/audio I/O** (audio is placeholder-only this sprint, so exclusion lists stay tiny).

**Docs:** `docs/CHANGELOG.md` entry. `tests/README.md` documenting the fixtures (this task's core doc deliverable). Verify `docs/DEVELOPER.md` §3's testing bullets against the harness as built and correct any drift.

**Acceptance criteria:** `timeout 60 pytest tests/unit/` and `timeout 180 pytest` both green; every write path introduced in B01-02…06 has a test asserting its `log_event` emission (standards); coverage ≥80% on the shipped modules; the fixtures are documented in `tests/README.md` so later sprints reuse rather than reinvent; Docs contributions landed.

---

### [B01-08] Setup documentation
**Type:** [REPORT]
**Law:** §01 (workflow), §04 (paths) — plus everything shipped this sprint
**Depends on:** B01-07

**What to build:** `docs/SETUP.md` in the build repo: prerequisites (Python 3.12, Linux keyring daemon), fresh-clone install (`pip install -r requirements.txt`), bootstrap CLI walkthrough, starting and stopping the app, where everything lives on disk (`APP_INTERNAL_DIR` map from §04), how to run the test sweeps and lint/import-linter, and the contribution conventions (branch naming, mandatory PRs, `[scope]:` commit prefixes, the done-criteria checklist from §01). One page, plain language, current — this document satisfies the CH-01 DoD's "documented setup steps" line and gets maintained every sprint after.

**Docs:** this task *is* documentation: `docs/SETUP.md` plus a `docs/CHANGELOG.md` entry. Additionally: verify the three B01-06 runbook procedures by literally following them (fix any step that doesn't survive contact), and update the SETUP row of the lens table in `docs/README.md` from *(lands with task B01-08)* to a live link.

**Acceptance criteria:** A fresh clone on the MASTER machine, following *only* this document, reaches a running, cleanly-stopping app — performed literally, not assumed; runbook procedures verified; Docs contributions landed.

---

### [B01-09] Chapter close — audit, kanban, guide
**Type:** [AUDIT]
**Law:** CH-01 Definition of Done (`BUILD_GUIDE.md` §5), M1 exclusions (`BUILD_SEQUENCING.md` §2.1)
**Depends on:** B01-08

**What to do:**
1. Walk every CH-01 DoD checkbox with concrete evidence (command outputs, test run logs), recorded in a short `docs/audits/CH-01.md` in the build repo.
2. **Scope audit:** verify by inventory that nothing from an EXCLUDED section exists — no `ucl.db` mount, no second database file, no sync/contacts/calendar/onboarding/vault code, no vector or embedding dependency in `requirements.txt`, `logic/` and `ui/` still placeholder-only. Verify the tree still matches §01 exactly.
3. **Docs sweep (Documentation Standards):** verify every task's **Docs:** contribution landed; update the status lines on `docs/architecture/00-system-context.md`, `01-containers.md`, and the data-flow pages plus the table in `data-flows/README.md` to reflect what CH-01 actually built; confirm the CH-01 section of `docs/CHANGELOG.md` is complete. Record the sweep's outcome in the audit file.
4. Tick the Definition-of-Done checkboxes on [issue #1](https://github.com/Squirrelthug/squirrelthug.github.io/issues/1) (`gh issue edit 1` on the body's checklist), move the project card to **Done** (`gh project item-edit`), and update `BUILD_GUIDE.md` §4 in the design-site repo: CH-01 → **Done** (commit via the site's normal flow).
5. Report completion to the developer — authoring `SPRINT-B02-voice-io.md` is the developer-triggered next step, not this agent's.

**Acceptance criteria:** Audit file merged (including the docs-sweep outcome); issue #1 shows all boxes ticked and the card sits in Done; the guide's status table reflects CH-01 complete; every architecture/data-flow status line matches built reality; the report to the developer lists any observations worth carrying into the B02 sprint authoring (tuning notes, friction, law ambiguities encountered and how they were resolved or reported).

---

## Sequential order

```
B01-01 ──► B01-02 ──┐
      └──► B01-03 ──┴──► B01-04 ──► B01-05 ──► B01-06 ──► B01-07 ──► B01-08 ──► B01-09
```

B01-02 and B01-03 are independent of each other and may run in parallel after B01-01. Everything else is strictly sequential.

---

*When B01-09 closes, CH-01 is done. Next: author `SPRINT-B02-voice-io.md` from `BUILD_GUIDE.md` CH-02 + §05/§09/§10/§11, per the working loop.*
