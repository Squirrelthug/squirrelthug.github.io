# SPRINT-B02 — Voice I/O Pipeline

**Sprint ID:** BUILD-02
**Chapter:** CH-02 (see `BUILD_GUIDE.md` §5) · **Kanban:** [Issue #2](https://github.com/Squirrelthug/squirrelthug.github.io/issues/2) on [Project 46 — Lilith v6 Build](https://github.com/users/Squirrelthug/projects/46)
**Status:** Draft — blocked on four open decision briefs (`BD-005`…`BD-008`) below and developer review of this sprint PR on the design site. Nothing of CH-02 is built until those decisions are resolved and the PR merges.
**Law for this sprint:** §05, §09, §10, §11 (+ §06 Phase 1 / Phase 9 / Shutdown step 1, §08 testing conventions, §01/§04/§16 foundations) — https://squirrelthug.github.io/lilith-v6-design/sections/s05.html (…s09, s10, s11, s06, s08, s01, s04, s16)
**Prerequisites:** CH-01 (`SPRINT-B01-foundation.md`) built and audited (`docs/audits/CH-01.md` on `feature/b01-08-setup`). Until CH-01's POSIX test run and MASTER fresh-clone walkthrough close `B01-09` steps 4–5 and merge the CH-01 PR chain to `main`, CH-02 task branches stack on `feature/b01-08-setup`.

## Open decisions blocking this sprint (added 2026-10-19)

Four groups of choices below are required by tasks in this sprint but are **not settled by the frozen law**. Per `BUILD_GUIDE.md` §2/§3 and `docs/decisions/README.md`, an agent must not invent values, schemas, or packages where a section is silent. Each brief below must be resolved into a build ADR (`docs/adr/B-NNN-*.md`) and the affected task text in this file edited to state the decision as instruction before that task starts.

| Brief | Decision | Blocks | Kanban | Status |
|:--|:--|:--|:--|:--|
| BD-005 | `CapabilityProfile` dataclass schema, `lilith.platform.session_state` module/attribute placement, GB/GiB threshold boundaries, and macOS Apple Silicon (`ctranslate2` CPU-only) execution mapping | B02-01, B02-05, B02-06 | sub-issue of [#2](https://github.com/Squirrelthug/squirrelthug.github.io/issues/2) | **OPEN** |
| BD-006 | Audio queue bounds (`audio_q`, `playback_q`, `transcription_q` / `utterance_q`), full-queue policy, `44.1`/`48 kHz` resampling blocksize, hot-plug retry limits, and audio error/telemetry classes | B02-02, B02-03, B02-04, B02-06 | sub-issue of [#2](https://github.com/Squirrelthug/squirrelthug.github.io/issues/2) | **OPEN** |
| BD-007 | Silero VAD runtime distribution (no-`torch` ONNX vs package), `480`-frame (`30ms`) chunk framing vs `512`-sample Silero v5/v6 window, Whisper language/beam defaults, and `voice.stt.start` payload schema | B02-04, B02-05 | sub-issue of [#2](https://github.com/Squirrelthug/squirrelthug.github.io/issues/2) | **OPEN** |
| BD-008 | `MODELS_DIR` (`APP_INTERNAL_DIR/models/`) layout & model-weight provisioning, Kokoro `135` WPM → `speed` multiplier mapping, and sentence/clause chunker delimiters | B02-04, B02-05, B02-06 | sub-issue of [#2](https://github.com/Squirrelthug/squirrelthug.github.io/issues/2) | **OPEN** |

### Details & allowed options for each open decision

1. **BD-005 — Hardware profile schema, placement, boundary arithmetic & macOS Whisper mode (`sections/s05.html`, `sections/s10.html`, `sections/s01.html`):**
   - **What the law fixes:**
     - Three tiers (`s05.html:29, 32-37, 56-76`): **Tier 0** (`< 8 GB VRAM`: Whisper `base` STT `int8` CPU, Kokoro TTS on CPU), **Tier 1** (`8 GB to 20 GB VRAM`, diagram `VRAM >= 8 GB?` at `s05.html:72`, e.g. RTX 3060 12GB, Apple M-series with `16GB+` unified RAM: Whisper `small` STT `float16` GPU, Kokoro TTS on CPU), **Tier 2** (`>= 20 GB VRAM` at `s05.html:36, 69`: Whisper `small` STT, Kokoro TTS on CPU).
     - Detection commands (`s05.html:39-44`): Windows/Linux NVIDIA via subprocess `nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits` with a strict `1000ms` execution timeout, parsing VRAM directly in MB (`s05.html:41`); macOS (Apple Silicon) unified memory via `sysctl hw.memsize` (`s05.html:42`); system RAM via `psutil.virtual_memory().total` (`16GB` required for local LLM execution in Tier 1+, `s05.html:43`).
     - Non-NVIDIA / non-Apple Silicon hardware returns no VRAM during detection and implicitly falls back to **Tier 0** (`s05.html:50`).
     - Stored once during early boot (Phase 1, `s06.html:35`) as an immutable `CapabilityProfile` dataclass in `lilith.platform.session_state`, never saved to the database (`s05.html:46`).
   - **What the law leaves open (options to decide):**
     - *Placement of `lilith.platform.session_state` (`s05.html:46` vs `s01.html:48-51`):* (a) a dedicated submodule `lilith/platform/session_state.py` re-exported on `lilith/platform/__init__.py` (sanctioned addition to the §01 diagram like `errors.py`, `telemetry.py`, and `bootstrap.py` in CH-01), or (b) a namespace/holder object `session_state` defined directly in `lilith/platform/__init__.py` so no new file is added under `lilith/platform/`.
     - *Exact field names and types of `CapabilityProfile`:* e.g. `tier: Literal[0, 1, 2]`, `vram_mb: int`, `system_ram_bytes: int`, `whisper_model: Literal["base", "small"]`, `whisper_device: Literal["cpu", "cuda"]`, `whisper_compute_type: Literal["int8", "float16"]`.
     - *Threshold conversion & multi-GPU parsing:* `nvidia-smi` reports integer MiB (where a marketed 8 GB card often reports `7982`–`8192` MB usable total memory) while `sysctl hw.memsize` and `psutil.virtual_memory().total` report bytes. Options: (a) strict binary GiB (`8192` MB / `20480` MB and `8 * 1024**3` / `20 * 1024**3` / `16 * 1024**3` bytes), (b) decimal GB (`8000` MB / `20000` MB), or (c) binary GiB for `sysctl`/`psutil` with an `nvidia-smi` marketed-card floor (e.g. `>= 7900` MB for 8 GB, `>= 19500` MB for 20 GB); plus whether multi-GPU `nvidia-smi` output takes `max(...)` or the first line, and whether `< 16GB` system RAM on a `>= 8 GB` discrete-VRAM host downgrades the whole profile to Tier 0 or only gates CH-11 local LLM while keeping Tier 1 Whisper `small`.
     - *macOS Apple Silicon guard & `faster-whisper` execution mode:* `sysctl hw.memsize` exists on Intel Macs too, so Apple Silicon detection must guard on `IS_MAC` plus architecture (`platform.machine() == "arm64"` or `sysctl -n hw.optional.arm64`). Furthermore, `s05.html:35` states `Whisper small STT (float16 GPU)` while `s10.html:36` states `small model (float16 quantized) executed on CUDA GPUs or optimized CPU paths (Apple Silicon NEON)`, and `HANDOFF.md:48` flags that `faster-whisper` (via `ctranslate2`) runs CPU-only on macOS (where CTranslate2 CPU supports `int8` / `float32`, not CUDA `float16`). Options: (a) on `IS_MAC` Tier 1/2, select `model="small", device="cpu", compute_type="int8"` (or `"float32"`), or (b) attempt `float16` and catch `ValueError`/`RuntimeError` to fall back to `device="cpu", compute_type="int8"`.

2. **BD-006 — Audio queues, `44.1`/`48 kHz` resampling blocksize, hot-plug retry limits & error taxonomy (`sections/s09.html`, `sections/s10.html`, `sections/s11.html`, `sections/s06.html`):**
   - **What the law fixes:**
     - Capture (`s09.html:33`): `sounddevice.InputStream` locked to `16 kHz` (`samplerate=16000`) `mono` (`channels=1`) `float32` (`dtype="float32"`) with `blocksize=480` frames (`30ms`), copying each chunk into thread-safe `audio_q` with no allocations (beyond the copy) or model inference on the callback thread.
     - Playback (`s09.html:34`, `s11.html:37`): `sounddevice.OutputStream(channels=1, samplerate=24000, blocksize=1024)` (`dtype="float32"`), draining a bounded `playback_q`, padding underruns with silence, and computing RMS for orb animation.
     - Queue naming between VAD and STT: `s10.html:51, 75` names `transcription_q` in both prose and diagram; `s09.html:52` labels the same queue `utterance_q` in its diagram (`s10.html` is primary for STT).
     - Resampling fallback (`s09.html:36`): if a mic rejects native `16 kHz`, open at default native rate (`44.1 kHz` or `48 kHz`) and resample down to `16 kHz` in the VAD thread via `numpy.interp`.
     - Stream restart & hot-plug recovery (`s09.html:37`): on stream exceptions or status flags (`underflow`/`overflow`), close the active stream, re-enumerate devices, select the system's new default device, and restart.
   - **What the law leaves open (options to decide):**
     - *Queue `maxsize` values and full-queue policy:* numeric `maxsize` for `playback_q` (explicitly "bounded `playback_q`" at `s09.html:34` / "bounded PCM queue" at `s11.html:37`), `audio_q`, and `transcription_q` (aliased as `utterance_q` if needed), and whether `audio_q` in the non-blocking PortAudio input callback drops the oldest or newest chunk on `queue.Full`.
     - *Resampling fallback input `blocksize`:* when opening `InputStream` at `44100` Hz or `48000` Hz (`s09.html:36`), whether `blocksize` scales to `30ms` (`1323` frames at `44100` Hz, `1440` frames at `48000` Hz) so each callback chunk resamples directly to `480` frames via `numpy.interp`, or uses a ring buffer before slicing `480`-frame (`30ms`) chunks.
     - *Hot-plug recovery backoff, retry cap, and `LilithError` / telemetry contract:* how many restart attempts and what backoff interval `audio.py` uses before surfacing a failure; what `RecoverableError` subclass(es) in `lilith/errors.py` (with which fixed `message`, `component`, and existing `RecoveryCategory` member per ADR `B-003`) represent audio/voice failures; and how `lilith/platform/audio.py` reports operational or error events without violating `import-linter` (`lilith.platform` is below `lilith.data` and cannot import `lilith.data.ucl.log_event` directly — callbacks/hooks injected by `logic`/`app.py` vs return values).

3. **BD-007 — Silero VAD runtime, `480`-frame (`30ms`) chunk framing, Whisper parameters & `voice.stt.start` payload (`sections/s10.html`):**
   - **What the law fixes:**
     - Silero VAD parameters (`s10.html:39-45`): `Input chunk size: 480 frames (30ms at 16 kHz sample rate mono float32)`, `Speech threshold: 0.5 (probability cutoff)`, `End-of-speech window: 600ms of contiguous silence (min_silence_duration_ms=600)`, `Padding: 250ms pre/post padding (speech_pad_ms=250)`.
     - STT package (`s10.html:32`): `faster-whisper (v1.2.1)` utilizing `CTranslate2` backend (MIT).
     - Telemetry (`s10.html:56-61`): `voice.stt.start` emitted when VAD identifies speech starting; `voice.stt.complete` emitted on successful transcription with payload `duration_ms`, `audio_len_ms`, `word_count`.
   - **What the law leaves open (options to decide):**
     - *Silero VAD package/model and `480`-frame (`30ms`) vs `512`-sample window:* `s10.html` does not name a PyPI package for Silero VAD. `onnxruntime==1.23.2` is already pinned in `s11.html:32` and `faster-whisper==1.2.1` bundles a Silero VAD ONNX model (`silero_vad_v6.onnx`), whereas the standalone `silero-vad` PyPI package pulls in `torch` (which `docs/audits/CH-01.md:57` verified is absent). Additionally, Silero VAD v4 ONNX accepts `480`-sample (`30ms` at `16 kHz`) chunks directly, whereas Silero VAD v5/v6 ONNX models require `512`-sample (`32ms` at `16 kHz`) windows per inference step. Options: (a) run Silero VAD on `onnxruntime==1.23.2` (zero `torch` dependency) using a rolling `512`-sample window fed by `480`-frame (`30ms`) `audio_q` chunks with `600ms` (`20`-chunk) silence and `250ms` (`9`-chunk / `4000`-sample) pre/post padding, or (b) run a Silero v4 ONNX asset that natively accepts `480`-frame (`30ms`) chunks on `onnxruntime==1.23.2`.
     - *`voice.stt.start` payload schema (`s10.html:58` vs `s08.html:41`):* `s10.html:58` names no payload keys for `voice.stt.start` (options: `{}` or `{"speech_threshold": 0.5}`).
     - *Whisper transcription parameters & empty transcripts:* whether `WhisperModel.transcribe()` locks `language="en"` or auto-detects (raised as an open question in the pre-freeze `checklist.html:363`, which is not law: its per-tier model names contradict `s05.html` and are ignored), uses `vad_filter=False` (since the dedicated Silero VAD worker thread already gated the utterance), and whether an empty/whitespace-only transcript still emits `voice.stt.complete` with `word_count=0` or is dropped before router dispatch.

4. **BD-008 — `MODELS_DIR` layout & provisioning, Kokoro `135` WPM speed mapping & clause chunker (`sections/s11.html`, `sections/s04.html`, `sections/s06.html`):**
   - **What the law fixes:**
     - `MODELS_DIR = APP_INTERNAL_DIR / "models"` (`s04.html:40, 73`, `lilith/platform/paths.py:101`).
     - `Phase 9 (Voice Pipeline Init): Load Whisper and Kokoro model files; open Sounddevice Streams.` (`s06.html:43`).
     - TTS pins & settings (`s11.html:32-38`): `kokoro-onnx==0.5.0`, `onnxruntime==1.23.2`, `sounddevice==0.5.5`; Apache 2.0 license in `licenses/`; voice `af_bella`, target speaking rate `135` WPM, mono `float32` PCM output; CPU-only ONNX Runtime provider for Tier 0, Tier 1, and Tier 2; `voice.tts.first_chunk` within `500` ms of `voice.tts.start` by synthesizing by sentence/clause and enqueueing the first playable PCM chunk as soon as Kokoro yields it; telemetry events `voice.tts.start (voice, chars)`, `voice.tts.first_chunk (latency_ms, frames)`, `voice.tts.complete (duration_ms, chunks, success)`.
   - **What the law leaves open (options to decide):**
     - *`MODELS_DIR` sub-paths and provisioning:* exact paths under `paths.MODELS_DIR` for Whisper (`download_root=paths.MODELS_DIR / "whisper"`) and Kokoro (`paths.MODELS_DIR / "kokoro" / "kokoro-v1.0.onnx"` and `"voices-v1.0.bin"`), and whether missing model files are downloaded via `python -m lilith.bootstrap` / a setup helper or on first Phase 9 init.
     - *Mapping `135` WPM (`s11.html:33`) to `kokoro-onnx`'s `speed: float` and `lang: str`:* `kokoro-onnx` accepts `speed: float` (default `1.0`) and `lang: str` (e.g. `"en-us"`), not an integer WPM. Decide the exact `speed` float constant (e.g. `1.0` or calibrated multiplier for `af_bella` at `135` WPM) and `lang="en-us"`.
     - *Sentence/clause chunker boundaries (`s11.html:35`):* exact punctuation split rule (`[.!?;:—,\n]+` with or without a minimum clause length) so `voice.tts.first_chunk` reliably fires within `500` ms of `voice.tts.start` without unnatural prosody splits.

---

## Goal

Sound in, text out; text in, sound out — both halves of the voice loop working independently on the dev machine, before any intelligence sits between them (`BUILD_GUIDE.md:115`). At sprint end, startup Phase 1 populates an immutable `CapabilityProfile` in `lilith.platform.session_state`, `sounddevice` input and output streams run with `16 kHz` mono `float32` capture (`480`-frame / `30ms` chunks) and `24 kHz` mono `float32` playback (`1024`-frame blocks from a bounded `playback_q` with silence underrun padding and RMS amplitude calculation), Silero VAD gates microphone audio into complete utterances on `transcription_q`, `faster-whisper` transcribes utterances according to the detected hardware tier, `kokoro-onnx` streams CPU-synthesized speech chunks (`af_bella`, `135` WPM) into `playback_q` with first audio within `500` ms, and startup Phase 9 plus shutdown step 1 manage the voice lifecycle cleanly.

### Definition of Done (verbatim from `BUILD_GUIDE.md` §5, CH-02)

- [ ] Speaking into the mic produces a correct transcript through the VAD→STT path (verified on real hardware, not only fixtures).
- [ ] An arbitrary text string is synthesized and audibly played through the chunk-queue path without underruns.
- [ ] Hardware detection returns the correct tier/mode on the dev machine and the CPU fallback path is exercised in tests.
- [ ] Unit tests cover the audio stream, Whisper inference, and Kokoro inference per §08 conventions.

---

## Context every agent must have

Each task below is worked by its own isolated agent. An agent receives, at minimum (`BUILD_GUIDE.md:50-55`):

1. **The Non-Negotiable Standards** — `../standards.html` (https://squirrelthug.github.io/lilith-v6-design/standards.html) — read first, every session. The floor below which code does not ship.
2. **The law sections listed on its task** — `../sections/sNN.html` (https://squirrelthug.github.io/lilith-v6-design/sections/sNN.html) — implemented *exactly as written*. If the task text and a section conflict, **the section wins**; if build work exposes a genuine gap or contradiction in the law, **stop and report** — the developer resolves it through a documented design session. Never improvise architecture in code.
3. **This file's header + its own task block.**

**Ground rules (from `BUILD_GUIDE.md` §2):**
1. **Only what is written gets built.** The section pages `../sections/s01.html`–`s29.html` are the law, implemented exactly as written.
2. **Standards are the floor.** `../standards.html` is read at the start of every agent session.
3. **Excluded means absent.** No router (`§13`), LLM (`§12`), CWM/PII tokenizer (`§14`), tools (`§15`), memory schema (`§18`), or GUI (`§22`/`§26`/`§27`/`§28`) code may be built in CH-02, and no secondary-endpoint (`kitchen_speaker`, WebSocket) code (`BUILD_SEQUENCING.md` §5 item 1) may appear.
4. **Validation gates are hard gates.** No embedding or vector dependency may enter `pyproject.toml` or `requirements.txt` (EXP-3, `BUILD_GUIDE.md` §6).

**Documentation is part of done (never broken, `standards.html:218-244`):** every task below has an explicit **Docs:** field naming its exact contributions in the build repo's `docs/` tree; a task whose code is merged without its named `Docs:` contribution is **not done**. Minimum for any task: its `docs/CHANGELOG.md` entry under `### CH-02 — Voice I/O Pipeline`. Any process passing data through more than two components requires a Mermaid flowchart in its wiki page with node labels linking to their respective wiki pages (`standards.html:233-237`).

### Starting state of the build repository (from CH-01)

- **Branch base:** CH-01 work sits on `feature/b01-08-setup` (audited in `docs/audits/CH-01.md`). Until the POSIX test sweep and MASTER fresh-clone run finish closing `B01-09` steps 4–5 and merge the CH-01 PR chain to `main`, branch B02 tasks in sequence from `feature/b01-08-setup` (`HANDOFF.md:27-28`).
- **Existing CH-01 files touched by CH-02:**
  - `lilith/platform/__init__.py` — defines `IS_LINUX`, `IS_MAC`, `IS_WINDOWS` once from `sys.platform` (`s04.html:59`). Feature code must import these flags rather than checking `sys.platform` or `os.environ` ad hoc.
  - `lilith/platform/paths.py` — defines `APP_INTERNAL_DIR`, `DB_DIR`, `LOG_DIR`, `MODELS_DIR`, `CACHE_DIR`, `BACKUP_DIR`, `SKILLS_DIR`, `EXTERNAL_BACKUP_DIR`. No path construction is permitted outside `paths.py` (`tests/unit/test_paths.py::test_no_path_construction_outside_paths_module` enforces this across `lilith/`).
  - `lilith/platform/audio.py` — currently a 4-line docstring placeholder (`"Placeholder. Filled by CH-02 (audio and hardware)."`). Filled by `B02-02` and `B02-03`.
  - `lilith/logic/__init__.py`, `lilith/logic/stt.py`, `lilith/logic/tts.py` — currently 4-line docstring placeholders (whose CH-01 docstrings say `"Filled by CH-03"`, recorded as a CH-01 sprint-header typo in `docs/audits/CH-01.md:98, 114`). `B02-04`/`B02-05` fill `lilith/logic/stt.py`, and `B02-06` fills `lilith/logic/tts.py` and updates `lilith/logic/__init__.py`. `lilith/logic/router.py` and `lilith/logic/cwm.py` remain docstring-only placeholders until CH-03.
  - `lilith/app.py` — implements the 10-phase §06 startup sequence and 5-step graceful shutdown. Currently Phase 1 (`_phase(1, PHASE_NAMES[0])` at `lilith/app.py:189`), Phase 9 (`_phase(9, PHASE_NAMES[8])` at `lilith/app.py:224`), and Shutdown step 1 (`_phase(1, "shutdown: audio streams stopped")` at `lilith/app.py:73`) are stubs; `B02-01` wires Phase 1 and `B02-06` wires Phase 9 and Shutdown step 1.
  - `lilith/data/ucl.py` — provides the Milestone-1 `log_event(event_type: str, payload: dict[str, Any]) -> str` dev-log shim writing JSON lines to `LOG_DIR / "dev.log"`.
  - `lilith/errors.py` & `lilith/telemetry.py` — implement the ADR `B-003` exception hierarchy (`LilithError` → `RecoverableError` / `UnrecoverableError` → concrete classes with fixed class-level `message`, `recovery_category`, `component`, keyword-only non-secret identifiers, `to_payload()`, and `raise ... from None`) and the root-handler `SanitizingFilter`.

### Layering & import-linter rule (critical for CH-02)

`pyproject.toml:66-76` enforces the downward-only 6-layer contract:

```
lilith.ui → lilith.logic → lilith.data → lilith.platform → lilith.telemetry → lilith.errors
```

- **`lilith.platform` is BELOW `lilith.data` and `lilith.logic`.** Modules inside `lilith/platform/` (`audio.py`, `session_state.py`, `paths.py`, `keyring.py`) **cannot** import `lilith.data.ucl.log_event` or anything from `lilith.logic`.
- **`lilith.logic` (`stt.py`, `tts.py`) is ABOVE `lilith.data` and `lilith.platform`.** It imports `log_event` from `lilith.data.ucl` (to emit `voice.stt.*` and `voice.tts.*`), `CapabilityProfile` / `session_state` and `MODELS_DIR` from `lilith.platform`, and streams/queues from `lilith.platform.audio`.
- **`lilith/app.py` sits at the package root** (outside the six subpackage layers) and coordinates `lilith.platform`, `lilith.data`, and `lilith.logic` during startup Phase 1, startup Phase 9, and shutdown step 1.

### Dependency rules (ADR `B-002` & `standards.html` Licensing Standards)

- Whenever a task adds a runtime dependency (`sounddevice==0.5.5`, `numpy`, `faster-whisper`, `kokoro-onnx==0.5.0`, `onnxruntime==1.23.2`, or a Silero VAD package if selected in `BD-007`), edit `pyproject.toml` only and regenerate `requirements.txt` with the exact ADR `B-002` command (`docs/runbook/add-or-update-a-dependency.md`):

  ```bash
  uv pip compile pyproject.toml --extra dev --universal --generate-hashes \
    --python-version 3.12 -o requirements.txt
  ```

- **Pinning rule:** Pin exact versions only where the frozen law states an exact pin (`kokoro-onnx==0.5.0`, `onnxruntime==1.23.2`, `sounddevice==0.5.5` in `s11.html:32`; `faster-whisper` is specified as `(v1.2.1)` in `s10.html:32`). Do **not** invent version pins the law does not give; let `uv pip compile` lock the resolved versions and hashes in `requirements.txt`.
- **RES-15 license check (`standards.html:250-254`, `docs/runbook/add-or-update-a-dependency.md` step 5):** verify every newly added and transitive package permits closed-source desktop use, end-user distribution, and commercial SaaS subscription sales, and record the check in the task report / PR. For `kokoro-onnx`, `s11.html:32` explicitly requires: *"Kokoro model and code are Apache 2.0 and must be listed in `licenses/`."*
- **Known platform constraints (`HANDOFF.md` §5, ADR `B-002`):**
  - `faster-whisper` (via `ctranslate2`) runs **CPU-only on macOS** (`HANDOFF.md:48`). Tasks `B02-01` and `B02-05` must honour `BD-005` so macOS Apple Silicon does not crash attempting CUDA `float16`.
  - `onnxruntime` (via `kokoro-onnx`) publishes **macOS 14+** (`macosx_14_0`) wheels only (`docs/adr/B-002-dependency-pinning.md:126-127`).

### Open items carried from the CH-01 audit (`docs/audits/CH-01.md` §6)

1. **POSIX test run and MASTER fresh-clone acceptance (`CH-01.md:105`):** Still pending on Linux/macOS to close `B01-09` steps 4–5; does not block authoring or executing CH-02 tasks on stacked branches (`HANDOFF.md:14, 28`).
2. **`python -m lilith.app` on Windows (`signal.pause()` at `lilith/app.py:231`, `CH-01.md:106`):** `_run_idle_loop()` in `lilith/app.py:229-231` calls `signal.pause()`, which is POSIX-only (`AttributeError` on `win32`). **No CH-02 task modifies `_run_idle_loop()`** — `B02-01` touches Phase 1 (`lilith/app.py:189`) and `B02-06` touches Phase 9 (`lilith/app.py:224`) and `Lifecycle.shutdown()` step 1 (`lilith/app.py:72-73`). Windows tests exercise `startup()` and `Lifecycle.shutdown()` directly in-process (as `tests/integration/test_seams.py` already does), while subprocess `SIGTERM` tests remain guarded with `@pytest.mark.skipif(sys.platform == "win32", ...)` unless the developer separately directs a cross-platform wait primitive before CH-05.
3. **Agent-worded error messages (`lilith/errors.py`, `CH-01.md:107-112`):** Any new `LilithError` subclass needed by CH-02 must have its class name, fixed `message`, `recovery_category`, and `component` settled in `BD-006` before implementation so agents do not invent unapproved recovery categories or strings, and `tests/unit/test_errors.py` must continue to pass unchanged.
4. **Kanban board / GitHub issues hygiene (`CH-01.md:113`):** `B02-07` ticks issue #2 (`CH-02`) and updates `BUILD_GUIDE.md` §4 only after the developer's live microphone and speaker runs pass.
5. **Placeholder docstrings in `lilith/logic/stt.py` and `lilith/logic/tts.py` (`CH-01.md:114`):** `lilith/logic/stt.py:3`, `lilith/logic/tts.py:3`, and `lilith/logic/__init__.py:1` currently say `"Filled by CH-03"` (from `SPRINT-B01-foundation.md:61`). `B02-04` and `B02-06` replace those docstrings with accurate CH-02 (§10 / §11) module docstrings.

### Testing discipline for CH-02 (`sections/s08.html`)

- **Unit tests (`tests/unit/`, `timeout 60 pytest tests/unit/`, `s08.html:32, 44, 55`):** Fast, isolated, deterministic, and runnable in headless environments without physical audio devices or multi-hundred-megabyte model downloads. Mock `sounddevice.InputStream`, `sounddevice.OutputStream`, `sounddevice.query_devices`, `sounddevice.query_hostapis`, `subprocess.run` (`nvidia-smi` / `sysctl`), and model inference objects (`WhisperModel`, `Kokoro`, Silero VAD session) using synthetic `float32` NumPy audio fixtures (sine waves / silence / impulse arrays). Assert all `voice.stt.*` and `voice.tts.*` emissions and payloads via the `mock_ucl` fixture (`tests/unit/conftest.py`, `tests/README.md`).
- **Hardware-bound & model integration tests (`tests/integration/`, `timeout 180 pytest`, `s08.html:45, 60-62`):** `s08.html:62` explicitly names `tests/integration/test_voice_stt.py` with the comment `# Marked as hardware-bound, skipped in headless CI`. Integration tests that require a live microphone, speaker, or local model files in `MODELS_DIR` must skip cleanly via `@pytest.mark.skipif(...)` when audio devices or model weights are absent so headless sweeps pass, while running end-to-end when invoked on a provisioned dev machine.
- **Developer-run Definition of Done boxes:** DoD box 1 (speaking into the real mic) and DoD box 2 (audible playback without underruns) require physical human speech and listening on the dev machine. `B02-07` records them as `pending developer run` until the developer confirms them.

---

## Tasks

---

### [B02-01] Hardware capability profiler, tier assignment & Phase 1 startup wiring
**Type:** [IMPLEMENT]
**Law:** `../sections/s05.html` (`Hardware Tier Definitions:`, `Detection Mechanisms:`, `Detection Timing & Scope:`, `Hardware Support & Detection Scope Statement:`, `STARTUP HARDWARE PROFILER FLOW:`), `../sections/s06.html` (`Ten-Phase Startup Sequence (Launch to Audio Ready):` → `Phase 1 (Hardware Profile):`), `../sections/s04.html` (`Platform Detection:`), `../sections/s08.html` (`Test Layout Directory Mirroring:`)
**Depends on:** BD-005

**What to build:**
- Implement the §05 hardware capability profiler and `CapabilityProfile` in `lilith/platform/` (`lilith.platform.session_state` per `s05.html:46` and `BD-005`):
  - **Immutable `CapabilityProfile` (`@dataclass(frozen=True)`, `s05.html:46`):** stores the assigned hardware tier (`0`, `1`, or `2`) and the derived STT/TTS execution configuration per `BD-005`, held in-memory in `lilith.platform.session_state` and **never saved to any database** (`s05.html:46`).
  - **Tier definitions and routing gates (`s05.html:32-37, 56-76`):**
    - **Tier 0 (`Low VRAM/CPU-only`, `< 8 GB VRAM`, `s05.html:34, 75`):** Whisper `base` STT (`int8` CPU) and Kokoro TTS on CPU; all LLM inference routes to cloud (Anthropic).
    - **Tier 1 (`Mid VRAM`, `8 GB to 20 GB VRAM`, diagram `VRAM >= 8 GB?` at `s05.html:35, 72`):** Whisper `small` STT (`float16` GPU on NVIDIA CUDA, or the `BD-005` Apple Silicon CPU path per `s10.html:36` and `HANDOFF.md:48`) and Kokoro TTS on CPU; conversational LLM local (`8B` model), artifact LLM cloud.
    - **Tier 2 (`High VRAM`, `>= 20 GB VRAM`, `s05.html:36, 69`):** Whisper `small` STT and Kokoro TTS on CPU; all LLM inference runs locally.
  - **Detection mechanisms (`s05.html:39-44`):**
    - **Windows/Linux (`IS_WINDOWS or IS_LINUX`, `s05.html:41`):** run `subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], ...)` with a strict `1000ms` (`timeout=1.0`) execution timeout, parsing VRAM directly in MB (`s05.html:41`). On `FileNotFoundError`, ` subprocess.TimeoutExpired`, non-zero exit code, or unparseable output (including AMD, Intel Arc, or CPU-only hosts per `s05.html:50`), treat detected VRAM as `0` MB and implicitly fall back to **Tier 0 (`CPU-only/Cloud`)** without raising an unrecoverable halt.
    - **macOS (`IS_MAC`, `s05.html:42, 49`):** on Apple Silicon (guarded per `BD-005`), query unified memory size via `sysctl hw.memsize` (`s05.html:42`, with the same `1000ms` subprocess timeout discipline), where unified memory behaves as both system memory and VRAM. On Intel Macs or failed `sysctl`, treat VRAM as `0` and fall back to **Tier 0** (`s05.html:49-50`).
    - **System RAM (`s05.html:43`):** read `psutil.virtual_memory().total` to verify minimum memory availability (`16GB` required for local LLM execution in Tier 1+, applied per `BD-005`). (`psutil` is already in `pyproject.toml:20`; no new dependency is added in this task.)
  - **Platform flags (`s04.html:59`):** branch only on `IS_LINUX`, `IS_MAC`, `IS_WINDOWS` imported from `lilith.platform` (or injected into the pure detection helper for cross-platform unit tests, matching `paths.build_paths()` in `lilith/platform/paths.py:60-64`). Never check `sys.platform` or environment variables ad hoc.
- **Wire Startup Phase 1 in `lilith/app.py` (`s06.html:35`, `lilith/app.py:189`):**
  - Replace the Phase 1 stub comment at `lilith/app.py:189` (`_phase(1, PHASE_NAMES[0])  # hardware profile stub (CH-02)`) so `startup()` runs the hardware profiler once before Phase 2, stores the immutable `CapabilityProfile` on `lilith.platform.session_state` (and on `Lifecycle` if exposed there), and emits `_phase(1, PHASE_NAMES[0])` (`lifecycle.phase` `{"phase": 1, "name": "hardware profile"}`, plus any telemetry field settled in `BD-005`).
  - Note per `docs/audits/CH-01.md:106`: do **not** modify `_run_idle_loop()` (`signal.pause()` at `lilith/app.py:231`).

**Docs:** `docs/CHANGELOG.md` entry under `### CH-02 — Voice I/O Pipeline`. Update `docs/architecture/data-flows/startup-sequence.md` (Phase 1 is now real, no longer a stub) and `docs/architecture/01-containers.md` (`platform/` box and status line naming the hardware profiler / `session_state`).

**Acceptance criteria:** Unit tests in `tests/unit/test_hardware.py` (using injected/monkeypatched `subprocess.run` and `psutil.virtual_memory` so every branch runs on Linux, macOS, and Windows without requiring an NVIDIA GPU or Apple Silicon): (a) Linux/Windows `nvidia-smi` returning `< 8 GB`, `12288` MB (`12 GB`), and `24576` MB (`24 GB`) with `>= 16GB` system RAM assigns Tiers `0`, `1`, and `2` respectively with the exact Whisper model/compute settings (`base`/`int8` CPU vs `small`/`float16` GPU); (b) `nvidia-smi` timeout (`subprocess.TimeoutExpired` after `1000ms`), missing binary (`FileNotFoundError`), non-zero exit code, and malformed stdout each fall back cleanly to Tier `0`; (c) macOS Apple Silicon `sysctl hw.memsize` at `8 GB`, `16 GB`, and `32 GB` assigns the expected tiers per `BD-005` while macOS Intel or failed `sysctl` falls back to Tier `0`; (d) `< 16GB` system RAM enforces the `s05.html:43` minimum memory rule per `BD-005`; (e) `CapabilityProfile` is frozen (`dataclasses.FrozenInstanceError` on mutation) and stored in `lilith.platform.session_state`; (f) `app.startup()` in `tests/unit/test_lifecycle.py` populates `session_state` during Phase 1 and never writes the profile to `conversation_db`; `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, and `pre-commit run --all-files` (ruff, basedpyright, lint-imports, gitleaks) pass; Docs contributions landed.

---

### [B02-02] Audio capture stream (`16 kHz` mono `float32`), WASAPI shared mode, resampling & hot-plug recovery
**Type:** [IMPLEMENT]
**Law:** `../sections/s09.html` (`Audio Library Choice:`, `Microphone Stream (Capture):`, `Windows WASAPI Integration:`, `Resampling Fallback:`, `Stream Restart & Hot-Plug Recovery:`, `Device Diagnostics:`, `AUDIO PIPELINE CONCURRENCY MODEL:`), `../sections/s11.html` (`Package pin:` for `sounddevice==0.5.5`), `../sections/s04.html` (`Resolutions for the Three Hard Windows Problems:` → `Audio Driver Variance:`), `../sections/s01.html` (`Package Management:`, `Module Boundaries:`), `../sections/s08.html` (`Testing Standards`)
**Depends on:** BD-006

**What to build:**
- **Add dependencies (`s09.html:32, 36`, `s11.html:32`, ADR `B-002`):**
  - Add `"sounddevice==0.5.5"` (exact pin from `s11.html:32`; `sounddevice` + PortAudio in `s09.html:32`, MIT license) and `"numpy"` (`numpy.interp` in `s09.html:36`, `NumPy array` in `s10.html:51`, BSD-3-Clause license) under `[project] dependencies` in `pyproject.toml`.
  - Follow `docs/runbook/add-or-update-a-dependency.md`: compile `requirements.txt` via `uv pip compile pyproject.toml --extra dev --universal --generate-hashes --python-version 3.12 -o requirements.txt`, verify multi-platform hashes for `sounddevice` and `numpy`, and record the RES-15 license check for `sounddevice`, `numpy`, and any transitive packages (`cffi`, `pycparser`).
- **Implement the capture half of `lilith/platform/audio.py` (replacing the CH-01 placeholder docstring):**
  - **Microphone capture stream (`s09.html:33`):** configure `sounddevice.InputStream` locked to `samplerate=16000` (`16 kHz`), `channels=1` (`mono`), `dtype="float32"`, and `blocksize=480` frames (`30ms`).
  - **Real-time callback discipline (`s09.html:33, 43-46`):** the `InputStream` callback **only** copies the incoming `indata` chunk (`indata.copy()`) and pushes it to a thread-safe `audio_q` (`queue.Queue` sized per `BD-006`), plus updates the latest input RMS amplitude scalar (`s09.html:38`). **No model inference, blocking locks, I/O, or heap allocations beyond copying the chunk may run on the PortAudio callback thread** (`s09.html:33`).
  - **Windows WASAPI Shared Mode (`s09.html:35`, `s04.html:55`):** when `IS_WINDOWS` is true, query `sounddevice.query_hostapis()` / `sounddevice.query_devices()` to resolve the `"Windows WASAPI"` Host API index and bind the input device to WASAPI in **Shared Mode** by default (`sounddevice.WasapiSettings(exclusive=False)` or default shared WASAPI device selection) to prevent exclusive-access locks that conflict with browsers or Discord (`s09.html:35`) and bypass legacy MME drivers (`s04.html:55`).
  - **Resampling fallback (`s09.html:36`):** if the microphone device rejects native `16 kHz` (`16000` Hz) capture (`sounddevice.PortAudioError` / invalid sample rate), open the hardware stream at the device's default native rate (`44.1 kHz` / `44100` Hz or `48 kHz` / `48000` Hz, with `blocksize` per `BD-006`) and provide the pure helper `resample_to_16khz(chunk: np.ndarray, src_rate: int) -> np.ndarray` using `numpy.interp` (`s09.html:36`) so the VAD worker thread (`B02-04`) resamples captured chunks down to `16 kHz` (`480` frames per `30ms`) before VAD inference, never inside the PortAudio callback thread.
  - **Stream restart & hot-plug recovery (`s09.html:37`):** handle stream exceptions or PortAudio `CallbackFlags` status flags (`input_underflow` / `input_overflow`) by closing the active stream, executing device re-enumeration, selecting the system's new default input device, and restarting the stream per `BD-006` (performed off the real-time callback thread so PortAudio is never closed from inside its own callback).
  - **Input RMS amplitude (`s09.html:38`):** compute and expose the latest real-time RMS amplitude (`float(np.sqrt(np.mean(np.square(chunk))))`) for downstream consumers (the CH-05 Orb widget and diagnostics). Do **not** build any GUI widget here (`BUILD_GUIDE.md:123`: GUI is CH-05 scope).
  - **Layer boundary (`pyproject.toml:66-76`):** `lilith/platform/audio.py` must not import `lilith.data` or `lilith.logic`. Any concrete `LilithError` added to `lilith/errors.py` follows ADR `B-003` and `BD-006` (`from None`, no free-text message field).

**Docs:** `docs/CHANGELOG.md` entry under `### CH-02 — Voice I/O Pipeline`. Create `docs/architecture/components/voice-pipeline.md` (the L3 component wiki page for the voice subsystem per `docs/architecture/README.md:9` and `standards.html:221-237`), documenting the capture stream, WASAPI shared-mode binding, `44.1`/`48 kHz` → `16 kHz` `numpy.interp` resampling path, hot-plug recovery loop, and a Mermaid flowchart of the capture → `audio_q` concurrency boundary.

**Acceptance criteria:** `requirements.txt` carries `uv`'s autogenerated header and multi-platform hashes for `sounddevice==0.5.5` and `numpy`; unit tests in `tests/unit/test_audio.py` (with mocked `sounddevice`) verify: (a) `InputStream` opens with `samplerate=16000, channels=1, dtype="float32", blocksize=480`; (b) the capture callback copies the `480`-frame `float32` buffer into `audio_q` (mutating the caller's source buffer after the callback returns does not mutate the queued array) and updates input RMS amplitude; (c) on simulated Windows (`IS_WINDOWS`), WASAPI Host API device selection and shared mode (`exclusive=False`) are used; (d) when `16000` Hz raises `PortAudioError`, the stream falls back to native `48000` Hz or `44100` Hz and `resample_to_16khz()` via `numpy.interp` produces a `480`-frame `float32` `16 kHz` array from a `30ms` native chunk; (e) simulated status flags (`input_overflow` / `input_underflow`) or stream errors trigger close → device re-enumeration → default-device selection → stream restart; `lint-imports` confirms `lilith.platform.audio` imports nothing above `lilith.platform`; `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, and `pre-commit run --all-files` pass; Docs contributions landed.

---

### [B02-03] TTS playback stream (`24 kHz` mono `float32`), bounded `playback_q` & underrun silence padding
**Type:** [IMPLEMENT]
**Law:** `../sections/s09.html` (`TTS Playback Stream (Output):`, `Windows WASAPI Integration:`, `Stream Restart & Hot-Plug Recovery:`, `Device Diagnostics:`), `../sections/s11.html` (`Playback:`), `../sections/s08.html` (`Testing Standards`)
**Depends on:** B02-02, BD-006

**What to build:**
- **Extend `lilith/platform/audio.py` with the TTS output stream and bounded `playback_q` (`s09.html:34`, `s11.html:37`):**
  - **Output stream parameters (`s09.html:34`, `s11.html:37`):** open `sounddevice.OutputStream(channels=1, samplerate=24000, blocksize=1024, dtype="float32", ...)` running concurrently with and independently of the `16 kHz` capture stream (`s09.html:34`).
  - **Bounded `playback_q` and partial-segment framing (`s09.html:34`, `s11.html:37`):** maintain a bounded `playback_q` (`queue.Queue(maxsize=...)` per `BD-006`) holding synthesized mono `float32` PCM arrays from Kokoro. Because synthesized sentence/clause chunks have arbitrary frame lengths (not multiples of `1024`), the output callback drains `playback_q` across callback invocations using an internal remainder slice/buffer so exactly `1024` frames (`frames == 1024`) are written to `outdata[:, 0]` on each callback without dropping samples between chunks.
  - **Underrun silence padding (`s11.html:37`):** when `playback_q` is empty (or a trailing segment has fewer than `1024` frames and no next chunk is queued), pad the remaining frames of `outdata` with `0.0` (`float32` silence) — never blocking the PortAudio callback thread (`s11.html:37`).
  - **Output RMS amplitude for the Orb bridge (`s09.html:38`, `s11.html:37, 43`):** compute the RMS amplitude of each `1024`-frame output block (`0.0` during silence padding) and expose it via a thread-safe getter/callback for the CH-05 Orb widget (`§27`).
  - **WASAPI Shared Mode & hot-plug recovery (`s09.html:35, 37`):** bind the output stream to WASAPI Shared Mode on Windows (`IS_WINDOWS`) and apply the same close → re-enumerate → select new default output device → restart recovery loop on `output_underflow` / `output_overflow` or stream exceptions as `B02-02`.

**Docs:** `docs/CHANGELOG.md` entry under `### CH-02 — Voice I/O Pipeline`. Update `docs/architecture/components/voice-pipeline.md` to add the `playback_q` → `sounddevice.OutputStream` (`24 kHz`, `1024` frames, silence underrun padding, output RMS) section and Mermaid flow.

**Acceptance criteria:** Unit tests in `tests/unit/test_audio.py` (with mocked `sounddevice.OutputStream`) verify: (a) `OutputStream` opens with `channels=1, samplerate=24000, blocksize=1024, dtype="float32"` independently of `InputStream`; (b) `playback_q` is bounded (`maxsize > 0` per `BD-006`); (c) enqueuing multi-block and non-multiple-of-`1024` PCM arrays (e.g. `2500` frames) drains across consecutive `1024`-frame callbacks (`1024`, `1024`, then `452` frames + `572` zeros of silence padding) with sample-exact continuity; (d) an empty `playback_q` fills all `1024` frames with `0.0` silence and reports `0.0` RMS amplitude without blocking or raising; (e) non-silent output updates the output RMS amplitude accurately; (f) simulated output stream errors / status flags trigger the hot-plug recovery loop; `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, and `pre-commit run --all-files` pass; Docs contributions landed.

---

### [B02-04] Silero VAD worker thread, utterance buffering & `voice.stt.start` telemetry
**Type:** [IMPLEMENT]
**Law:** `../sections/s10.html` (`Silero VAD Parameters:`, `Speech Pipeline Architecture:` items 1–3, `UCL Telemetry Events:` → `voice.stt.start`, `STT PIPELINE DATAFLOW:`), `../sections/s09.html` (`Resampling Fallback:`, `AUDIO PIPELINE CONCURRENCY MODEL:`), `../sections/s08.html` (`UCL Telemetry Assertions:`, `Payload Schema Review:`), `../sections/s16.html` (`Write rule:`, `Payload Content Boundary:`)
**Depends on:** B02-02, BD-006, BD-007, BD-008

**What to build:**
- **Replace the CH-01 placeholder in `lilith/logic/stt.py` (`docs/audits/CH-01.md:114`) with the Silero VAD worker stage (`s10.html:39-51, 58, 65-75`):**
  - If `BD-007` selects `onnxruntime==1.23.2` (pinned in `s11.html:32`) or a Silero VAD package not yet in `pyproject.toml`, add it to `pyproject.toml` and recompile `requirements.txt` via `uv pip compile pyproject.toml --extra dev --universal --generate-hashes --python-version 3.12 -o requirements.txt` per ADR `B-002` and `docs/runbook/add-or-update-a-dependency.md` (with RES-15 license verification).
  - **Silero VAD parameters (`s10.html:39-45`, quoted verbatim as module constants):**
    - Input chunk size: `480` frames (`30ms` at `16 kHz` sample rate mono `float32`, `s10.html:41`).
    - Speech threshold: `0.5` probability cutoff (`s10.html:42`).
    - End-of-speech window: `600ms` of contiguous silence (`min_silence_duration_ms=600`, `s10.html:43`).
    - Padding: `250ms` pre/post padding (`speech_pad_ms=250`) so word boundaries are not truncated (`s10.html:44`).
  - **VAD worker thread & state machine (`s10.html:49-51`, `s09.html:36, 46-52`):**
    1. Pull raw chunks from `audio_q`. If the capture stream opened at a fallback native rate (`44.1 kHz` or `48 kHz`), resample the chunk down to `16 kHz` (`480` frames per `30ms`) in this VAD thread using `numpy.interp` (`resample_to_16khz` from `B02-02`, `s09.html:36`).
    2. Maintain a pre-speech ring buffer covering `speech_pad_ms=250` (`250ms` at `16 kHz` = `4000` samples / chunks per `BD-007`) while idle.
    3. Compute the Silero VAD speech probability for each frame window per `BD-007`.
    4. **Speech onset (`prob >= 0.5`, `s10.html:42, 58`):** transition to speaking state, prepend the `250ms` pre-padding frames into the active utterance buffer, and emit `log_event("voice.stt.start", ...)` via `lilith.data.ucl.log_event` (payload per `BD-007`).
    5. **Contiguous silence tracking & end-of-utterance (`s10.html:43-44, 51`):** while in speaking state, buffer incoming frames; reset the silence counter whenever `prob >= 0.5`; increment contiguous silence when `prob < 0.5`. Once contiguous silence reaches `min_silence_duration_ms=600` (`600ms`), retain `speech_pad_ms=250` (`250ms`) post-padding (without keeping trailing silence beyond `250ms`), concatenate the buffered frames into a single contiguous 1-D `float32` NumPy array (`np.concatenate`), push it to `transcription_q` (`s10.html:51, 75`, exposing `utterance_q` as an alias if settled in `BD-006` for `s09.html:52`), and reset the VAD state for the next utterance.

**Docs:** `docs/CHANGELOG.md` entry under `### CH-02 — Voice I/O Pipeline`. Update `docs/architecture/components/voice-pipeline.md` with the Silero VAD state machine (`480` frames / `30ms`, threshold `0.5`, `speech_pad_ms=250`, `min_silence_duration_ms=600`, `voice.stt.start`, and `audio_q` → `transcription_q` Mermaid diagram).

**Acceptance criteria:** Unit tests in `tests/unit/test_stt.py` (using a deterministic fake/stubbed VAD probability callable and synthetic `480`-frame `float32` chunks, plus `mock_ucl`) verify: (a) chunks with probability `< 0.5` stay idle, emit no `voice.stt.start`, and enqueue nothing to `transcription_q`; (b) a chunk crossing `>= 0.5` emits `voice.stt.start` exactly once for the utterance and includes `250ms` of pre-speech padded frames; (c) brief silence `< 600ms` followed by more speech (`>= 0.5`) stays in a single utterance without premature cut or duplicate `voice.stt.start`; (d) `600ms` of contiguous silence (`prob < 0.5`) triggers end-of-utterance, retains `250ms` post-padding, concatenates a single 1-D `float32` `np.ndarray` onto `transcription_q`, and resets cleanly for a second utterance; (e) fallback `48 kHz` chunks are resampled to `16 kHz` via `numpy.interp` on the VAD worker thread before VAD evaluation; `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, and `pre-commit run --all-files` pass; Docs contributions landed.

---

### [B02-05] `faster-whisper` STT worker thread, tier-gated model loading & `voice.stt.complete` telemetry
**Type:** [IMPLEMENT]
**Law:** `../sections/s10.html` (`Python Package & Backend:`, `Model Selection by Tier:`, `Speech Pipeline Architecture:` item 4, `Output Structure:`, `UCL Telemetry Events:` → `voice.stt.complete`, `STT PIPELINE DATAFLOW:`), `../sections/s05.html` (`Hardware Tier Definitions:`, `Detection Timing & Scope:`), `../sections/s08.html` (`UCL Telemetry Assertions:`, `Payload Schema Review:`, `TESTING ARCHITECTURE:` → `test_voice_stt.py`), `../sections/s16.html` (`Write rule:`, `Payload Content Boundary:`)
**Depends on:** B02-01, B02-04, BD-005, BD-007, BD-008

**What to build:**
- **Add `faster-whisper` dependency (`s10.html:32`, ADR `B-002`):**
  - Add `"faster-whisper==1.2.1"` (`s10.html:32`: `faster-whisper (v1.2.1)` utilizing the `CTranslate2` backend, MIT license) to `[project] dependencies` in `pyproject.toml`.
  - Follow `docs/runbook/add-or-update-a-dependency.md`: compile `requirements.txt` with `uv pip compile pyproject.toml --extra dev --universal --generate-hashes --python-version 3.12 -o requirements.txt`, verify multi-platform wheel hashes for `ctranslate2` and `faster-whisper`, and record the RES-15 license audit for `faster-whisper` and its transitive tree.
- **Implement tier-gated `faster-whisper` model selection and batch transcription worker in `lilith/logic/stt.py` (`s10.html:32-38, 52-61`):**
  - **Model selection by hardware tier (`s10.html:33-38`, `s05.html:34-36`):** read `CapabilityProfile` from `lilith.platform.session_state`:
    - **Tier 0 (`s10.html:35`, `s05.html:34`):** `base` model, `int8` quantized, executed on `cpu` (`<1.0s` transcription latency target).
    - **Tier 1 & Tier 2 (`s10.html:36`, `s05.html:35-36`):** `small` model, `float16` quantized on CUDA GPUs (`device="cuda", compute_type="float16"`) or the `BD-005` CPU fallback path on macOS Apple Silicon (`HANDOFF.md:48`: `faster-whisper` via `ctranslate2` is CPU-only on macOS) and when CUDA initialization fails (`<0.5s` transcription latency target).
    - Store/load model weights under `paths.MODELS_DIR` per `BD-008` (`s04.html:40, 73`).
  - **Whisper worker thread (`s10.html:52, 55, 75-81`):**
    1. Pop concatenated utterance `float32` NumPy arrays from `transcription_q`.
    2. Transcribe the array in a batch via `WhisperModel.transcribe(...)` (parameters per `BD-007`) and join the segment texts into a **single plain text string** (`s10.html:55`: downstream components receive the raw string directly without metadata or timestamp arrays).
    3. Deliver the plain text string to a registered callback or transcript output queue (the CH-02 seam that CH-03's two-mode router will subscribe to; do **not** implement router logic here, `BUILD_GUIDE.md:123`).
  - **UCL telemetry (`s10.html:59`, `s08.html:41`, `s16.html:38`):**
    - On successful transcription, emit `log_event("voice.stt.complete", {"duration_ms": ..., "audio_len_ms": ..., "word_count": ...})` via `lilith.data.ucl.log_event`.
    - **Payload hygiene (`s04.html:50`, `s08.html:41`, `s16.html:38`):** never include the transcribed user text in `voice.stt.complete` or in any plaintext log.
    - Wrap driver/runtime exceptions in the `BD-006` `RecoverableError` subclass (`raise ... from None` per ADR `B-003`) and log via `err.to_payload()`.
- **Add `tests/integration/test_voice_stt.py` (`s08.html:62`):**
  - Implement the §08-named integration test file `tests/integration/test_voice_stt.py` exercising the full `audio_q` → Silero VAD worker → `transcription_q` → `faster-whisper` worker pipeline on a spoken-audio fixture (`16 kHz` mono `float32`), marked as hardware/model-bound and skipped cleanly in headless environments when model weights or audio hardware are unavailable (`s08.html:62`).

**Docs:** `docs/CHANGELOG.md` entry under `### CH-02 — Voice I/O Pipeline`. Update `docs/architecture/components/voice-pipeline.md` (adding the `faster-whisper` worker, tier-to-model mapping table, and `voice.stt.complete` schema) and `docs/architecture/data-flows/conversational-path.md` (updating the Mic → VAD → STT notes to name the concrete classes/functions in `lilith/platform/audio.py` and `lilith/logic/stt.py`).

**Acceptance criteria:** `requirements.txt` compiles cleanly with multi-platform hashes for `faster-whisper==1.2.1` and `ctranslate2`; unit tests in `tests/unit/test_stt.py` (with a fake/stubbed `WhisperModel` and `mock_ucl`) verify: (a) Tier `0` initializes `WhisperModel("base", device="cpu", compute_type="int8", ...)` while Tier `1` and Tier `2` select `"small"` with `"cuda"` / `"float16"` and exercise the CPU fallback path when CUDA is unavailable or on macOS (satisfying CH-02 DoD box 3's test requirement); (b) an utterance array popped from `transcription_q` is transcribed into a single plain `str` (no timestamps or metadata tuples) and passed to the transcript consumer; (c) `voice.stt.complete` is emitted with integer/numeric `duration_ms`, `audio_len_ms` (matching `len(audio) / 16.0`), and `word_count`, and the payload contains **zero** words of the transcript text; `tests/integration/test_voice_stt.py` exists and either passes against local model weights or skips cleanly with a clear reason when weights/hardware are absent; `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, and `pre-commit run --all-files` pass; Docs contributions landed.

---

### [B02-06] `kokoro-onnx` CPU streaming TTS, sentence/clause chunker, Phase 9 / shutdown wiring & `voice.tts.*` telemetry
**Type:** [IMPLEMENT]
**Law:** `../sections/s11.html` (`Package pin:`, `Voice:`, `Backend:`, `Latency target:`, `Cloud-path input gate (Fool's NC-4):`, `Playback:`, `Telemetry:`), `../sections/s06.html` (`Ten-Phase Startup Sequence (Launch to Audio Ready):` → `Phase 9 (Voice Pipeline Init):`, `Graceful Shutdown Sequence:` step 1), `../sections/s09.html` (`TTS Playback Stream (Output):`), `../sections/s08.html` (`UCL Telemetry Assertions:`, `Payload Schema Review:`), `../sections/s16.html` (`Write rule:`, `Payload Content Boundary:`)
**Depends on:** B02-03, B02-05, BD-006, BD-008

**What to build:**
- **Add `kokoro-onnx` and `onnxruntime` dependencies & Apache 2.0 license notice (`s11.html:32`, ADR `B-002`, `standards.html:250-254`):**
  - Add `"kokoro-onnx==0.5.0"` and `"onnxruntime==1.23.2"` (exact pins from `s11.html:32`, if `onnxruntime==1.23.2` was not already added in `B02-04`) to `[project] dependencies` in `pyproject.toml`.
  - Recompile `requirements.txt` via `uv pip compile pyproject.toml --extra dev --universal --generate-hashes --python-version 3.12 -o requirements.txt` per `docs/runbook/add-or-update-a-dependency.md`, verify multi-platform hashes, and record the RES-15 license check (noting `onnxruntime` publishes `macOS 14+` wheels only per ADR `B-002`).
  - Add the Apache 2.0 license text for Kokoro model and code under `licenses/` at the repo root (`s11.html:32`: *"Kokoro model and code are Apache 2.0 and must be listed in `licenses/`"*).
- **Implement `lilith/logic/tts.py` and update `lilith/logic/__init__.py` (replacing the CH-01 `"Filled by CH-03"` placeholder docstrings noted in `docs/audits/CH-01.md:114`):**
  - **CPU-only backend (`s11.html:34`):** initialize `kokoro-onnx` (`Kokoro`) forced onto the CPU-only ONNX Runtime provider (`"CPUExecutionProvider"`) across **all** hardware tiers (`Tier 0`, `Tier 1`, and `Tier 2`) so TTS never consumes GPU VRAM reserved for local LLM inference (`s11.html:34`). Load model and voice files from `paths.MODELS_DIR` per `BD-008`.
  - **Voice and output format (`s11.html:33, 37`):** lock voice to `"af_bella"`, target speaking rate `135` WPM (mapped to `kokoro-onnx` `speed` and `lang` per `BD-008`), producing mono `float32` PCM output at `24000` Hz (`24 kHz`).
  - **Sentence/clause chunker & streaming synthesis (`s11.html:35, 36, 41-44`):**
    - Split incoming text (or an iterator/stream of post-reverse-substitution text chunks; document the `s11.html:36` Fool's NC-4 boundary so CH-03's §14 reverse-substitution filter plugs directly into this entry point) into sentence/clause chunks per `BD-008`.
    - Synthesize clause by clause and push each resulting `24 kHz` mono `float32` PCM `np.ndarray` directly into `playback_q` (`B02-03`) as soon as Kokoro yields it so `voice.tts.first_chunk` fires within `500` ms of `voice.tts.start` (`s11.html:35`).
  - **UCL telemetry (`s11.html:38`, `s08.html:41`, `s16.html:38`):**
    - Emit `voice.tts.start` with payload `{"voice": "af_bella", "chars": ...}` when synthesis of an utterance begins (`s11.html:38`).
    - Emit `voice.tts.first_chunk` with payload `{"latency_ms": ..., "frames": ...}` when the first playable PCM chunk is enqueued to `playback_q` (`s11.html:35, 38`).
    - Emit `voice.tts.complete` with payload `{"duration_ms": ..., "chunks": ..., "success": ...}` when synthesis finishes (`s11.html:38`).
    - **Payload hygiene (`s04.html:50`, `s08.html:41`, `s16.html:38`):** never include raw or synthesized text in any `voice.tts.*` payload or plaintext log.
- **Wire Startup Phase 9 and Graceful Shutdown Step 1 in `lilith/app.py` (`s06.html:43, 49`):**
  - **Phase 9 (`lilith/app.py:224`, `s06.html:43`):** wire voice pipeline initialization into `startup()` at Phase 9 (loading Whisper and Kokoro models and opening the `sounddevice` input/output streams per `BD-006`/`BD-008` so existing unit/integration tests that run without models/devices can stub or skip cleanly as designed).
  - **Shutdown step 1 (`lilith/app.py:72-73`, `s06.html:49`):** in `Lifecycle.shutdown()`, stop the microphone capture stream immediately (`close Sounddevice inputs`, `s06.html:49`) and cleanly stop the output stream and VAD/STT/TTS worker threads before logging `_phase(1, "shutdown: audio streams stopped")` and proceeding to steps 2–5.
  - **Coverage floor (`s01.html:41`, `pyproject.toml:85-92`):** keep line + branch coverage `>= 80%` across `lilith/`. If any low-level PortAudio hardware callback lines cannot be reached under mocked `sounddevice`, document and scope any exclusion narrowly per `s01.html:41` (`80%+ test coverage (excluding hardware/audio I/O)`).

**Docs:** `docs/CHANGELOG.md` entry under `### CH-02 — Voice I/O Pipeline`. Update `docs/architecture/components/voice-pipeline.md` (adding the `kokoro-onnx` CPU streaming pipeline, clause chunker, `voice.tts.*` events, and Phase 9 / shutdown lifecycle wiring), `docs/architecture/data-flows/startup-sequence.md` (Phase 9 and Shutdown step 1 are now real), `docs/architecture/data-flows/conversational-path.md` (TTS → Speaker segment naming `lilith/logic/tts.py` and `lilith/platform/audio.py`), and `docs/SETUP.md` (documenting `MODELS_DIR` voice model setup and audio prerequisites per `BD-008`).

**Acceptance criteria:** `requirements.txt` compiles cleanly with multi-platform hashes for `kokoro-onnx==0.5.0` and `onnxruntime==1.23.2`; `licenses/` contains the Kokoro Apache 2.0 license notice; unit tests in `tests/unit/test_tts.py` (with a fake/stubbed `Kokoro` engine, `playback_q`, and `mock_ucl`) verify: (a) `Kokoro` is initialized with the CPU-only ONNX provider (`"CPUExecutionProvider"`) on Tier `0`, Tier `1`, and Tier `2` alike; (b) synthesis uses voice `"af_bella"`, the `BD-008` `135` WPM speed setting, and mono `float32` PCM at `24000` Hz; (c) multi-clause text is split and streamed so the first PCM chunk is enqueued to `playback_q` before later clauses finish synthesizing; (d) `voice.tts.start` (`voice`, `chars`), `voice.tts.first_chunk` (`latency_ms`, `frames`), and `voice.tts.complete` (`duration_ms`, `chunks`, `success`) are emitted in order with the exact `s11.html:38` keys and zero text content; (e) `Lifecycle.shutdown()` in `tests/unit/test_lifecycle.py` stops the voice streams at step 1 before closing SQLCipher connections at step 4; `pytest -q --cov` meets the `80%` floor; `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, and `pre-commit run --all-files` pass; Docs contributions landed.

---

### [B02-07] Chapter close — audit, hardware verification handoff, kanban, guide
**Type:** [AUDIT]
**Law:** CH-02 Definition of Done (`BUILD_GUIDE.md` §5, lines `127-132`), M1 section requirements & exclusions (`BUILD_SEQUENCING.md` §2.1 & §5), `../sections/s05.html`, `../sections/s08.html`, `../sections/s09.html`, `../sections/s10.html`, `../sections/s11.html`, `../standards.html` (`Documentation Standards`)
**Depends on:** B02-06

**What to build:**
1. **Walk every CH-02 Definition of Done checkbox (`BUILD_GUIDE.md:127-132`)** with concrete command outputs and test evidence, recorded in `docs/audits/CH-02.md` in the build repo:
   - **Box 1 (`Speaking into the mic produces a correct transcript through the VAD→STT path (verified on real hardware, not only fixtures)`):** provide a repeatable developer verification command / script and mark this box **`pending developer run`** in `docs/audits/CH-02.md` until the developer speaks into the real microphone on the dev machine and pastes the transcript/telemetry output (following the `B01-09` precedent in `docs/audits/CH-01.md:39-47`, lesson L-005).
   - **Box 2 (`An arbitrary text string is synthesized and audibly played through the chunk-queue path without underruns`):** provide a repeatable developer verification command / script and mark this box **`pending developer run`** until the developer confirms audible playback with zero underruns on the dev machine.
   - **Box 3 (`Hardware detection returns the correct tier/mode on the dev machine and the CPU fallback path is exercised in tests`):** record the live `CapabilityProfile` output on the audit machine plus the passing unit tests in `tests/unit/test_hardware.py` and `tests/unit/test_stt.py` exercising the CPU fallback path.
   - **Box 4 (`Unit tests cover the audio stream, Whisper inference, and Kokoro inference per §08 conventions`):** record the passing `timeout 60 pytest tests/unit/`, `timeout 180 pytest`, coverage (`pytest -q --cov`), and `pre-commit run --all-files` outputs covering `test_hardware.py`, `test_audio.py`, `test_stt.py`, and `test_tts.py`.
2. **Scope audit (`BUILD_SEQUENCING.md` §2.1 & §5, `BUILD_GUIDE.md` §2 ground rule 3 & §6 EXP-3):** verify by repo-wide inventory and record the exact commands and outputs in `docs/audits/CH-02.md`:
   - Still **exactly one** database (`conversation_db`) opened by code; `lilith/data/ucl.py` remains the M1 `dev.log` shim only.
   - No CH-03+ or excluded-section modules exist: `lilith/logic/router.py`, `lilith/logic/cwm.py`, and `lilith/ui/*` (`bus.py`, `screens/__init__.py`, `widgets/__init__.py`) remain docstring-only placeholders; no LLM (`§12`), router (`§13`), CWM/PII (`§14`), tool (`§15`), memory schema (`§18`), sync (`§19`), contacts (`§20`), calendar (`§21`), onboarding (`§25`), or vault/skills (`§29`) code exists.
   - No parked secondary-endpoint (`kitchen_speaker`, WebSocket streaming, voice auth — `BUILD_GUIDE.md:123`, `BUILD_SEQUENCING.md:243`) code exists.
   - No vector or embedding package (`faiss`, `chroma`, `sentence-transformers`, `sqlite-vec`, `lancedb`, `qdrant`, `milvus`, `weaviate`, `annoy`, `hnswlib`) appears in `pyproject.toml` or `requirements.txt` (`BUILD_GUIDE.md:346`).
   - Compare `git ls-files lilith/` against the `§01` package tree (`s01.html:45-66`) and account for every sanctioned file (`errors.py`, `telemetry.py`, `bootstrap.py`, `migrations/`, plus `session_state.py` if created per `BD-005`).
3. **Docs sweep (`standards.html:218-244`, `BUILD_GUIDE.md:374`):** verify every `B02-01`…`B02-06` **Docs:** contribution landed; update the status lines on `docs/architecture/00-system-context.md`, `docs/architecture/01-containers.md`, `docs/architecture/components/voice-pipeline.md`, and `docs/architecture/data-flows/` (`README.md`, `startup-sequence.md`, `conversational-path.md`, `artifact-path.md`) to match built CH-02 reality; link `audits/CH-02.md` in `docs/README.md`; and confirm `docs/CHANGELOG.md` has a complete `### CH-02 — Voice I/O Pipeline` section including `B02-07`.
4. **Kanban & Build Guide close (gated on developer live-audio confirmation):** once the developer runs and confirms DoD boxes 1 and 2 on real hardware (and CH-01's POSIX close completes), tick the Definition-of-Done checkboxes on [issue #2](https://github.com/Squirrelthug/squirrelthug.github.io/issues/2) (`gh issue edit 2`), confirm all CH-02 sub-issues (`BD-005`…`BD-008`, `B02-01`…`B02-07`) are closed, move the CH-02 card to **Done** on Project 46, and update `BUILD_GUIDE.md` §4 in the design-site repo (`CH-02` → **Done**).
5. Report completion to the developer with any observations or law notes to carry into `SPRINT-B03` (CH-03 Intelligence Core: `§12`, `§23`, `§14`, `§13`).

**Docs:** `docs/audits/CH-02.md`, `docs/CHANGELOG.md` entry (`B02-07`), `docs/README.md` (Chapter audits row updated to link `audits/CH-02.md`), and status-line updates across `docs/architecture/00-system-context.md`, `docs/architecture/01-containers.md`, `docs/architecture/components/voice-pipeline.md`, and `docs/architecture/data-flows/` (`README.md`, `startup-sequence.md`, `conversational-path.md`, `artifact-path.md`).

**Acceptance criteria:** `docs/audits/CH-02.md` is merged with concrete command evidence for every DoD box (marking boxes 1 and 2 `pending developer run` until live mic/speaker confirmation), the full M1 scope inventory, and the docs-sweep table; every architecture and data-flow status line matches built CH-02 reality; after the developer's live hardware confirmation, issue #2 shows all DoD boxes ticked, the card sits in Done on Project 46, and `BUILD_GUIDE.md` §4 shows `CH-02` as `Done`; Docs contributions landed.

---

## Sequential order

```
B02-01 (§05 hardware tier + Phase 1) ─────────────────────────────┐
                                                                  ▼
B02-02 (§09 capture stream) ──┬──► B02-04 (§10 Silero VAD) ──► B02-05 (§10 faster-whisper STT) ──┐
                              │                                                                  ▼
                              └──► B02-03 (§09/§11 playback) ────────────────────────────────► B02-06 (§11 Kokoro TTS + §06 Phase 9/shutdown) ──► B02-07 (CH-02 audit)
```

- All four decision briefs (`BD-005`…`BD-008`) resolve before code tasks begin.
- `B02-01` and `B02-02` touch disjoint modules (`lilith/platform/session_state.py` + `lilith/app.py` vs `pyproject.toml` + `requirements.txt` + `lilith/platform/audio.py`) and may run in parallel or in sequence (`B02-01` → `B02-02`).
- `B02-03` and `B02-04` both depend on `B02-02` and touch disjoint modules (`lilith/platform/audio.py` vs `lilith/logic/stt.py`).
- `B02-05` → `B02-06` → `B02-07` are strictly sequential (`B02-05` and `B02-06` both recompile `requirements.txt`, and `B02-06` wires the completed STT and TTS pipelines into `lilith/app.py` Phase 9 and Shutdown step 1).

---

*When B02-07 closes, CH-02 is done. Next: author `SPRINT-B03-intelligence-core.md` from `BUILD_GUIDE.md` CH-03 + §12/§23/§14/§13, per the working loop.*
