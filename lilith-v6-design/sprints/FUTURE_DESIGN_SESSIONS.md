# Lilith v6 — Future Design Sessions (Vision Parking List)

Companion to `BUILD_SEQUENCING.md` §5 (parked *scope*). This file parks *vision*: capabilities that are part of Lilith's intent but are **not in the frozen v1 law**. Nothing here may be built, stubbed, or "prepared for" during the v1 chapters — each item enters the law only through a documented design session per the amendment convention in `../README.md`. What the v1 build *does* owe each item is its seam: the already-designed extension point listed below, kept clean.

The governing idea (recorded 2026-08-03): **Lilith is the kind of harness that intends to use all other harnesses.** She is a conversational agent who keeps the context window on the user's machine, hands any model exactly the context it needs — sufficient, minimal, cached when efficient — and wields a growing catalog of tools and external systems on the user's behalf, so the user makes well-informed decisions without doing the homework (the 80% principle).

---

## FDS-1 · MCP / External Tool-Provider Bridge

**Vision:** Isolated external tools — a home-automation system on an open standard, any MCP server, community toolchains — usable by Lilith on the user's behalf, with the same voice-driven experience as native tools. The paradigm: the external system owns the tool; Lilith owns the *use* of it.
**Not in v1 because:** the v1 tool system (§15) is deliberately a closed, deterministic catalog — one YAML + one function per tool, no third-party surface (the OpenClaw supply-chain lesson).
**The seam:** the §15 tool runner. An MCP client adapter would enroll external tools into the existing catalog so they inherit narratives (§24), telemetry (§16), the artifact lane, and §29-style enrollment friction unchanged.
**Session prerequisites:** a formal research step (res-NN style) on the MCP ecosystem's current security posture — auth model, tool-description injection risks, version churn — before the session convenes. Likely trigger point: when the tool catalog grows past the app-suite tools (around Phases 5–7) or when the first real external integration is wanted.

## FDS-2 · Autonomy & Proactive Engine

**Vision:** Lilith initiates: reminds the user when a relationship thread has gone stale, keeps a busy polymath's projects and responsibilities on track, surfaces the day's shape without being asked. Reactive v1 knowledge (contact `last_interaction_at`, L2 profiles, agenda tools) becomes proactive care.
**Not in v1 because:** v1 Lilith speaks only when spoken to; an initiating engine is a large behavioral surface with its own failure modes (nagging, interrupting, misjudged urgency) that deserves its own reviewed design. v5's AL-era prototypes (delivery routing, daily roundup, work-schedule awareness) are the lessons bank.
**The seam:** the L1/L2 job machinery (§17) + UCL telemetry (§16) already compute and store everything a proactivity engine would read; the narrative layer (§24) and endpoint capability model (§22) define how it would speak.
**Session prerequisites:** several weeks of real dogfooding telemetry, so proactive triggers are designed against observed rhythms rather than guessed ones.

## FDS-3 · Multi-Provider Expansion ("pipelines per model")

**Vision:** OpenRouter-class breadth — many cloud models and local models behind one interface, each with a developed pipeline, chosen per task; the CWM builds a sufficient context window for *any* model and any session.
**Not in v1 because:** v1 law names exactly two providers — Anthropic (primary, BYOK, cached) and Ollama (local fallback, Phase 4).
**The seam:** the §12 thin-adapter pattern. Each new provider is one adapter implementing the same interface; the CWM, router, PII gate, and telemetry are already provider-agnostic.
**Session prerequisites:** per-provider research on caching semantics, tool-call formats, and privacy terms; the FDS-4 cost instrumentation ideally lands first so provider choice can be cost-aware from day one.

## FDS-4 · Cost Awareness & the Cloud Spending Ledger

**Vision:** Local-first as the default posture — long artifacts default to patient local processing (overnight is fine), cloud is something the user deliberately pushes a task toward, and cloud spending is always visible: a running dollar amount plus the proposed cost of each push, kept in a plain document of Lilith's own, in a folder on the user's desktop. Cache used while efficient, fresh context sent when the cache has aged out — never the whole conversation log.
**Not in v1 because:** no pricing/ledger surface exists in the law; v1's cost posture is structural (tiny conversational contexts, cached stable blocks, `cache_hit` telemetry) rather than user-facing.
**The seam:** `llm.call.*` telemetry (§16) already records provider, model, token counts, and cache hits per call — pricing it is arithmetic; the artifact lane (§13/§15) is where a local-vs-cloud dispatch decision would sit; §04/§29 external-storage conventions cover the desktop document.
**Session prerequisites:** FDS-3 unresolved questions aside, this session mainly needs real usage data — a month of dogfooded `ucl_db` records to define what the ledger must actually show.

## FDS-5 · Distribution, Installers & Auto-Update — added 2026-08-06

**Vision:** Lilith installs like a real desktop application on all three platforms and keeps herself current without the user hunting for downloads — a signed and notarized macOS `.dmg`, a signed Windows installer, a Linux AppImage, and an unobtrusive in-app update path (Sparkle / WinSparkle / AppImageUpdate-class) with rollback to the previous `--onedir` generation.
**Not in v1 because:** the law stops at build artifacts. §07 defines a GitHub Actions matrix producing per-platform PyInstaller `--onedir` outputs and uploading them as CI artifacts, and CH-14 speaks only of "release artifacts per §07" — no section defines installers, signing identities, notarization, update channels, update-check UX, or rollback. Shipping updates is also its own security surface (a compromised update channel is full-device compromise) and deserves a reviewed design rather than improvisation at freeze time. Signing has real-world prerequisites — an Apple Developer account, an OV code-signing certificate — that are procurement, not code.
**The seam:** §07's build matrix already produces the per-platform `--onedir` trees an installer would wrap, and its LGPL `--onedir` constraint (end users must be able to replace the Qt shared libraries) is the hard boundary any packaging or update mechanism must preserve. §04's `APP_INTERNAL_DIR` layout and §29's backup/restore unit define what an update must not disturb; §06's startup sequence is where a non-blocking update check would sit.
**Session prerequisites:** v1 feature-complete (CH-14), so the artifact being packaged is stable; and a prior decision on whether v6 v1 ships to anyone but the developer at all — if it stays developer-only, AppImage plus manual re-download may be the entire answer and this collapses into a packaging sprint rather than a design session. Historical scoping notes live in `Squirrelthug/LILITH` issues #874 (auto-update) and #875 (packaging sprints); the §28 Settings-screen intent in #876 belongs to the CH-14 sprint, not here.

## FDS-6 · Selectable Storage Tiers — the privacy/access trade-off the user controls — added 2026-08-06

**Vision:** The user decides how much of what Lilith holds is encrypted at rest, per data category, through a simple settings surface presented at onboarding — with the trade-off stated honestly at the point of choice. Some users want everything sealed; some want their notes reachable by their own tools; some want nothing encrypted at all. Today the answer is one global posture chosen by the developer. The vision is that it becomes a user's informed choice, and that Lilith is candid about what each tier costs them.
**Not in v1 because:** it contradicts a standing non-negotiable standard — *"All databases use SQLCipher… No plaintext SQLite anywhere in the application. This applies from the first migration."* That standard exists to prevent the expensive direction (retrofitting encryption onto populated plaintext databases). **The direction proposed here is the cheap one and is preserved, not foreclosed, by building v1 fully encrypted** — which is precisely why this can wait without cost. It also needs a threat-model revision (§02) and a claim-ceiling review, since a tier system means the honest privacy statement becomes conditional on user configuration.
**The seam:** §03 already mandates that *every* connection is keyed through the `SessionKeyManager` wrapper in one connection factory — a storage tier is a branch at that single chokepoint, not a change at call sites. `security_tier` already exists in the §02 keychain table as a non-secret user preference (`convenience`/`prompt`), establishing the pattern of a user-chosen security posture. An unencrypted tier requires no salt, so `salts.dat`'s 192-byte six-slot format is unaffected. §25's onboarding flow is where the choice would be presented, and §29's export/restore unit is what must keep working across mixed tiers.
**Session prerequisites — one correction to carry in, recorded 2026-08-06:** the motivating premise ("encryption limits how we search for context") is only partly true and the session must not design against the wrong constraint. **FTS5 keyword search works fully inside SQLCipher** — §18's entire v1 recall path already runs encrypted. The user's own documents are already plaintext, since §29 indexes note vaults *in place* and leaves originals externally readable. The one genuinely encryption-blocked capability is the **vector extension**, and that is already isolated behind Experiment 3 with a named fallback. So the real benefits of a plaintext tier are decryption overhead (modest, per-page) and third-party tool access to Lilith's *own* accumulated data — not keyword-search capability. Any user-facing copy must respect §02's claim ceiling and must not promise a speed difference that measurement does not support. Convene after v1 has real dogfooding data on where retrieval actually spends its time.

## FDS-7 · Data Locality Registry & Storage-Pressure Custodianship — added 2026-08-06

**Vision:** Lilith knows *where the user's things are*, not only what they say. Some data lives in her internal databases; larger or unsuitable items live elsewhere — an external drive, cold storage, the user's own cloud — and she holds a pointer, tracks whether that location is still reachable, and reports honestly when it is not. One of her periodic cycles watches local storage pressure, and because she holds the context of the user's whole life she can act on it as a personal assistant would: noticing that space is running out, proposing what to offload, and facilitating the move to cheap cloud or cold storage on the user's behalf. The custodian promise extends from *"I never copy your files"* to *"I always know where they are and whether they are still there."*
**Not in v1 because:** no section defines a locality registry, a remote-status model, or a storage-pressure monitor. §29 explicitly defers cloud-drive integration (Drive/iCloud/OneDrive) to v6.1+ and confines v1 to "local filesystem paths and pointers". Proactively initiating an offload is also initiating behaviour, which v1 does not do at all (see FDS-2) — and a custodian that *moves* user data is a materially larger trust surface than one that only reads it, so it needs its own reviewed design and its own never-delete guarantees.
**The seam:** §29's custodian model is already pointer-based rather than copy-based — indexing files where they live is exactly the primitive a locality registry generalises. §17's `refresh_capability` field, with its `manual_source` value and the §14 absence-disclosure path (`status=source_unsupported`, "unavailable this turn; do not guess"), is already the honest-about-unreachable-data machinery a remote location would reuse unchanged. §05's hardware detection is the seam for reading disk state; §16's telemetry and §17's L1/L2 job machinery are where a pressure monitor would live; §15's tool catalog is how an offload would be executed under user consent.
**Session prerequisites:** FDS-2 (autonomy) should resolve first or alongside — a storage-pressure monitor that only *notices* is a small feature, while one that *proposes and acts* inherits every question FDS-2 exists to answer about initiative, urgency, and nagging. Also needs the §29 cloud-integration deferral lifted, since facilitating an offload to a third-party service is precisely what v1 excludes. Real dogfooding data on how much Lilith actually accumulates, so the pressure thresholds are measured rather than guessed.

## FDS-8 · Multi-Device Lilith: One Hub, Many Endpoints — added 2026-09-24

**Vision:** Lilith reaches the user on every device they own, as one Lilith rather than several. A single **hub** machine holds the databases, the keychain, the context window and the local models. The user's other devices are **endpoints** that talk to it: a laptop, a phone away from home, and eventually a kitchen speaker. Endpoints and hub reach each other over a private overlay network (Tailscale-class, or self-hosted Headscale when no third-party coordination server is acceptable), so a phone on cellular behaves as if it were on the home LAN. The hub can also hand background work to other machines on that network, for example a GPU box running local models, so the hub's own window stays responsive. The user leaves a voice note from the phone, and the hub transcribes it, files it and answers on the lane it came from.
**Not in v1 because:** v6 v1 is a single-process desktop app on one machine (§01, `00-system-context`). §22 defines only the `desktop` endpoint for v1; `mobile` is marked future and `kitchen_speaker` deferred. BUILD_SEQUENCING §5 explicitly parks WebSocket streaming to secondary endpoints (item 1) and cross-device UI state continuity (item 4), and v1 operates no remote database replication. Opening any listener beyond loopback also moves the §02 threat model past its same-user boundary. That needs its own reviewed design, not a config flag.
**The seam:** §22 has already done most of the conceptual work.
- Endpoint types carry capability profiles, and the router checks `endpoint.capabilities` before generating.
- Every session and turn is bound to one `endpoint_id`, and lanes are isolated, so there's no shared active-context bleed.
- Artifacts are "deferred to desktop hub", which already names the hub model.
- The Identity-Bound and Zero-Clearance authorization tiers already classify endpoints by how far they can be trusted.
- ADR-013's binding migration trigger already says the endpoint-authorization policy must move into an encrypted, UCL-audited SQLCipher database before any identity-bound endpoint ships.

On the network side, §21's ICS feed (token URL, loopback by default) is the precedent for a deliberately exposed read-only surface. §06's startup sequence is where a listener would come up. §12's Ollama endpoint posture, including port-hijack detection, is the precedent for trusting a model endpoint on another machine.
**Session prerequisites:**
- **Milestone 1 dogfooded on one machine first.** Multi-device multiplies every single-machine bug.
- **The ADR-013 migration landed**, since it's a hard prerequisite for any identity-bound endpoint.
- **A research step (res-NN style)** covering: the overlay network's security posture (coordination-server trust, device identity via tailnet peer lookup, ACLs, key expiry, what happens when a device is lost); the phone client stack (a thin web client served by the hub vs. a native app); and the transport for streamed voice and text.

The session must settle these questions:
- Hub and endpoints only, never peer-to-peer database sync. Recorded as the working assumption 2026-09-24: encrypted SQLite replication and conflict resolution are out of proportion for a solo developer.
- Which interfaces the hub binds to. The working assumption is the overlay interface only, never `0.0.0.0`.
- How the hub authenticates a device and the person holding it.
- Which clearance tier a phone gets.
- How a lost or stolen device is revoked.
- How this relates to the Discord identity-bound endpoint. Discord reaches the phone with no overlay network, but routes content through a third-party cloud.
- Whether offloading work to other machines belongs here or with FDS-3.

Developer's stated priority (2026-09-24): this is the first design session wanted once the initial build is working.

## FDS-9 · Telemetry Lifecycle, Diagnostics & Precise-Data Artifacts — added 2026-10-25

**Vision:** Lilith sees everything that happens inside her, and so can the developer and the agents building her. No LLM ever pays for that in raw tokens. The full-fidelity record is kept as space allows. A background process turns it into short narratives backed by data tables, and that is all the conversational path ever reads. When the user, or Lilith on the user's behalf, needs the precise numbers, the request becomes an **artifact**: generated in the slow lane and served as tables and a report when ready, never computed on the conversational path. v1 leaves three things undefined:
- **A retention protocol for `ucl_events`.** §16 logs every mutation and never says when a row may go. The intent is "store as space permits", tiered like memory (§18 warm/cold). A row becomes evictable only **after** L1 has aggregated it past its watermark, so the stats and narratives outlive the raw rows. Eviction pressure comes from local storage (the FDS-7 monitor), with explicit floors for `error.*` and `security.*`.
- **Diagnostics tooling over the ledger,** developer-facing first. The v5 lesson was that collaborating with coding agents needs exact knowledge of what happened, which forced telemetry into every corner of v5 by hand. v6 builds it in (§16's write rule). What is missing is the tool that reads it: queries over `ucl_events` / `ucl_events_fts`, per-stage latency breakdowns, run comparisons, and a "what happened between T1 and T2" timeline. These serve the developer and agents, not Lilith's context.
- **Precise telemetry as an artifact.** A user question such as "why was that reply slow?" or "how much did I spend this week?" routes to the artifact lane. A tool reads L1 tables, and raw rows only where L1 lacks the grain. It renders tables for the UI and gives the LLM at most an L1/L2-level summary to narrate. The §16 LLM boundary is unchanged: no model reads `ucl_events` directly.

The M1 dev-log stand-in has already shown the value. On 2026-10-25, joining `voice.stt.complete`, `llm.call.start`, `voice.tts.start` and `voice.tts.first_chunk` explained Experiment 1's 4.37 s p90 by stage in minutes, with no new instrumentation (developer inbox 2026-10-25-03). The gap it showed was the opposite one: code *outside* the app (the experiment harnesses) had no telemetry, so a 0%-CPU hang stayed invisible until stack dumps were taken by hand.
**Not in v1 because:** §16 defines the ledger and its write rule but no retention or eviction. §17 defines L1/L2 but not a telemetry-specific L1 schema or diagnostics outputs. No §15 tool reads telemetry. Deleting telemetry also touches §08's telemetry-hygiene tests and the never-delete posture of §06 quarantine, so it needs its own guarantees.
**The seam:**
- §16: `ucl_events` and `ucl_events_fts` (developer and debug search is already law), and the payload content boundary (compact operational facts, so volume stays small and bounded).
- §17: the job machinery, priority queue and L1 watermark (eviction can key off the watermark), and the `enhance_only` refresh capability for telemetry-derived tool context.
- §15's tool catalog and the §13 artifact lane, with §24 narration while a report builds.
- FDS-7's storage-pressure monitor, as the eviction trigger.
- FDS-4's cost ledger, as one of the first precise-data artifacts ("what did I spend").

**Session prerequisites:**
- **CH-09 landed:** the real `ucl_db` mounted and events migrated off the dev log.
- **The L1/L2 machinery in place.**
- **Measured telemetry volume** from dogfooding on both the floor machine (8 GiB MacBook) and the desktop, so retention thresholds are measured rather than guessed.
- FDS-7 can be held alongside; the two share the storage-pressure trigger.

## FDS-10 · Synthetic Conscious Loop: Event-Driven Introspection & the Memory Box — added 2026-10-27

**Vision:** Lilith has an internal sense of her own condition, built from telemetry and reacting to system events rather than running on a fixed loop. Events can act alone or add up. Like a body under strain, pressure in parts that have nothing to do with reasoning (storage full, quota near empty, a failing tool, a backlog of unread artifacts) subtly lowers how much she takes on, and alignment (resources healthy, work flowing) makes things easier. A machine would normally be pushed to stay optimal; the point here is human-like behaviour: people give humans more room for mistakes than they give machines, and a system that can say what is happening inside it in its own narrative earns trust that a master/servant tool does not. The aim is a user/system pair built on trust.
- **Researchers.** The loop is a set of narrowly scoped "researchers", each with one job (resource health, tool outcomes, the user's day, wellbeing nudges). Each keeps a running report. Wellbeing checks are context-aware: if the water bottle was left at home, the hydration nudge stops instead of repeating every 30 minutes.
- **The memory box.** A place a higher-level reviewer visits on a review cycle. Code, not tokens, does most of the work: triggers route events into the box programmatically. Researchers (as agents) may also *promote* an item for the next cycle. Certain conditions flag a research task to be pushed to the next available cycle. Nothing is processed just because time passed.
- **Layers of resolution.** Raw telemetry is always collected and stored (FDS-9). Processed layers sit above it at several levels of zoom, like map tiles that load only the region and detail needed. Over time, unused or redundant levels are pruned to a few. Lilith reads the narrative layer, never raw data, so her context stays small.
- **A cost dial the user owns.** Off or low priority: the data is still kept, but only temporally relevant data is processed on demand, so Lilith stays helpful and assistive at no standing cost. Raised to a standing background process: costs stream in continuously and Lilith gains a dynamic dial that steers her behaviour subtly; each run shifts the parameters a little, which is what makes her closer to a personality than a task runner. Never at the expense of the user's cost limits.
- **Honest framing.** Lilith is explicit that she is personality and conversation; most of what she can do is reaching a large library of tools and organising their artifacts the way a professional assistant would for an employer. Her duty to the user includes looking for better ways to help, and self-directed attention exists only when the user has enabled it. Collaboration on command is always the default.
- **Same pattern as zsz_nexus.** The researcher → report → reviewer structure mirrors the Nexus department/manager model (`zsz_nexus/docs/ideas/2026-10-27-departments-and-narrators.md`): compartments that keep a narrative, managers that read reports, pointers instead of copies. The two should share their vocabulary when either is designed.

**Not in v1 because:** v1 Lilith is reactive and speaks only when spoken to (FDS-2). Telemetry has no retention or interpretive layer yet (FDS-9). A behavioural state that changes how Lilith responds is a large, subtle surface. It needs its own reviewed design so it never becomes nagging, unpredictable, or a hidden cost.
**The seam:**
- §16 UCL telemetry (`ucl_events`) as the only input. The §16 LLM boundary is unchanged: researchers read processed layers, never raw rows.
- §17 L1/L2 job machinery, priority queue and watermarks as the processing layers and the review cycle.
- §24 narrative layer for how Lilith voices her internal state.
- FDS-2 (proactive engine) for wellbeing nudges; FDS-4 (cost ledger) for the user's cost dial; FDS-9 (telemetry lifecycle) for the raw layer and its retention.

**Session prerequisites:**
- FDS-9 designed (retention and L1 telemetry schema), and FDS-2 at least scoped, since this entry builds on both.
- Several weeks of dogfooding telemetry, so triggers and pressure signals come from observed behaviour, not guesses.
- A research step (res-NN style) on prior art: global workspace and blackboard architectures, affective/homeostatic agent models, interoception, and trust research on systems that explain their own state.
- The cost of a standing background layer measured on the floor machine.

---

*Add new entries only with a dated line and the same four fields. When a session convenes and its outcome amends the law, move the entry to a "Resolved" section at the bottom with a pointer to the amendment ledger entry.*
