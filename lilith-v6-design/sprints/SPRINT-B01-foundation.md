# SPRINT-B01 — Foundation & Skeleton

**Sprint ID:** BUILD-01
**Chapter:** CH-01 (see `BUILD_GUIDE.md` §5) · **Kanban:** [Issue #1](https://github.com/Squirrelthug/squirrelthug.github.io/issues/1) on [Project 46 — Lilith v6 Build](https://github.com/users/Squirrelthug/projects/46)
**Status:** Unblocked — all four decision briefs are DECIDED (BD-004 closed 2026-08-09). Every task below reads as instruction; B01-01 is ready to start
**Law for this sprint:** §01, §02, §03, §04, §06, §08 — https://squirrelthug.github.io/lilith-v6-design/sections/s01.html (…s02, s03, s04, s06, s08)
**Prerequisites:** none — this is the first code of v6.

## Open decisions blocking this sprint (added 2026-08-06)

Four choices below are assumed by tasks in this sprint but are **not made by the frozen law**. Each has a researched decision brief in `docs/decisions/` on the build repo and a kanban sub-issue on [#1](https://github.com/Squirrelthug/squirrelthug.github.io/issues/1). Until a brief is resolved, the task that depends on it must not be started — an agent hitting the gap will either guess or stop and report, and both cost more than deciding first.

| Brief | Decision | Blocks | Kanban | Status |
|:--|:--|:--|:--|:--|
| BD-001 | Lint, format & type-check toolchain | B01-01, all later tasks | [#16](https://github.com/Squirrelthug/squirrelthug.github.io/issues/16) | **DECIDED 2026-08-06 — ADR `B-001`; B01-01 text below is now instruction** |
| BD-002 | Dependency pinning & `requirements.txt` regeneration | B01-01, CH-09 CI gate | [#17](https://github.com/Squirrelthug/squirrelthug.github.io/issues/17) | **DECIDED 2026-08-07 — ADR `B-002`; B01-01 text below is now instruction.** Closes BD-001's second pinning location: the three Python tools become `repo: local` hooks driven by `requirements.txt` |
| BD-003 | Exception hierarchy & error taxonomy | B01-01 … B01-06 | [#18](https://github.com/Squirrelthug/squirrelthug.github.io/issues/18) | **DECIDED 2026-08-09 — ADR `B-003`; B01-01/03/04/05/06 text below is now instruction.** Reach was wider than the brief assumed: `lilith/errors.py` + `lilith/telemetry.py` move into **B01-01**, because B01-02 and B01-03 also raise |
| BD-004 | Migration manager shape across six databases | B01-05 (+ CH-04/09/12/13) | [#19](https://github.com/Squirrelthug/squirrelthug.github.io/issues/19) | **DECIDED 2026-08-09 — ADR `B-004`; B01-05 text below is now instruction.** Two corrections to the brief: `PRAGMA foreign_keys` is silently ignored inside a transaction (so the rebuild hook wraps the transaction from outside), and §06 Phase 7's **mandatory pre-migration backup** was missing from B01-05 and is now in scope |

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
├── errors.py              # Exception hierarchy & RecoveryCategory (BD-003 / ADR B-003)
├── telemetry.py           # §16's sanitize_exception() seam + root-handler filter (ADR B-003)
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

Dependency direction (law, enforced with import-linter): `ui → logic → data → platform`, downwards only — extended by ADR `B-003` with two lower layers, giving the full contract `ui → logic → data → platform → telemetry → errors`. `errors.py` imports nothing from `lilith`, so every layer may import it.

**`errors.py` and `telemetry.py` are additions to the §01 tree, and are sanctioned — do not report them as drift.** §01's diagram does not show them, but §16 names `lilith.telemetry.sanitize_exception()` outright, so the law itself requires a root module the diagram omits; the diagram is the layered skeleton, not an exhaustive inventory. ADR `B-003` records this reading. B01-01's "byte-for-name" criterion means *the tree in this header*, these two modules included.

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
- **No §16 `ucl_db`.** `log_event(event_type: str, payload: dict)` ships now with its permanent signature, but writes JSON lines to `APP_INTERNAL_DIR/logs/dev.log`. Payloads carry compact operational facts and non-secret identifiers only.
- **The §16 sanitizer: seam now, intelligence at CH-09** (revised by ADR `B-003`; supersedes the earlier note that *all* sanitizer machinery is CH-09 scope). §16 names `lilith.telemetry.sanitize_exception()` and §01 requires it on dev and startup logs — both of which exist in this sprint — so CH-01 builds the function, the root-handler filter and the excepthooks, with a deliberately simple fail-closed implementation. CH-09 replaces this module's internals with §16's real pattern-based sanitizer; no raise site changes when it does. The module docstring must name CH-09 as its owner.
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
- `.python-version` → `3.12`. `pyproject.toml` declaring the project and Python `>=3.12`. Runtime dependencies go under `[project] dependencies` as later tasks introduce them (`sqlcipher3-wheels`, `argon2-cffi`, `keyring`, `psutil` land in their own tasks); the toolchain goes under `[project.optional-dependencies] dev` — start with `pytest`, `ruff`, `basedpyright`, `import-linter`, `pre-commit`.
- **Dependency pinning — decided in BD-002, see ADR `B-002`. Use exactly this command; do not substitute the tool or drop a flag.** `requirements.txt` is **compiled, never hand-edited** — a version number typed into it by hand is a defect:

  ```bash
  uv pip compile pyproject.toml --extra dev --universal --generate-hashes \
    --python-version 3.12 -o requirements.txt
  ```

  - **`uv` compiles; pip installs.** This is the §01-compatible reading ruled on in B-002: uv produces the artifact and never installs, never ships, and never appears in CI. Installation stays `pip install -r requirements.txt` (with §07's `--prefer-binary`). Install uv locally as a build-time tool (`pip install uv`) and note it in `docs/SETUP.md` at B01-08 as a prerequisite.
  - **`--universal` is not optional.** It resolves for Linux, macOS and Windows at once and emits environment markers, so one committed file serves all three and the command is correct to run from any machine. Without it, the file is only valid on the OS that compiled it — a macOS-compiled file omits `secretstorage`/`jeepney`, which are `keyring`'s Linux backend and are exactly what **B01-03** exists to verify.
  - **`--generate-hashes` is not optional.** Expect a large file (≈1,400 lines for ≈90 packages) with many `--hash=sha256:` lines per package — that is correct, not noise. A binary-wheel package showing only *one* hash means `--universal` was dropped.
  - **One file, dev tools included** (`--extra dev`). §01 names one artifact; do not create `requirements-dev.txt`.
  - **Do not write the header comment by hand.** uv writes `# This file was autogenerated by uv via the following command:` plus the exact command into the file, which is what satisfies this task's "document the regeneration command in the file header" requirement.
  - Adding or bumping anything later follows the runbook procedure `docs/runbook/add-or-update-a-dependency.md`, including its mandatory **RES-15 licence check**. No Dependabot or Renovate is configured in v1.
  - Two platform floors, recorded so they are not rediscovered as CI failures: `PySide6==6.11.1` needs **glibc ≥ 2.34** on Linux (Ubuntu 22.04+); `onnxruntime` via `kokoro-onnx` publishes **macOS 14+** wheels only. Neither blocks Milestone 1 (Linux-only, §04).
- The §01 package layout exactly as shown in this sprint's header. Modules whose content belongs to later chapters are **docstring-only placeholders** stating which chapter fills them (e.g. `logic/router.py` → "CH-03, §13") — no speculative logic.
- **Toolchain — decided in BD-001, see ADR `B-001`. Configure exactly this; do not substitute tools or re-derive the choice.** All tool config lives in `pyproject.toml` (§01's agreed home), never in a scatter of dotfiles — the sole exception is `.pre-commit-config.yaml`, which the framework requires at the repo root.
  - **`ruff`** for both lint and format — it replaces black, isort, pyupgrade and most flake8 plugins; do not add those. In `[tool.ruff.lint]` set `select = ["E", "F", "I", "N", "B", "UP", "PTH"]`. `PTH` (flake8-use-pathlib) is the mechanism that enforces the standards page's pathlib mandate: it flags every `os.path` call and names the `pathlib` replacement. `pathlib.Path` is the only path API — **`PTH` is not optional and is never globally disabled.** Commands: `ruff check .` and `ruff format .`.
  - **`basedpyright`** for static type checking — `[tool.basedpyright]` with `typeCheckingMode = "basic"` and `include = ["lilith"]`. Basic (non-strict) is deliberate: annotate function signatures, dataclasses and the interfaces between layers; the checker reports genuine contradictions, not missing annotations. Use `basedpyright`, **not** `pyright` — it is the same engine redistributed as a pure-Python package, so it installs via pip into `requirements.txt` and keeps Node out of the build environment. Strictness is scheduled for review at CH-06; **do not raise it early.** Command: `basedpyright`.
  - **`import-linter`** configured with the layered contract `ui → logic → data → platform` (§01, law), extended downwards by ADR `B-003` so the errors module cannot import anything above it. Write exactly:

    ```toml
    [[tool.importlinter.contracts]]
    name = "Layers"
    type = "layers"
    layers = [
        "lilith.ui",
        "lilith.logic",
        "lilith.data",
        "lilith.platform",
        "lilith.telemetry",
        "lilith.errors",
    ]
    ```

    Command: `lint-imports`.
  - **`gitleaks`** as a local pre-commit hook (`zricethezav/gitleaks`), decided in BD-001. This is commit-time secret scanning only — it is **not** §07's CI job, which stays CH-09 scope along with bandit, semgrep and pip-audit. Do not add those three here.
  - **`pre-commit`** ties all four together in `.pre-commit-config.yaml` so they run on `git commit` against changed files. This is the enforcement mechanism until §07's CI arrives at CH-09, and the same config CI will then invoke — there is never a second definition of "clean". B01-01 must run `pre-commit install` and document it. Full-repo sweep: `pre-commit run --all-files`.
  - **Hook version pinning — decided in BD-002, see ADR `B-002`.** `ruff`, `basedpyright` and `import-linter` are configured as **`repo: local` hooks with `language: system`**, invoking whatever `requirements.txt` installed into the active environment. Do **not** give them remote `rev:`-pinned `repo:` entries — that would pin each tool a second time, in a file that can drift from `requirements.txt` with nothing reporting the mismatch. With local hooks there is exactly one pinned version of each tool, and drift is structurally impossible rather than merely monitored. Shape:

    ```yaml
    repos:
      - repo: local
        hooks:
          - id: ruff-check
            name: ruff check
            entry: ruff check --force-exclude
            language: system
            types_or: [python, pyi]
            require_serial: true
          # ruff format, basedpyright and lint-imports follow the same pattern
      - repo: https://github.com/zricethezav/gitleaks
        rev: v8.30.1        # the one accepted duplicate pin — see below
        hooks:
          - id: gitleaks
    ```

    **`gitleaks` is the deliberate exception**: it is a Go binary and is not distributed on PyPI, so it cannot live in `requirements.txt` under any arrangement. It keeps a remote `rev:` pin, which B-002 records as *accepted duplication* rather than unnoticed drift — bumping it is a step in the monthly dependency procedure. Pin a real released tag (`v8.30.1` was current at B-002; verify before writing it).
  - Add a `lint` section to the `README.md` covering the install (`pre-commit install`), the per-tool commands above, and the full sweep — noting these join CI in CH-09.
  - **If a tool rule ever conflicts with a section of the law: tune the rule, never the law.** Suppress or reconfigure narrowly, with a written justification at the suppression site. No blanket global ignores.
- **Exception hierarchy & sanitizer seam — decided in BD-003, see ADR `B-003`. Build exactly this; every later task raises through it.** This is the one part of B01-01 that is not a placeholder, and it is here rather than in B01-04 because B01-02 and B01-03 already raise.

  **`lilith/errors.py`:**

  ```python
  class RecoveryCategory(Enum):
      ALREADY_RUNNING = "already_running"          # §06 lock acquisition
      PERMISSIONS_INVALID = "permissions_invalid"  # §04 verify-and-tighten
      KEYRING_UNAVAILABLE = "keyring_unavailable"  # §02 daemon not running
      KEYRING_INSECURE = "keyring_insecure"        # §02 keyrings.alt / FailKeyring
      SALTS_MISSING = "salts_missing"              # §06 Phase 4
      CREDENTIAL_MISSING = "credential_missing"    # §06 Phase 5
      CREDENTIAL_INVALID = "credential_invalid"    # §06 Phase 6 · §25 row (b)
      DATABASE_CORRUPT = "database_corrupt"        # §06 (c) · §25
  ```

  These eight are the closed CH-01 set. **Do not add a member** — a new one needs a §06/§25 recovery state and its message, which is a decision, not an implementation detail. (`DATABASE_LOCKED` was considered and rejected: `busy_timeout = 5000` makes contention retryable, not a recovery-screen state.)

  `LilithError(Exception)` is the root, with exactly two children, `RecoverableError` and `UnrecoverableError`, and concrete errors below them — **three levels, no deeper.** Recoverable = caught at a module boundary, logged, surfaced, app continues; unrecoverable = recovery screen or hard exit, so `except UnrecoverableError` at the top of the process is a complete routing decision.

  - **No Lilith exception has a free-text message field.** Each concrete class declares three class-level constants — `message` (the §06/§25 string verbatim where the law gives one), `recovery_category`, `component` — and `__str__` returns `message`, so `f"{err}"` is safe. Instance state is **non-secret identifiers only** (`db_name`, event id), declared as keyword-only `__init__` parameters. There is deliberately no `detail=`, `context=` or `reason=` parameter; do not add one.
  - **`to_payload() -> dict[str, str]` on `LilithError`** returns exactly §16's declared `error.*` field set: `exception_type`, `message`, `recovery_category`, `component`, plus the instance's identifiers. Call sites write `log_event("error.…", err.to_payload())` and **never** assemble an error payload by hand — that is what keeps §08's payload schema review to one function.

  **`lilith/telemetry.py`** — `sanitize_exception(exc) -> str` (this name is fixed by §16, do not rename), a `SanitizingFilter`, `install_sanitizer()`, and `add_handler()`.

  - **Fail closed.** A `LilithError` returns its fixed `message`; **anything else** returns `<TypeName redacted>`. Never pass a non-Lilith exception's text through. The filter additionally strips long hex runs, `PRAGMA key = …`, `sk-ant-…` and `Bearer …` from record text.
  - **Install the filter on the root logger's `handlers`, never on the root logger itself.** A filter attached to a *logger* is consulted only for records logged through that logger directly — records propagating from child loggers skip it, which is every third-party library and therefore the entire point. Verified during the decision session; a logger-level filter passes its own unit test and protects nothing.
  - **The filter must collapse `record.getMessage()` and clear `record.args` before sanitizing.** A secret passed lazily (`log.info("key: %s", secret)`) is not in `record.msg` at all and is interpolated downstream of the filter. Sanitizing `record.msg` alone leaks it — this was an actual bug in the session's first prototype.
  - `install_sanitizer()` also sets `sys.excepthook` and `threading.excepthook` to route through `sanitize_exception()`, so an unhandled exception cannot print a raw traceback. It is called **once, before §06 Phase 1** (B01-06 wires it as the first statement of startup, ahead of the phase sequence — it is process setup, not an eleventh phase).
  - Any handler added later goes through `telemetry.add_handler()`. A handler attached directly to the root logger is a silent hole; the test below exists to catch it.
  - The module docstring names **CH-09 (§16)** as the owner that replaces these internals.
- `tests/unit/test_errors.py` — the tests that make the convention self-enforcing as chapters accumulate. Cheap to write, and they are why this lands at B01-01: (a) walk every `LilithError` subclass and assert no `__init__` parameter is named `message`/`msg`/`detail`/`details`/`context`/`reason`/`text`/`error`; (b) assert every concrete (leaf) class defines all three class constants and that `str(instance)` equals the class `message` regardless of instance state; (c) assert `to_payload()` emits only the declared keys; (d) assert every root-logger handler carries the `SanitizingFilter`; (e) assert `sanitize_exception()` on a non-Lilith exception carrying a 64-char hex string returns neither the hex nor the type's text.
- `tests/unit/` and `tests/integration/` mirroring the source layout (§08), with one trivial passing test each so the timeout conventions (`timeout 60 pytest tests/unit/`, `timeout 180 pytest`) are exercised from day one.
- `.gitignore`: `.env` (never committed, §02/standards), `__pycache__`, virtualenvs. `README.md` stub pointing at the design site and `docs/SETUP.md` (B01-08).

**Docs:** `docs/CHANGELOG.md` entry (CH-01 section). Verify `docs/DEVELOPER.md` §3 against what you actually configured — exact linter names, install and sweep commands, and the dependency-regeneration command — and §4 ("Raising errors") against the hierarchy as built; correct any drift.

**Acceptance criteria:** Fresh clone + `pip install --require-hashes --prefer-binary -r requirements.txt` succeeds on Linux — `--require-hashes` is what proves the hash set is complete, so use it here even though the everyday command omits it; `requirements.txt` carries uv's autogenerated header naming the regeneration command; every platform-specific binary-wheel package (`sqlcipher3-wheels` and friends) shows **many** `--hash=` lines, not one; both pytest sweeps pass inside their timeouts; `pre-commit run --all-files` passes clean (ruff check, ruff format, basedpyright, lint-imports, gitleaks); `pre-commit install` has been run and the hook fires on a test commit; the tree matches this sprint header's layout byte-for-name — which includes `errors.py` and `telemetry.py`, sanctioned by ADR `B-003` and not to be reported as drift; `lint-imports` passes the six-layer contract; the five `test_errors.py` assertions pass; no `os.path` anywhere — verified by `PTH` being enabled and passing, not by grep alone; first PR merged with `[scope]:`-prefixed commits; Docs contributions landed.

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
- **Errors, per ADR `B-003`:** the verify-and-tighten helper raises `PermissionsInvalid` (an `UnrecoverableError`, `recovery_category = RecoveryCategory.PERMISSIONS_INVALID`, `component = "platform.paths"`, identifier `path: str`) — B01-06 catches it at Phase 2. A rejected `EXTERNAL_BACKUP_DIR` override is a **`RecoverableError`**, not a halt: it is a config-value problem the user can correct, so it surfaces and the app continues on the §04 default. Neither carries a free-text field; do not invent a third exception here.

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
- **The two exceptions, per ADR `B-003`** — both `UnrecoverableError` subclasses in `lilith/errors.py`, `component = "platform.keyring"`, no free-text field:
  - `KeyringInsecure` — `recovery_category = RecoveryCategory.KEYRING_INSECURE`. These are two categories rather than one precisely because §02 treats them as distinct halts with different user guidance, and this task's acceptance criteria already test them separately.
  - `KeyringUnavailable` — `recovery_category = RecoveryCategory.KEYRING_UNAVAILABLE`, `message` set to the §02 string above **verbatim**.
  - Wrapping a backend error uses `raise KeyringUnavailable() from None` — a bare `raise` inside `except` leaks the caught exception's text through `__context__`.
- **No keyring operations are logged** (§02) — no `log_event`, no debug lines, nothing, to prevent timing/leak vulnerabilities.

**Docs:** `docs/CHANGELOG.md` entry. Verify the keychain reflexes in `docs/DEVELOPER.md` §4 match implemented behavior (service name, refusal semantics) and correct any drift.

**Acceptance criteria:** Unit tests with substituted backends: a secure backend passes verification; a `keyrings.alt`-style backend and a fail-backend each cause boot refusal with the correct exception type and message; get/set/delete round-trip against the test backend; a log-capture fixture proves zero log emissions from any keyring code path — **including the error paths**, which raise and let the caller log (§02 admits no exception for failures); the rendered exception chain from a wrapped backend error contains none of the driver's text; Docs contributions landed.

---

### [B01-04] Key derivation, `salts.dat` handling & `SessionKeyManager`
**Type:** [IMPLEMENT]
**Law:** §03 (primary), §02 (salt file rules)
**Depends on:** B01-02, B01-03

**What to build:**
- Salt file I/O (§02): read `DB_DIR / "salts.dat"` via `Path.read_bytes()`; validate **exactly 192 bytes**; slice into six 32-byte salts under the fixed index order `ucl_db=0, calendar_db=1, contacts_db=2, finance_db=3, memory_db=4, conversation_db=5` (a module-level constant). Reading is this task; *generation* belongs only to the B01-06 bootstrap CLI (§02's three-origins rule — never generate here).
- Argon2id derivation via `argon2-cffi`: `time_cost=3, memory_cost=65536, parallelism=2`, 32-byte raw output per database from (master passphrase, that database's salt) (§03).
- `SessionKeyManager` (§03): derives all keys **once per unlocked session**, holds them privately; `apply_sqlcipher_key(conn, db_name)` executes `PRAGMA key = "x'<64 hex>'"` in a narrow internal scope; **any** exception while applying/verifying raises generic `DatabaseKeyingFailed` carrying database identity and recovery category only — no key material, PRAGMA text, locals, raw driver text, or tracebacks in message or `__cause__`. `__repr__`/`__str__` return a constant redacted value (`<SessionKeyManager redacted>`). `relock()` closes registered connections and drops key material; post-relock keying requests raise `DatabaseKeyingFailed` until a new unlock.
- **The exceptions this task adds, per ADR `B-003`** — `DatabaseKeyingFailed` and `SaltsInvalid`, both `UnrecoverableError` subclasses with no free-text field:
  - `DatabaseKeyingFailed`: `message = "Key verification failed. Incorrect passphrase or mismatched salts."` (§25 verbatim), `recovery_category = RecoveryCategory.CREDENTIAL_INVALID`, `component = "data.db"`, and exactly one identifier — `db_name: str`, keyword-only. That is the whole of §03's "database identity and recovery category only".
  - `SaltsInvalid` for a salt file of the wrong size: `recovery_category = RecoveryCategory.SALTS_MISSING`, `message` set to the §06 string `"Salts missing — restore salts.dat from backup to recover access"`. **Do not put the observed byte count in the message** — it is a `log_event` payload field, not exception text. (B01-06 adds a sibling `SaltsMissing` for the *absent-file* case, sharing this category — two conditions, one recovery path, same user-facing message. Do not merge them, and do not add a third.)
  - **Every raise inside an `except` block uses `from None`.** `raise DatabaseKeyingFailed(db_name=db_name) from None`. This is the line the leak-scanning test below is actually checking: `from e` leaks the driver text via `__cause__`, and a *bare* `raise` leaks it via implicit `__context__` — measured, both fail; only `from None` passes.

**Docs:** `docs/CHANGELOG.md` entry. Update `docs/architecture/data-flows/key-derivation.md`: name the actual modules/classes you built in the diagram and prose, and correct any within-the-law detail that differs from the seeded version.

**Acceptance criteria:** Known-vector test: same passphrase+salt reproduces the same 64-char hex across runs; wrong-size salt files (191, 193, 0 bytes) rejected with a recovery-category error; `repr`/`str` leak nothing under direct call and inside f-strings/tracebacks; a forced keying failure's exception chain is scanned by the test for absence of hex/PRAGMA/passphrase substrings — **scan the fully rendered chain** (`traceback.format_exception(...)`), not `str(err)`, since `__context__` is where the leak actually appears and `str(err)` is safe by construction; the same scan is applied to `err.to_payload()`; `relock()` behavior verified; Docs contributions landed.

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
- **Custom migration manager — decided in BD-004, see ADR `B-004`. Build exactly this; CH-04, CH-09, CH-12 and CH-13 all extend it.** M1 mounts **exactly one** database: `conversation_db`. Its `0001_init.sql` creates only the migration-tracking meta table — the `turns`/`sessions` schema is CH-04 scope (§18) and must not appear here. The manager itself is written for all six from the start.

  - **Layout: six independent chains.** `lilith/data/migrations/<db_name>/NNNN_snake_case.sql`, where `<db_name>` is one of the six names in B01-04's salt-index constant (`ucl_db`, `calendar_db`, `contacts_db`, `finance_db`, `memory_db`, `conversation_db`). Each chain numbers from `0001` independently. Before running anything, validate the chain: four-digit prefixes, contiguous from `0001`, no duplicates — a gap or repeat raises `MigrationFailed`, it is not a warning.
  - **Resolve the directory with `importlib.resources.files("lilith.data.migrations").joinpath(db_name)` — never `Path(__file__).parent`.** This is what makes §07's PyInstaller `--onedir` bundle work from one code path with no `sys._MEIPASS` branch. Add `lilith/data/migrations/**/*.sql` to the package data so the files are installed and, later, collected into the bundle.
  - **Tracking table** — this is B01-05's "`schema_version` or equivalent meta" table, and it is the equivalent, not an integer. `0001_init.sql` for `conversation_db` contains exactly this and nothing else:

    ```sql
    CREATE TABLE IF NOT EXISTS schema_migrations (
      version    INTEGER PRIMARY KEY,   -- the NNNN from the filename
      filename   TEXT NOT NULL,
      checksum   TEXT NOT NULL,         -- SHA-256 hex of the file's bytes
      applied_at TEXT NOT NULL          -- ISO-8601 UTC
    );
    ```

    The manager must not create this table itself — it belongs to migration `0001` of every chain. To read a table its own first migration creates, query `sqlite_master` first; absent means "nothing applied yet". The tracking row for `0001` is inserted **inside `0001`'s own transaction**, which is legal because SQLite shares a transaction between DDL and DML. No migration is exempt from tracking.
  - **Checksum every applied migration on every startup.** Re-hash each recorded file and compare. Halt with `MigrationFailed` on: a mismatch, a recorded migration whose file is missing, or an unrecorded file numbered at or below the highest applied version. The error names the file (the script *name* only — never its SQL, §16).
  - **Idempotency means both readings, and tracking is the guarantee.** The manager never re-runs a recorded migration; scripts additionally use `IF NOT EXISTS` where it costs nothing. Do not treat `IF NOT EXISTS` as the mechanism — it cannot make an `UPDATE`/`INSERT` idempotent.
  - **Pre-migration backup (§06 Phase 7 — mandatory, and previously missing from this task).** When a database has pending migrations, *before* the first `BEGIN`, run `VACUUM INTO` to `APP_INTERNAL_DIR/backups/pre-migration-<timestamp>/<db_name>.db` (§03's same-key backup API; §04's `backups/`). A boot with nothing pending copies nothing. `VACUUM INTO` must run outside a transaction and **fails if the target path already exists** — hence a fresh timestamped directory, never a fixed filename. Delete the previous `pre-migration-*` set only after the whole run succeeds, so exactly one survives in the steady state and a failed run keeps both. This is **not** §29's six-database atomic set, which arrives at CH-09.
  - **One explicit transaction per migration**, not per run: `BEGIN` → statements → insert tracking row → `PRAGMA user_version = NNNN` → `COMMIT`; on any exception `ROLLBACK` then raise. A failure therefore leaves the database at a *valid earlier version*, with earlier migrations applied and recorded. `user_version` is a redundant marker for out-of-app inspection (verified transactional); the table is the source of truth.
  - **Two mechanical rules that are the whole point of the transaction.** Both were measured; both are what an unbriefed implementer gets wrong:
    - Write `BEGIN` explicitly. Python's `sqlite3` opens an implicit transaction before DML but **not before DDL** — `in_transaction` is `False` after a bare `CREATE TABLE`, so DDL executed without an explicit `BEGIN` runs in autocommit and §03's guarantee is satisfied in wording only.
    - **`Connection.executescript()` is forbidden here.** It issues a `COMMIT` before running and does not roll back; a script failing at its third statement leaves the first two committed. Split multi-statement files with `sqlite3.complete_statement()` and run one `execute()` per statement. When deciding whether a split buffer is skippable, a buffer counts as empty only if *every* line is blank or a `--` comment — testing `buf.startswith("--")` silently discards the statement following a leading comment, and every migration file has one.
  - **Table rebuilds — the `-- lilith:rebuild` marker.** SQLite's `ALTER TABLE` cannot drop or retype a column; the documented rebuild requires `foreign_keys = OFF`, and **that PRAGMA is silently ignored inside a transaction** (`defer_foreign_keys` does not substitute — the rebuild then fails at `COMMIT`). So the manager, not the script, owns it: a script whose first line is exactly `-- lilith:rebuild` runs as `PRAGMA foreign_keys = OFF` → `BEGIN` → statements → tracking row → `PRAGMA foreign_key_check` (non-empty result aborts the transaction) → `COMMIT`, with `PRAGMA foreign_keys = ON` restored in a `finally` so the failure path restores it too. Ordinary migrations never touch the PRAGMA, and no migration file may contain `BEGIN`, `COMMIT`, or a `foreign_keys` PRAGMA. No rebuild migration exists in M1; the path is built now so CH-12/CH-13 do not improvise around §03's connection sequence.
  - **Forward-only.** No down migrations, no `--dry-run`, no squashing. Undo is "restore the pre-migration backup" (§29) — which is exactly what the mandatory backup above guarantees exists.
  - **Any failure halts the whole application**, not just the affected database, and never repairs or deletes (§06, standards).
- `log_event()` M1 shim in `data/ucl.py` (permanent signature `log_event(event_type: str, payload: dict)`): JSON lines to `LOG_DIR / "dev.log"`; catches its own exceptions (telemetry never crashes the main path — standards); payload discipline per the plaintext-logs boundary.
- **Error handling, per ADR `B-003` — the conventions are decided; implement, do not re-derive.**
  - Every `error.*` payload comes from `err.to_payload()`. Do not build one by hand, and do not add fields to it at the call site; a fact worth logging that is not in the declared set belongs in a non-`error.*` event.
  - `data/db.py` raises `DatabaseKeyingFailed(db_name=…) from None` (B01-04's class) — this task does not define a second keying exception.
  - Migration failure raises a new `MigrationFailed(UnrecoverableError)`: `recovery_category = RecoveryCategory.DATABASE_CORRUPT`, `component = "data.db"`, identifiers `db_name` and `migration: str` (the script *name*, e.g. `"0001_init.sql"` — a non-secret identifier; **never** the failing SQL, which §16 forbids outright). Raised `from None` inside the transaction's `except`, after rollback.
  - `log_event()`'s own failure handler writes `sanitize_exception(exc)` to stderr — never the raw exception. This is the standards' "logged to stderr and counted, but never propagates", made §16-compliant.

**Docs:** `docs/CHANGELOG.md` entry. Update the connection-sequence portion of `docs/architecture/data-flows/key-derivation.md` and the `data/` layer names in `docs/architecture/01-containers.md` to match the real modules. The migration manager's own two pages already exist and were written with the decision (`docs/runbook/add-a-schema-migration.md`, and Phase 7 of `docs/architecture/data-flows/startup-sequence.md`) — verify both still describe what you built, and correct them if they do not.

**Acceptance criteria:** Real-SQLCipher tests (no mocks, §08): create → key → open → verify succeeds; wrong passphrase surfaces as `DatabaseKeyingFailed` (and the file is untouched); `PRAGMA journal_mode` returns WAL; migration runner applied twice is a no-op the second time; a deliberately broken migration script rolls back and raises `MigrationFailed` whose rendered chain and payload contain no SQL, and after reopening the database the failed script has left **nothing** behind (this is the test that catches an `executescript()` implementation — it passes trivially if the runner never actually failed, so assert on a reopened connection); editing an applied script's bytes halts the next startup with `MigrationFailed` naming the file; a chain with a gap or a duplicate number halts; a database with pending migrations produces a `pre-migration-<timestamp>/` set before applying and prunes the previous set only on success, while a boot with nothing pending creates no backup at all; `PRAGMA user_version` matches the highest applied `version` row; a fixture migration marked `-- lilith:rebuild` completes a column-drop rebuild with `PRAGMA foreign_key_check` clean, referencing rows intact, and `PRAGMA foreign_keys` back to `1` **on both the success and the failure path**; a cross-thread connection-sharing attempt is caught by the discipline (factory API makes it structurally awkward and tests document the rule); `log_event` writes valid JSON lines and survives an unwritable log dir without raising *and without writing a raw exception to stderr*; Docs contributions landed.

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
- **Error handling & the recovery vocabulary, per ADR `B-003` — this is the task that consumes the enum.**
  - **`telemetry.install_sanitizer()` is the first statement of startup**, before Phase 1. It is process setup, not an eleventh phase: nothing may log before the root handlers carry the filter. Add log handlers only via `telemetry.add_handler()`.
  - **The top-level handler is `except UnrecoverableError`** — that is what the two-child split exists for. Its branch prints/dialogs `err.message`, emits `log_event("error.recovery.<state>", err.to_payload())`, and exits non-zero. There is no lookup table mapping exception types to severity, and no `except Exception` catch-all above it; an unhandled non-Lilith exception is the excepthook's job and is redacted there.
  - **The halts this task raises**, all `UnrecoverableError`, all with the §06/§25 message verbatim as the class `message`, all raised `from None`:

    | Condition | Class | `recovery_category` |
    |:--|:--|:--|
    | Lock held by a live process | `AlreadyRunning` | `ALREADY_RUNNING` |
    | Phase 2 permission verify fails | `PermissionsInvalid` | `PERMISSIONS_INVALID` |
    | Databases exist, `salts.dat` absent | `SaltsMissing` | `SALTS_MISSING` |
    | Databases exist, no `master_passphrase` | `CredentialMissing` | `CREDENTIAL_MISSING` |

    `KeyringUnavailable` / `KeyringInsecure` (B01-03) and `DatabaseKeyingFailed` / `MigrationFailed` (B01-04/05) propagate to the same handler unchanged — do not re-wrap them.
  - **`AlreadyRunning` carries the `psutil`-derived PID as an identifier, not in the message.** §06 fixes the user-facing string as `"Lilith is already running"`; the PID enriches the *payload*. The flock result alone gates the refusal.
  - **The bootstrap CLI's refusal when databases exist is not an exception** — it is a normal CLI exit with guidance. Exceptions are for the startup path; do not manufacture a recovery category for a deliberate user-facing refusal.
  - Startup with neither salts nor databases is **not** an error either: it is the §25 classification pointing at the bootstrap CLI, and it touches nothing.

**Docs:** `docs/CHANGELOG.md` entry. Update the status line of `docs/architecture/data-flows/startup-sequence.md` (built-subset state). Write the first three runbook procedures in `docs/runbook/` per its writing rule (numbered steps, exact commands, expected outcomes, telemetry events emitted): *bootstrap a fresh machine*, *start / stop / verify*, *second-instance & stale-lock behavior*.

**Acceptance criteria:** Scripted end-to-end on Linux: bootstrap → start → phase log shows the ordered sequence → SIGTERM → exit code 0, lock removed, WAL flushed; second concurrent start refused with the exact §06 message while the first keeps running; kill -9 then restart cleans the stale lock and logs `error.crash_recovery`; bootstrap refuses when a database exists; salts-missing-with-databases halts with the §06 recovery message; startup with no salts and no databases points to the bootstrap CLI and touches nothing; every root-logger handler carries the `SanitizingFilter` after startup (assert it, since a directly-attached handler is a silent hole); an exception deliberately raised past the top-level handler produces a redacted excepthook line and no traceback in `dev.log`; Docs contributions landed.

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
