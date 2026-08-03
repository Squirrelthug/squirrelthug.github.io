# Report 01 — Foundation and a Voice (CH-01, CH-02)

*Covers Chapter CH-01 (Foundation & Skeleton — §01, §02, §03, §04, §06, §08) and Chapter CH-02 (Voice I/O Pipeline — §05, §09, §10, §11). The law for this stretch is those ten section pages; this report is the story of how we'll work through them and what we'll be thinking about.*

---

## Where we are in the story

This is the first code of v6. Nothing exists yet — that's not a gap, it's the point. v5 was archived precisely so that this moment could happen on purpose: an empty directory, a frozen design, and the discipline to build the boring parts first and build them right.

The temptation at the start of any rebuild is to sprint toward the part that feels like the product — the conversation, the personality, the orb. Every previous era of this project gave in to some version of that temptation, and every one of them paid for it later: credentials scattered where they shouldn't be, databases that grew schemas nobody designed, silent failures with no record. The construction rule from the February blog post governs here more literally than anywhere else in the build: **you don't frame walls before the foundation cures.** These two chapters are the pour and the cure.

## What we're building, in plain English

**CH-01 builds a skeleton you can trust.** By the end of it, the app does almost nothing — and does it perfectly. It starts. It refuses to start twice. It derives an encryption key the proper way, opens one encrypted database, and closes it cleanly when told to shut down. Its secrets live in the operating system's keychain and nowhere else. Its tests run against real encrypted databases, not mocks. That's the whole chapter, and every piece of it is load-bearing for the next thirteen.

**CH-02 gives the skeleton ears and a mouth.** Sound comes in from the microphone and becomes accurate text; text goes out and becomes a natural spoken voice. The two halves don't talk to each other yet — there is deliberately no brain between them — but each is real, tested, and running on the actual hardware. When this chapter closes, you can speak to a machine and watch your words appear, and you can hand it a sentence and hear Lilith's voice say it. The first moment this project feels *alive* happens here, well before it's intelligent.

## What we'll be thinking about

**Security is a foundation, not a feature.** The single most expensive lesson of v5 was that security added later is security fought for room. v6's law makes it structural: SQLCipher from the very first migration — there is never a plaintext database at any point in this project's history. Keys derived with Argon2id from a master passphrase held in the OS keychain. The insecure-fallback checks active from day one, so if a machine can't provide a real keyring the system *says so* instead of quietly degrading. Getting this right in CH-01, when there's one database and no features, costs almost nothing. Getting it wrong here poisons everything downstream, because five more databases will be keyed by the same machinery in later chapters. We will think of `SessionKeyManager` and the salt registry not as chapter-one plumbing but as the security perimeter of the entire future system, built while the attack surface is still tiny enough to reason about completely.

**Discipline about scope is the product of this chapter.** The Milestone-1 table says *exactly one database* and means it. No "while we're here" second schema, no stub of the telemetry DB, no speculative table for contacts. The excluded list (§07, §16, §17, §19, §20, §21, §25, §29) is a fence, and part of CH-01's definition of done is an audit that nothing inside the fence exists. This sounds bureaucratic; it is actually the whole reason a solo developer can move fast later. Every piece of speculative structure built now is a piece that would be built without its design section in hand, and the first rule of this build is that only what is written gets built.

**Conventions are cheaper now than ever again.** `pathlib.Path` everywhere. Module boundaries with one dependency direction. Tests that use real databases so the tests exercise the same code paths the app does. The standard import shapes, the standard place paths come from, the standard way a module is laid out. None of these decisions are interesting, and that's why they're decided — the design already made every one of them, and CH-01's job is to make the codebase's very first files exemplify them, because every later file will be written (largely by agents) in imitation of the files that already exist. The first hundred lines of this repo set the accent of the next hundred thousand.

**Audio is where the real world bites.** CH-02 is the first encounter with hardware, drivers, sample rates, and timing — the least deterministic layer in the whole design. The engineering posture here is humility: keep the callback paths thin (enqueue frames, do nothing clever), push all real work onto consumer threads, and treat the queues between them as the contract. VAD thresholds and silence windows come from the law, but the *feel* — does she stop listening too eagerly? does she clip the first syllable? — can only be tuned by a human with a microphone, which is why CH-02's definition of done insists on verification against real hardware and not just fixtures. We'll also be quietly gathering intuition for CH-07 here: every millisecond the audio layer spends is a millisecond stolen from the 3-second conversational budget, and the walking-skeleton latency benchmark will hold this layer to account.

**Hardware honesty starts on day one.** The §05 tier detection built in this chapter is small, but it carries a principle: Lilith always knows what machine she's on and never pretends otherwise. Whisper runs on GPU where a GPU exists and falls back to CPU where it doesn't, *by detection rather than by configuration*. This is the first instance of a pattern that recurs through the whole project — the system inspecting its own circumstances and adapting truthfully — and it's worth building it as the exemplar of that pattern rather than as a one-off switch.

## Engineering at a high level

The shape of the work: CH-01 is mostly sequential (structure → credentials → encryption → paths → lifecycle → tests), because each layer literally depends on the previous. CH-02 splits naturally into two parallel tracks — the input chain (capture → VAD → STT) and the output chain (TTS → queue → playback) — which meet only at the definition of done. Sprint tasks will reflect that: strict ordering in B01, looser ordering in B02.

What we expect to be easy: the individual libraries. `sqlcipher3-wheels`, `sounddevice`, `faster-whisper`, `kokoro-onnx` are all well-researched choices with their integration patterns already written down in the design and the res-files behind it.

What we expect to be hard, and will watch closely: the *seams*. Keyring behavior differs across machines; PortAudio device selection has sharp edges; VAD tuning is feel, not spec; and graceful shutdown — closing an audio stream and a database in the right order under a signal — is the kind of thing that works in the happy path and betrays you in the crash path. Tests will lean into the seams, not the libraries.

What we deliberately defer without guilt: packaging, CI, Windows and macOS specifics, and every kind of polish. Linux, one machine, running from a checkout. The design says cross-platform is infrastructure, and its chapter (CH-09) will treat it that way.

## What done feels like

There's a specific moment that ends this stretch: sitting at the MASTER machine, you launch the process from a fresh checkout by following the written setup steps. It detects the hardware, unlocks its one encrypted database, and waits. You speak — the words land in a log as text. You feed it a sentence — Lilith's voice says it aloud. You press Ctrl-C and it puts everything away cleanly. Try to start it twice and it politely refuses.

It doesn't converse. It doesn't remember. It doesn't think. But every promise it makes, it keeps — and for the first time in this project's four-year history, there is a codebase where *that* is true from the very first commit. The next report is about giving this trustworthy body a mind.
