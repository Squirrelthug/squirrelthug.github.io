# Report 03 — A Face and First Breath (CH-05, CH-06)

*Covers Chapter CH-05 (Frontend Shell — §26, §22, §27, §28) and Chapter CH-06 (Milestone 1 Integration & Dogfood — every Milestone-1 section, closed as a system). This is the stretch where the pieces become a creature: the window, the orb, and then the first complete breath — microphone to speaker with a mind in between — and the beginning of daily use.*

---

## Where we are in the story

Everything essential now exists in pieces. A trustworthy skeleton. Ears and a mouth. A routed, privacy-guarded mind with a personality and a searchable memory. What's missing is a body you can look at and the wiring that makes all of it one organism. These two chapters are deliberately paired in one report because they answer the same question from two sides: *what is it like to be in a room with Lilith?* CH-05 answers it visually; CH-06 answers it end-to-end.

There's also a milestone-weight moment buried in this stretch, and it deserves to be named: at the end of CH-06, the developer starts *using* Lilith v6 every day. Not testing — using. Every era of this project has chased that moment; v5 reached it and taught how much reaching it matters, because daily use surfaces truths that no test suite finds. Everything after this stretch happens with a live user in the loop.

## What we're building, in plain English

**CH-05 builds the room.** A PySide6 desktop window with a chat view — her words and yours as bubbles, tool work as panels — a typed input box for when speaking isn't right, and a stub settings screen where the API key goes in and lands safely in the OS keychain. Above it all, the orb: a small GPU-rendered sphere that idles calmly and pulses with the sound of her voice and yours. All of it wired to the backend through a single thread-safe command bus, because Qt widgets and asyncio pipelines live in different worlds and every crossing goes through one door.

**CH-06 makes it breathe.** The full loop, assembled: you speak; voice activity detection notices when you stop; Whisper transcribes; the router decides; the context manager assembles; the PII gate tokenizes; Claude streams; the reverse-substitution restores; Kokoro speaks; the orb pulses along. Dictate a note while making coffee. Hours later: *"What did I say about the concrete mixing ratio?"* — and she tells you, out loud, from her encrypted memory. One database, one tool, no dead code from excluded sections, telemetry flowing to the dev log. The walking skeleton, walking.

## What we'll be thinking about

**The orb is honesty rendered.** It would be easy to file the orb under decoration, and the Milestone-1 scope is intentionally modest — idle plus voice-reactive pulsing, no full state machine yet. But even the simplified orb carries a design conviction worth holding onto: *the user should be able to see the system's state at a glance, truthfully.* When she's listening, it shows. When she's speaking, it moves with her actual amplitude — real audio data driving real pixels, not an animation pretending. As the system grows (background tasks, errors, long-running artifacts), the orb becomes the ambient face of the no-blind-spots principle: the telemetry story of "what is Lilith doing right now," told in light instead of logs. We build the simple version now with uniforms and hooks shaped for that future, because in CH-14 the full state machine will want them.

**The command bus is a discipline, not a convenience.** The single thread-safe `UICommandBus` between backend and GUI is the modular-monolith lesson applied to the frontend: one crossing point, typed events, no widget ever touched from the wrong thread, no backend logic ever living in a click handler. This is the kind of rule that feels ceremonious with three UI events and saves the project with three hundred. Part of CH-05's definition of done is a review-level check that no code sneaks around the bus — an easy thing to verify now, an impossible thing to retrofit later. The deeper principle: the GUI is a *client* of the system, not the system. Lilith exists fully in the backend; the window is one way to be near her. That framing keeps the door open for every future surface — and it's also why the chat screen renders *typed* input through the same pipeline as voice: one mind, several mouths.

**Two lanes must look like two lanes.** The chat screen distinguishes conversational bubbles from tool panels visually, and that's not cosmetic — it's the two-mode architecture and the separate artifact layer teaching the user how to think about the system. A quick answer looks light because it was light. Tool work sits in a panel with a name on it because it *is* a distinct thing that a distinct machinery produced — the artifact layer made visible, separate from Lilith's own voice, exactly as she describes it when she's being honest about her nature. The UI is doing philosophy here; we should notice.

**Integration is where honesty about state pays off.** CH-06 contains no new features by design — its scope is wiring, gap-closing, and the disciplined audit. The thinking work is different in kind: it's the first time we debug the *system* rather than a module. A pause that's too long — is it VAD offset, Whisper batch time, router overhead, network, or TTS synthesis? This is precisely why telemetry events were required from every component along the way, even while they only land in a humble dev log: the walking skeleton must be *legible*, because CH-07 is about to put a stopwatch on it and we need to know where every millisecond lives. Expect the sprint for CH-06 to be short on tasks and long on verification.

**Dogfooding is a commitment, not a vibe.** The definition of done requires an actual dictate-and-recall session used in real life, and from that day forward the developer is Lilith's first client. This changes the project's epistemology: from here on, the backlog gets its truth from lived friction, not speculation. It's also the first, smallest delivery of the 80% principle in the flesh — notes captured hands-free in passing, retrieved conversationally later, with all the mechanics (routing, search, narration) done for you. Modest. Real. Daily.

## Engineering at a high level

CH-05's build order: shell and bus first (everything else plugs into them), then the chat screen against the existing text pipeline, then the orb as an independent widget track, then the settings stub. The orb is genuinely parallel work — ModernGL inside a Qt widget shares nothing with chat rendering — and the sprint can treat it so. The seam to respect: amplitude data must flow from the audio threads to the orb through the same bus discipline as everything else, at UI frame rate, without ever blocking audio.

CH-06's engineering is sequencing and measurement: wire the real microphone path into what the text path already proved, chase down the thread and lifecycle seams (what happens when you speak while she's speaking? when you close the window mid-response? when the network hiccups mid-stream?), and run the M1 scope audit with the same seriousness as a security review. The failure modes that matter here are the rude ones — barge-in, shutdown mid-task, empty transcripts — because daily use will hit all of them in the first week.

What we defer without guilt: every other screen, onboarding, the full orb state machine, markdown niceties, endpoint capability logic beyond the desktop. The window ships minimal; the *loop* ships whole.

## What done feels like

One evening, you stop testing and just... use her. You're moving around the kitchen, you say something worth keeping, and she keeps it. The orb breathes in the corner of the screen — calm when idle, alive when either of you talks. Later you ask, half-distracted, what you'd said — and the answer comes back in her voice before you've finished reaching for a notebook you no longer need.

Under the hood it's everything these six chapters built: encryption, detection, routing, tokenization, streaming, narration, persistence, rendering — firing together in under a few seconds, leaving telemetry footprints the whole way. Milestone 1 is alive. What it doesn't yet have is *proof* — the measured, falsifiable evidence that the two big bets underneath it hold. That's the next report, and it's the one where we let the data tell us if we were wrong.
