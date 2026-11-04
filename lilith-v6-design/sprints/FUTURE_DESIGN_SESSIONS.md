# Lilith v6 — Future Design Sessions (Vision Parking List)

Companion to `BUILD_SEQUENCING.md` §5 (parked *scope*). This file parks *vision*: capabilities that are part of Lilith's intent but are **not in the frozen v1 law**. Nothing here may be built, stubbed, or "prepared for" during the v1 chapters — each item enters the law only through a documented design session per the amendment convention in `../README.md`. What the v1 build *does* owe each item is its seam: the already-designed extension point listed below, kept clean.

The governing idea (recorded 2026-08-03): **Lilith is the kind of harness that intends to use all other harnesses.** She is a conversational agent who keeps the context window on the user's machine, hands any model exactly the context it needs — sufficient, minimal, cached when efficient — and wields a growing catalog of tools and external systems on the user's behalf, so the user makes well-informed decisions without doing the homework (the 80% principle).

**Developer restatement, 2026-11-03:** she is *another me, but digital*, able to handle all the things the user forgets. She does not hold everything herself: asked for a podcast stored away on a drive, she goes and gets it and serves it (FDS-7). How much she does scales with the person: one user has her automate scripts, another talks through relationships with her and has her find rare enamel pins online, the developer uses her across podcasting, programming, game story design, scripts and novels through the Nexus (FDS-11). She can do a lot, a little or almost nothing. The picture-led explainer of this vision is the site page `vision/index.html`.

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

**Developer input, 2026-11-03:** the morning brief, learned durations and prep time between events are recorded as their own entry, FDS-12, which depends on this one.

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

**Developer input, 2026-11-03 (go and get it):** knowing where a thing is must extend to fetching it. Asked for a podcast episode stored on an external drive or in the user's own cloud, Lilith locates it through the registry, retrieves it (with consent, reporting honestly if the drive is not reachable) and serves it: plays it, or hands it to the device the user is on. Retrieval is read-only and never moves the original.

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

**Developer decision, 2026-11-02: multi-node is a v7 job.** The security work is too large for v6, and the developer is content that v6 runs on the Linux desktop and the MacBook as separate instances. This supersedes the 2026-09-24 priority below (first session once the initial build works); FDS-8 remains the record of the idea and of the input above.

Developer's stated priority (2026-09-24): this is the first design session wanted once the initial build is working.

**Developer input, 2026-11-01 (after the first dogfood on Linux and a MacBook):** the build already runs on both machines, but as two separate Lilith instances. Nothing lets one "master" Lilith know that she is installed on other hardware for the same user. What the developer wants, as stated:
- **First run asks what this install is:** a *new* Lilith, or an *extra node* of the user's existing Lilith. The developer's own order would be the desktop first, fully set up, then the MacBook as a node.
- **Hardware-aware use of nodes:** the system uses the user's available machines to best advantage, and if the user installed in a different order the system *reorganises* to suit.
- **Adapting to nodes going down.** The developer flagged this as likely very complex and possibly something to shelve to v7, or to build as a tool.
- **Security may force a ground-up v7:** a design where several machines share one user's data may not be reachable by extending the v6 single-machine security model.

How this meets the existing FDS-8 text (agent's reading, for the session to confirm):
- Enrolment ("new, or join an existing Lilith") is the natural *first-run* form of FDS-8's open question "how the hub authenticates a device and the person holding it". It also needs an answer for the opposite case: what a node does with data it already holds when it joins.
- Hardware-aware use fits FDS-8's "the hub can hand background work to other machines" and FDS-3 (per-task model choice); the new need is that nodes *advertise capabilities* (the §05 tier profile already exists per machine) so the hub can choose.
- **Node loss splits into two very different problems.** A *worker* node going down is graceful degradation: the hub stops routing to it. The *hub* going down is a failover problem: another node must hold the keys and a current copy of the data, which is exactly the encrypted replication and conflict resolution the 2026-09-24 working assumption ("hub and endpoints only, never peer-to-peer database sync") rejected as out of proportion. Automatic reorganisation therefore means either keeping that assumption (fixed hub; hub down means unavailable) or reversing it.
- The security question is a research step, not an assumption: whether §02 (credentials) and §03 (SQLCipher key model, same-user boundary) can extend to a second machine without a rewrite. If they cannot, that is the case for a v7 built for multi-node from the start.

Options for the session to weigh (none decided):
1. **v6 FDS-8 scoped to a fixed hub:** first-run enrolment, capability advertisement, worker-node degradation; hub failover and automatic reorganisation shelved to v7.
2. **Hub with a standby replica:** adds encrypted replication and a failover rule; large, security-sensitive.
3. **v7 ground-up multi-node design:** only if the research step shows the v6 security model cannot extend.

Note for sequencing: the first-run question exists today as a one-way door. A v6 install has no "join" path, so whatever the first-run flow (§25) records about its own identity should not assume it is the only Lilith for the user. That is a constraint on the current build only if the session picks option 1 or 2.

**Developer input, 2026-11-03:** the phone or tablet is meant to become the main way the developer manages Lilith: speaking to her through it and reading short-lived cards with a dynamic view (the Surface idea, the 12-column card model in the Nexus research). Screen size is then the only thing the user chooses. This raises the priority of a thin, read-mostly endpoint even while full multi-node stays a v7 job.

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

**Developer input, 2026-11-03:** within herself, Lilith applies the same principles as the Nexus (FDS-11) to manage the user's life: compartments, reports, review, and no emotional attachment.

## FDS-11 · Lilith and the Nexus: Specialisation by Context, Never by Strapping In — added 2026-11-03

**Vision (developer, 2026-11-03):** Nexus is how Lilith specialises and how that specialisation stays where it belongs. It is **not** a hub for smart-home devices or outside services; that is FDS-1's territory, and the plain-words guide described it wrongly before 2026-11-03. The developer's description, in order:
- **A tree of cells shaped like businesses.** At the top is the **MASTER nexus**, run by a manager. Below it are divisions (programming, writing, the podcast, game story design, film and TV scripts, novels), and below those the projects, each a **cell**. A division such as writing is an editor or publisher layer over every writing cell beneath it. Cells can nest. The rigid business-like structure is where the standards live, so once a pipeline is built it can be driven from any seat along the structure.
- **Every cell has a harness already in place.** Any agent, even a fresh one with no prior context, can step into a cell and start its job, because the cell holds the standards, the history and the "where we left off" record.
- **Lilith never straps into a harness.** The Nexus is a vast mech suit she can travel all over and ask anything of; she knows what is in each level and can talk to the user about it, and hold design conversations there. The cells themselves run autonomously when they run. When the user agrees a design with her and it meets the cell's schema standards, she hands it to the ready harness and the cell builds it.
- **Moving into a mode is moving down the tree.** When the user decides it is time to code, or to manage a running project, Lilith steps into that level's context (programming is one or more levels down) and is a specialist there. When they leave, the specialisation stays in the cell; her own window keeps only the facts ("we spent the afternoon on x, y and z").
- **Reports roll up, nothing compounds.** The lowest agents write full reports. The layer above reads all of them and writes its own report, and so on to the top. Every layer reads the full reports of the layer below for each brief, so summaries are never summaries of summaries; and Lilith or the MASTER nexus can step into any cell and read its full verbose report instead of the abbreviated ones higher up. Some text is processed more than once by design; the navigation conventions must make that efficient.
- **Small windows everywhere.** Standing at the top never floods the context. Like the autopilot's managers (capped near 80k tokens), every agent in the Nexus works inside a bounded window, because the work is compartmentalised and layered. Only walking the tree gives more context, and even then it is abbreviated.
- **Tree plus graph.** The tree is the chain of command; a relational database across the whole Nexus links cells that share things (a podcast episode that cites a research artifact from a writing cell). The MASTER nexus, and Lilith working with it, query the graph.
- **History is the truth.** Constant history keeps everything straight. Memory is a database with provenance and telemetry built in: no blind spots.
- **Budget-aware scheduling.** Not everything runs at once, and nothing has to be used. The MASTER nexus manager coordinates with Lilith to schedule sequential work as budgets open: a plan window resets, an account is topped up, a quota returns.
- **What a cell produces is the user's.** Data, insights and artifacts made in Nexus sessions are part of the user's personal knowledge network: Lilith ingests and catalogues them with provenance, so she can recall and serve them later.
- **Gates that keep the work the user's.** Creative cells are built on the educational literature of their craft. When a novel turns out to lack an act, the cell says so, gives advice and does research on the user's behalf, but the user decides what fills it. The user may tell Lilith to generate it anyway; the cell records that the choice and its consequences are the user's, because agent-filled creative gaps are rarely good.
- **The end state.** The user gives agents enough context to run work autonomously, edits the last 20%, and checks in when they come back to that headspace.

**Not in v1 because:** the Nexus is a separate project (`Squirrelthug/zsz_nexus`, research phase: design draft, passes R01..R06, the departments-and-narrators idea of 2026-10-27, and the Surface idea that gates its design). v6 v1 has no external tool surface (FDS-1), no standing background work (FDS-2) and no cost ledger (FDS-4), and all three are prerequisites for Lilith using a Nexus.
**The seam:**
- §15 tool system and FDS-1: Lilith reaches the Nexus as a governed tool provider (the Nexus design already plans an MCP surface), so reading a cell or handing it a design is a tool call with a narrative, telemetry and consent.
- §13 artifact lane: a hand-off to a cell is slow-lane work; Lilith narrates while it runs.
- §18 memory and §29 vault: ingesting cell outputs as pointers with provenance, under the custodian model (index where it lives; never copy without consent).
- §16 telemetry and FDS-9: one event vocabulary, so a check-in reads telemetry, not transcripts.
- §14 context window manager: stepping into a cell is the CWM loading that cell's context block instead of her everyday one.
- FDS-10: the same researcher-report-reviewer pattern; the two should share vocabulary.

**Session prerequisites:**
- The zsz_nexus design past its research phase (R05 tool abstraction, R11 departments and narrators) and the Surface idea resolved.
- FDS-1 designed (how any outside tool provider is trusted), and FDS-4 at least scoped (budget-aware scheduling needs a ledger).
- A research step on cognitive-apprenticeship and craft-education literature for the gate design of creative cells.
- The autopilot's lessons (account routing as data, a workspace lease, session caps) carried in as the first worked example of a cell harness.

## FDS-12 · The Daily Rhythm: the Morning Brief, Real Durations and Time Between Things — added 2026-11-03

**Vision (developer, 2026-11-03):** Lilith wakes up with the user and gets them started on the day, the way JARVIS briefs Tony Stark: as much or as little as they need. Over time, with built-in presets as starting points, she finds the best way to communicate with this user after they wake, so they do not have to think about or remember things. She knows how long things take and when they clash. There is preparation between playing outside and going to dinner, so those are never scheduled back to back. Reminders say what is happening and why (the prep time, the travel, what clashes), so the user is informed at all times. When the user is away from the desk, she can say factually what was worked on (x, y and z) without carrying the specifics.
**Not in v1 because:** v1 Lilith speaks only when spoken to (FDS-2); §21 events have no duration model beyond start and end, and no transition, travel or preparation time; there is no wake-time routine.
**The seam:** §21 calendar (events, `when` policy, the user's day boundaries from DS-2 and P01's `evening_starts_hour`/`night_ends_hour`); DS-6 background reminders (delivery while the window is closed); §17 L2 profiles (learned durations and rhythms); §24 narrative (what the brief sounds like); DS-7 presets (how much she says).
**Session prerequisites:** FDS-2 designed, since a morning brief is initiated speech; weeks of dogfooding calendar and reminder telemetry, so durations and buffers are learned rather than guessed; DS-6 decided; research on interruption and briefing design (the research wave 2 conflict "proactivity vs shame and creepiness" applies).

## FDS-13 · How She Speaks: Modality, Initiative and the Right to Stay Silent — added 2026-11-03

**Vision (developer, 2026-11-03):** Lilith adapts how she communicates to the user. Some users do not want her voice to change, or do not want her to speak much even when they speak to her; they may want text, or only a confirmation. Personality layers let her stay useful while choosing how she speaks and which thoughts or observations she shares: more proactive, or more inclined to wait to be spoken to. She does not reply to everything the user says; **silence is a valid reply**. The aim is that the user only touches a keyboard or a computer when they want to: speech through whatever device is at hand, and short-lived cards with a dynamic view on a phone or tablet for anything that must be read (the Surface idea, FDS-8).
**Not in v1 because:** v1 answers every turn; the router has no "no reply" outcome; output modality is fixed per endpoint (§22), not chosen per user and per moment. DS-7 presets add dials for chattiness, humour, formality and volunteering, but not modality, and not silence.
**The seam:** §13 router (a `silent` outcome alongside the existing ones, logged in `router.dispatch` telemetry so a silence is never a blind spot); §22 endpoint capabilities (text, speech, confirmation-only); §23 personality and DS-7's VOICE files and dials; §24 narrative; the persona charter (P01-22), which holds under every setting: warm, never a companion, no emotional attachment.
**Session prerequisites:** DS-7 built; telemetry on which replies users skip, interrupt or ask to shorten; a research step on conversational turn-taking and when an assistant's silence reads as rude rather than respectful; FDS-8 or the Surface idea for the card side.

## FDS-14 · Messaging Channels: Reaching Her Through the Apps People Already Use — added 2026-11-04

**Vision (developer, 2026-11-03):** Lilith ships able to talk through the channels people already use to talk to each other: Discord first, then others such as Telegram, Signal, SMS and email. They are a reliable way to exchange messages *and files* with anyone who has internet access, at little or no cost. Today the only way to reach her is from a machine on the user's own network, which is limiting and is not her final design. A channel is a way *in* to the one Lilith on the user's hub, not a second Lilith: the same memory, the same tools and the same persona, with a lane of its own. It works away from home with no overlay network and no app of hers to install. v5 had a Discord integration; v6 has none yet.
**Not in v1 because:** §22 defines only the `desktop` endpoint for v1. ADR-013's binding migration trigger says endpoint-authorization policy must move from `config.json` into an encrypted, UCL-audited database before any identity-bound endpoint (§22 names Discord as the example) ships. Every channel sends the user's words and files through a third party's servers, which meets DS-1's "nothing private leaves" and EDICTS 5 head on. Every inbound message is untrusted text arriving with the user's authority, so the prompt-injection defences must be in place before a channel opens. FDS-2 (speaking first) is parked, so she could only reply, never message first.
**The seam:** §22 already has most of the shape:
- per-endpoint lanes with no shared active context, and the desktop chat's side-by-side view of lanes;
- capability profiles that the router checks before generating;
- the **Identity-Bound** tier ("can be configured to filter and respond only to an authorized user identity, ignoring all other requests") and **Zero-Clearance** for devices that cannot prove who is speaking;
- artifacts "deferred to desktop hub".

Elsewhere: ADR-013 (the policy store migration); §02 (each channel's bot token in the keyring); §06 (where a channel listener starts and stops); DS-1 and the tool-argument guard (what may leave through a channel reply as well as through a tool); §17 and the cloud masking path (a channel message is cloud-bound text twice over: once to the channel's servers, once to a cloud model); FDS-13 (text and confirmation-only replies suit channels); FDS-8 (the hub; its open question "how this relates to the Discord identity-bound endpoint" moves here); FDS-2 (messaging first, later).
**Session prerequisites:**
- **The ADR-013 migration landed**, since it is a hard prerequisite for any identity-bound endpoint.
- **The developer's security review items for untrusted input closed**, since a channel turns every inbound message into third-party text.
- **A research step (res-NN style)** on prior art:
  - OpenClaw (formerly Clawdbot): one gateway process with an adapter per channel, and pairing before an unknown sender is answered. Its public security problems are as instructive as its features.
  - v5's Discord wiring.
  - Each candidate channel's identity guarantees, encryption (end-to-end or not), file limits, rate limits, cost, bot terms of service, and what the provider keeps.

The session must settle these questions:
- **Which channels ship first.** The working assumption is Discord alone, then one end-to-end-encrypted channel (Signal or similar) if the research supports it.
- **How a channel account is bound to the user:** pairing from the desktop, a one-time code, and revocation in one step.
- **The clearance tier per channel**, and what a channel may carry. Candidates: no unmasked personal data in replies by default; a per-category opt-in (health, money, location, in line with FDS-6); files only from an allow-listed folder; a "check your desktop" reply for anything private.
- **Inbound files:** quarantine, type and size caps, and never parsed by the model as instructions.
- **Groups and other people:** a channel is for the user only, and she ignores everyone else unless a later session (DS-5, multi-user) says otherwise.
- **Telemetry:** every channel turn and refusal logged with `endpoint_id`, with no message text in the payload.
- **The edge of the scope:** the podcast-operator Discord bot (HANDOFF §3) stays a separate tool exposed through FDS-1, not part of this entry.

---

*Add new entries only with a dated line and the same four fields. When a session convenes and its outcome amends the law, move the entry to a "Resolved" section at the bottom with a pointer to the amendment ledger entry.*
