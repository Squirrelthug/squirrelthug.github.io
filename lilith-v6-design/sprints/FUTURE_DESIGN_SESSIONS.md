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

---

*Add new entries only with a dated line and the same four fields. When a session convenes and its outcome amends the law, move the entry to a "Resolved" section at the bottom with a pointer to the amendment ledger entry.*
