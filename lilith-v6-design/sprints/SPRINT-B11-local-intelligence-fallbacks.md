# SPRINT-B11 — Local Intelligence & Fallbacks

**Sprint ID:** BUILD-11  
**Chapter:** CH-11. **Status:** DRAFT 2026-10-26 (manager, autopilot session 3).  
**Prerequisites:** CH-01 through CH-10 built and audited. **Law:** `BUILD_GUIDE.md` §5 CH-11; `s12.html` (Ollama fallback, installer SEC-017/SEC-026, endpoint SEC-008, provider visibility), `s05.html` (tiers), `s02.html` (credentials table: `ollama_bearer_token`), `s14.html` (tokenization bypass for local inference), `s16.html`, `standards.html`.

## Open decisions (manager decides under AUTONOMOUS-DECISIONS)

| Brief | Value the law leaves open | Decision |
|:--|:--|:--|
| BD-048 | Local model tag for "the 8B model". | `llama3.1:8b`, one constant `OLLAMA_MODEL`; Tier 2 uses the same tag (§12 names no second model). |
| BD-049 | Pinned per-release installer SHA-256 values cannot be fetched from the sandbox. | The pin table (`OLLAMA_INSTALLER_PINS`: release -> platform -> sha256) is application source. Tests use a fixture release with a locally computed hash. Filling real release hashes is **developer-only** (recorded in HANDOFF); until then the table has no real release and the installer refuses with `install_integrity_failed`-class "no pinned release" (fail closed). |
| BD-050 | Tier 1 routing detail: §05 says conversational local, artifact cloud; §12 `select_provider` is per-key. | Selection is per **mode**: Anthropic key present -> Anthropic for both modes (§12 order wins); no key: Tier 1 conversational -> Ollama, Tier 1 artifact -> `missing_cloud_key`; Tier 2 both -> Ollama; Tier 0 -> `missing_cloud_key`. |
| BD-051 | Local conversational caps. | Same caps as cloud (`<=50` output tokens target; provider `max_tokens` 100 like Anthropic, AD-referenced). Artifact mode has no fixed cap. |

## Goal

Tier 1/2 machines without an Anthropic key answer locally: OpenAI-compatible Ollama adapter, endpoint verification, tier-gated provider selection, a hardened consent-gated installer/model-pull flow with a resumable marker, and a truthful always-visible provider indicator (shell + tray). No LiteLLM, no other local runtime, no GPU-driver installation beyond what the Ollama installer does.

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-11)

- [ ] Phase-4 validation passes as written: on a Tier 1 machine with no Anthropic key, the app detects/installs Ollama, warms the 8B model, and answers queries locally.
- [ ] Provider selection follows §05/§12 tier rules; status indicator reflects the active provider truthfully.

The first box has a **developer-only live part** (a real install and multi-GB pull on a Tier 1 machine); local evidence is a fake-Ollama-server end-to-end test.

## Context every agent must have

Read `standards.html`, the law pages above, this sprint, `tasks/00-AGENT-BRIEF.md`. Tests use real SQLCipher where a DB is touched, never DB mocks; network is faked with a local `httpx`/`asyncio` server on 127.0.0.1 or `httpx.MockTransport`. Seams: `lilith/logic/llm.py` (`AnthropicProvider`, `complete`/`complete_events`, telemetry payloads), `lilith/app.py` (`provider_factory` at ~L291/L539, `_build_lock_tray` ~L1643, `_save_api_key`), `lilith/platform/session_state.py` (`CapabilityProfile.tier`, `local_llm_eligible`), `lilith/platform/keyring.py` (add `OLLAMA_BEARER_TOKEN`), `lilith/errors.py` (`CloudKeyMissing`, recovery categories), `lilith/config.py`. The `openai==2.44.0` dependency is added by the manager before B11-01 (pyproject + requirements).

### [B11-01] Ollama provider adapter
**Type:** [IMPLEMENT]. **Law:** s12 (Adapter contract, Ollama fallback, Budgets, Context safety, Telemetry).  
**What to build:** `lilith/logic/ollama.py` with `OllamaProvider(mode, *, client=None)` implementing the same `complete(messages, system, stream=True)` and `complete_events(...)` contract as `AnthropicProvider` via `openai.AsyncOpenAI(base_url=<config>, api_key=<bearer or "ollama">)`. System blocks are flattened to one system message (no `cache_control`). Base URL from `config.json` (default `http://127.0.0.1:11434/v1`); bearer token only from keychain `ollama_bearer_token` (add the constant; never config). Emit `llm.call.start`/`llm.call.complete` with provider `"ollama"`. Map openai errors to `LlmCallFailed`. `complete_events` yields text only (artifact tools never run locally on Tier 1; on Tier 2 the artifact path calls `complete`).  
**Docs:** extend `docs/architecture/components/llm-provider.md`, `docs/CHANGELOG.md`.  
**Acceptance:** tests against a local fake OpenAI-compatible streaming server: deltas, token usage, caps, bearer header present only when keychain holds it, nothing bearer-like in config, telemetry fields, error mapping.

### [B11-02] Endpoint verification and port-hijack block
**Type:** [IMPLEMENT]. **Law:** s12 (SEC-008, AC-004, `error.ollama.port_hijack`, `error.ollama.verify_failed`).  
**Depends on:** B11-01.  
**What to build:** `verify_ollama_endpoint()` queries `/api/version` (validate JSON shape) and `/api/tags` for the model; returns a result enum (`ok`, `unreachable`, `port_hijack`, `model_missing`). `OllamaProvider` refuses to send any context until a successful verification this session (and after any failure it blocks outflow and logs the UCL error event with a payload-safe shape). Loopback-only unless a custom base URL is configured.  
**Docs:** llm-provider.md, `docs/runbook` row for the port-hijack warning, CHANGELOG.  
**Acceptance:** fake servers: bound-but-silent port, wrong-metadata server, missing model, healthy; assert no completion request reaches the server when verification failed; events logged to a real UCL.

### [B11-03] Tier-gated provider selection and routing wiring
**Type:** [IMPLEMENT]. **Law:** s12 (`select_provider`), s05 (tier definitions), s13 only as the consumer.  
**Depends on:** B11-01, B11-02.  
**What to build:** `select_provider(mode, profile)` per BD-050, returning a provider or raising `CloudKeyMissing`; wire it into the `provider_factory` default in `lilith/app.py` so the composition root picks per turn (key read each call, AD-031 style, so removing the key falls back immediately). Tokenization bypass (§14) for local providers is a flag the CWM caller consults; do not weaken the cloud path. Missing model/daemon is not handled here (B11-05).  
**Docs:** llm-provider.md, router.md, `docs/architecture/data-flows` provider-selection note, CHANGELOG.  
**Acceptance:** table-driven tests over (key present/absent) x (tier 0/1/2) x (mode); key removal mid-session switches provider; Tier 0 without key raises `CloudKeyMissing`.

### [B11-04] Installer download and integrity core
**Type:** [IMPLEMENT]. **Law:** s12 (SEC-017, SEC-026, AC-005/006/007, `install_source_refused`, `install_integrity_failed`, `disk_full`).  
**What to build:** `lilith/platform/ollama_install.py`: compile-time host allowlist (constant tuple, no runtime extension); download with TLS verification always on and no override parameter or env hook; redirects checked hop by hop against the allowlist, refusal deletes the partial and logs `error.ollama.install_source_refused`; streaming SHA-256 against `OLLAMA_INSTALLER_PINS` (BD-049), mismatch deletes the artifact and logs `error.ollama.install_integrity_failed` with no run-anyway path; `verify_artifact(path, release)` reusable for resume re-verification; 15 GB free-space preflight (`error.ollama.disk_full`, payload has available/required). Do not execute anything in this task.  
**Docs:** create `docs/architecture/components/ollama-installer.md`, CHANGELOG.  
**Acceptance:** `httpx.MockTransport`/local server tests: allowed host, off-allowlist redirect, tampered bytes, unpinned release, low disk; mutation check that removing the host check turns a test red; grep proves no `verify=False`.

### [B11-05] Setup flow: consent, marker, execution, model pull
**Type:** [IMPLEMENT]. **Law:** s12 (Auto-Setup, EARS list, AC-001/002/003/008/009, error table).  
**Depends on:** B11-02, B11-03, B11-04.  
**What to build:** `lilith/logic/ollama_setup.py` state machine (`detect -> disclosure -> download -> verify -> install -> start_daemon -> pull_model -> ready`) persisted as a marker in `config.json` (atomic write; stores state, release, artifact path, consent flag — never secrets). Disclosure data (size, time, reboot warning) is a returned object; the UI shows it; download starts only after `accept()`. Resume after restart re-verifies the artifact hash before executing (consent persisted but hash re-checked, AC-002/007). Installer execution goes through an injectable runner whose real implementation uses the OS elevation mechanism only (pkexec/polkit on Linux, macOS Authorization Services via `osascript ... with administrator privileges`, Windows `runas`/ShellExecute verb) — never silent sudo; on non-zero exit log `error.ollama.install_failed` and installer output to `logs/setup.log`. Model pull via `POST /api/pull` streaming with progress callback, resumable; `error.ollama.pull_failed`. On success log `sync.ollama.install_verified` (version, hash) and warm the model with a keep-alive request.  
**Docs:** ollama-installer.md, `docs/runbook` setup/recovery rows, CHANGELOG.  
**Acceptance:** fake daemon + injected runner: happy path, consent-gated download, disk-full halt, interrupted-then-resumed with and without tampered artifact, install failure, pull drops then resumes, audit event present. The real installer run is developer-only.

### [B11-06] Provider status indicator (shell and tray)
**Type:** [IMPLEMENT]. **Law:** s12 (Provider Visibility, SEC-008), s26 indicator note.  
**Depends on:** B11-03.  
**What to build:** a small `ProviderStatus` model (`anthropic`, `ollama`, `none`, plus a transient `setting_up` with progress text) published on the UI bus; a persistent label in the main window shell and a tray tooltip/menu line (disabled action) updated on every selection change, key save/removal, and setup progress. The indicator reads what `select_provider` actually chose, not a config guess.  
**Docs:** `ui-shell.md`, `settings-screen.md` if touched, CHANGELOG.  
**Acceptance:** offscreen Qt tests: key saved -> "Anthropic Cloud"; key removed on Tier 1 -> "Local Ollama" immediately; verification failure -> "none/blocked"; tray menu line matches. Real desktop tray is developer-only.

### [B11-07] Startup wiring: detect, disclose, set up, indicate
**Type:** [IMPLEMENT]. **Law:** s12 (`select_provider` flow, AC-001/002, Provider Visibility), s25 only for the dialog being a plain modal.  
**Depends on:** B11-05, B11-06 (added by the manager 2026-10-26: the sprint draft had no task that connects the setup machine to the app).  
**What to build:** at app start (after the capability profile and before the first chat turn is allowed), when `selected_provider_id("conversational", profile)` is `ollama`: run `OllamaSetup.run()` off the UI thread; at `disclosure` show a modal built from `Disclosure` (size, time, reboot warning, Accept / Not now); `accept()` then `run()` again with progress posted to `bus.post_provider_status("setting_up", text)`; on `ready` publish `ollama`; on any typed failure publish `none` with the error's user message (integrity, source refused, disk full, pull failed with Resume, port hijack). A leftover non-`ready` marker resumes without a new prompt when consent is stored (AC-002). Saving an Anthropic key during setup does not cancel it but the indicator follows `selected_provider_id`. When the provider is `ollama` and verification currently fails, the indicator must show `none`, not `ollama` (truthfulness, DoD box 2): `_publish_provider_status` consults the last verification result.  
**Docs:** `ui-shell.md`, `ollama-installer.md`, runbook rows, CHANGELOG.  
**Acceptance:** offscreen Qt tests with a fake daemon and injected runner: disclosure shown once, decline leaves `none` and downloads nothing, accept reaches `ready` and the indicator says Local Ollama, a restart with a stored marker resumes, a failed verification shows `none`.

### [B11-08] Phase-4 validation and chapter close
**Type:** [VALIDATE]+[DOCS]. **Depends on:** all above.  
**What to build:** one end-to-end test: Tier 1 profile, no key, fake absent Ollama -> disclosure -> accept -> verified fake installer -> daemon -> pull -> warm -> a chat turn answered locally through the real `respond` path, indicator "Local Ollama", UCL has the expected event chain. Write `docs/audits/CH-11.md` (DoD trace, developer-only items: live install/pull on a Tier 1 machine, real pinned hashes, tray on desktop, GPU). Sweep status lines of architecture diagrams; journal, index, HANDOFF.  
**Acceptance:** all gates green (`pytest`, `ruff`, `basedpyright`, `lint-imports`), audit lists every EARS requirement as built or developer-only.

## Sequential order

```text
manager: add openai dep -> B11-01 -> B11-02 -> B11-03 -> B11-06
                         B11-04 (parallel with B11-01..03: different files) -> B11-05 (needs 02,03,04)
B11-05, B11-06 -> B11-07 (wiring) -> B11-08
```
