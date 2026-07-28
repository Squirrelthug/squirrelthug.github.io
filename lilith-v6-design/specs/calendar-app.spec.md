# Feature: Calendar App (§21) — Lilith v6

**Design session:** 2026-07-27 · **Replaces:** §21 Finance App (shelved to post-v1 scope; see `BUILD_SEQUENCING.md` §5) · **Derived law:** `sections/s21.html` — this spec is the working artifact; the section page is the law derived from it.

## Overview

Lilith ingests the user's Google Calendar and keeps her **own** calendar up to date; she can write to her own calendar, but the user's calendar is safe from this untested system. `calendar_db` holds two strictly separated event stores: a read-only, provenance-tagged **mirror** of the user's Google Calendar events (`synced_events`, kept fresh by the §19 sync, existing to be overwritten by the next sync), and **Lilith's own calendar** (`lilith_events`, writable, modeled with iCalendar semantics: UID, SEQUENCE, STATUS). Lilith's calendar is published as a local, read-only ICS subscription feed so the user can keep seeing their day in the calendar view they have always used, while Lilith knows what the user knows. No Google Calendar write path exists anywhere in v6 v1; more telemetry is required before Lilith is ever granted the ability to manage the user's own calendar.

**User value:** most users will hopefully depend on Lilith to convey and organize their tasks throughout the day; some of those users *also* want a glance at the view they have always used. The information is identical either way — the value is that Lilith knows what the user knows AND the user stays informed in the way they have always been informed. The design must service that user.

## Functional Requirements (EARS)

### Two-store separation

- **FR-CAL-001:** The calendar application shall maintain the Google mirror (`synced_events`) and Lilith's own calendar (`lilith_events`) as two separate stores inside `calendar_db`, with no storage-layer merge between them.
- **FR-CAL-002:** When a §19 calendar sync runs, the sync pipeline shall create, update, and delete `synced_events` rows from Google data; the §19 sync shall be the only writer of Google-sourced fields in `synced_events`.
- **FR-CAL-003:** The system shall not permit any tool, UI action, or L2 job to mutate `synced_events` rows; the sole non-sync writer is the L1 echo-detection job, which sets only the local annotation column `echo_of_lilith_event_id` and never alters a Google-sourced field.
- **FR-CAL-004:** When Lilith creates an event, the system shall write it to `lilith_events` with a new RFC 5545 `ical_uid` (stable for the event's lifetime), `sequence = 0`, and `status = 'confirmed'` or `'tentative'`.

### Scoped write tools (`lilith_events` only)

- **FR-CAL-005:** Where LLM-callable calendar write tools are active, the tools (`calendar_event_create`, `calendar_event_update`, `calendar_event_cancel`) shall create, update, or cancel rows in `lilith_events` only.
- **FR-CAL-006:** When a write tool receives an event id that does not identify a `lilith_events` row — including any mirrored Google event id — the tool shall refuse the operation, modify no row, and return an explicit refusal message.
- **FR-CAL-007:** When `calendar_event_update` succeeds, the system shall increment the row's `sequence` so feed subscribers observe the change.
- **FR-CAL-008:** When `calendar_event_cancel` succeeds, the system shall set `status = 'cancelled'` and increment `sequence`; the system shall never hard-delete a `lilith_events` row through any tool.
- **FR-CAL-009:** When `calendar_event_cancel` is invoked on an already-cancelled event, the tool shall return success without modifying the row (idempotent; no additional `sequence` increment).

### Read tools

- **FR-CAL-010:** The read tools `agenda(period: str) -> str` and `event_lookup(query: str) -> str` shall run in `artifact_only` mode and shall return L2-style narrative text, never raw event rows (§20 pattern).

### No Google write path (v6 v1, normative)

- **FR-CAL-011:** The system shall not register, request, or expose any Google Calendar write operation in v6 v1: no write scope is requested, no write-back method is registered, and no tool definition exposes a Google Calendar mutation — reaffirming §19's read-only enforcement.

### ICS subscription feed

- **FR-CAL-012:** Where the ICS feed is enabled, the system shall serve Lilith-originated events (`lilith_events`) only; mirrored Google events shall never be serialized into the feed.
- **FR-CAL-013:** The feed server shall serve read-only HTTP GET at an unguessable token path (`/calendar/<token>/lilith.ics`, token from `secrets.token_urlsafe(32)`, stored inside `calendar_db`), shall respond 404 to any unknown path or wrong token without disclosing valid paths, and shall respond 405 to any non-GET method.
- **FR-CAL-014:** The feed server shall bind to loopback by default; where the user enables LAN serving, it shall bind to the local network interface only and shall never be exposed beyond the local network by Lilith.
- **FR-CAL-015:** When an event is updated or cancelled, the feed shall publish the event's current `SEQUENCE` and `STATUS` (including `STATUS:CANCELLED`) so subscribing clients observe updates and cancellations.
- **FR-CAL-016:** When the user regenerates the feed token, the system shall invalidate the previous token path immediately.

### Echo-loop handling (mandatory)

- **FR-CAL-017:** When a §19 calendar sync completes, the L1 job shall compare each incoming synced event's iCalendar UID against `lilith_events.ical_uid` and set `echo_of_lilith_event_id` on every match.
- **FR-CAL-018:** While a `synced_events` row carries `echo_of_lilith_event_id`, the L1 and L2 jobs shall exclude it from agenda merging and conflict detection, so each event appears exactly once and never conflicts with itself.

### Conflict flagging & merge-at-view

- **FR-CAL-019:** When a non-echo synced event genuinely overlaps in time with an active (non-cancelled) Lilith event, the L1 job shall flag the pair for user review; the system shall never auto-resolve, move, or cancel either event.
- **FR-CAL-020:** The system shall merge the two stores only at view/summary time (L2 period agenda summaries and the calendar screen), never at the storage layer.
- **FR-CAL-021:** The L2 job shall produce period agenda summaries by template (non-LLM, per §17's untrusted-domain rule); CWM shall read L2 summaries only.
- **FR-CAL-022:** Where an event in either store carries location data, the §19 address-context preprocessing (raw address → relative plain-text context) shall be applied before CWM ingestion.

### Telemetry

- **FR-CAL-023:** The system shall emit `sync.calendar.echo_detected` (lilith_event_id, google_event_id) on each echo tag, `calendar.conflict.flagged` (lilith_event_id, synced_event_id, overlap_minutes) on each flag, and `calendar.feed.served` (event_count, response_bytes) on each feed response — payloads per §16 hygiene (operational facts and non-secret ids only, never event content). Existing events are unchanged: `sync.calendar.*` (§19), `tool.call.start`/`tool.call.complete` (§15).

## Non-Functional Requirements

### Performance
- Feed response: serialize and respond within 2 s for calendars of up to 5,000 `lilith_events` rows.
- L1 echo detection: completes within the §17 enhancement-pipeline priority rules (priority 0, before L2); idempotent re-run safe.
- `agenda` tool: completes within the §14 artifact lane budget (10 s) for a 90-day window.

### Security
- All event PII lives inside SQLCipher-encrypted `calendar_db` per §03; no plaintext event storage anywhere.
- Google scope remains `calendar.readonly` only (§19); no write scope, ever, in v6 v1.
- Write tools are scoped to `lilith_events`; cancel-never-delete preserves subscriber-visible history.
- The feed token is **capability-style security on the local network, not authentication**: anyone on the LAN who learns the URL can read Lilith's calendar. This limitation is stated honestly in user-facing copy (same honesty rule as §29's boundary paragraphs); the token is never logged and is regenerable.
- Cloud LLM calls involving calendar context pass through §14 PII tokenization as usual; the feed itself never transits any cloud service.

### Reliability
- §19 sync behavior is unchanged and frozen: read-only scope, 15-minute interval, `nextSyncToken`, HTTP 410 → full resync. A full resync rebuilds the mirror; echo tags are recomputed by the next L1 run (idempotent).
- Feed GET is idempotent and side-effect-free.

## Acceptance Criteria (Given/When/Then)

### AC-CAL-001: Lilith schedules without touching the user's calendar
Given the user asks Lilith to schedule a reminder event,
When `calendar_event_create` completes,
Then a `lilith_events` row exists with a fresh UID, `sequence` 0, and confirmed status, the ICS feed includes the event, no Google API write call was issued, and the user's Google Calendar is unchanged.

### AC-CAL-002: Echo loop — each event appears exactly once (keystone)
Given the user has subscribed to Lilith's feed in their own calendar and Lilith's events sync back through §19 as Google events,
When the next sync imports an echoed copy whose iCal UID matches a `lilith_events` row,
Then the L1 job sets `echo_of_lilith_event_id` on the synced copy, emits `sync.calendar.echo_detected`, the agenda shows the event exactly once, and no conflict is flagged between the event and its echo.

### AC-CAL-003: Write tools refuse mirrored events
Given a mirrored Google event id,
When any calendar write tool is invoked with it,
Then the tool refuses with an explicit message, no row in either store is modified, and `tool.call.complete` records the refusal.

### AC-CAL-004: Cancel, never delete
Given an active Lilith event with `sequence` N,
When `calendar_event_cancel` is invoked,
Then the row remains in `lilith_events` with `status = 'cancelled'` and `sequence` N+1, and the feed publishes `STATUS:CANCELLED` with the incremented `SEQUENCE`.

### AC-CAL-005: Genuine conflicts are flagged, never auto-resolved
Given a genuine (non-echo) user event overlapping an active Lilith event,
When the L1 job runs after sync,
Then the pair is flagged for user review, `calendar.conflict.flagged` is emitted, and neither event is modified, moved, or cancelled.

### AC-CAL-006: Feed is Lilith-events-only and read-only
Given the feed is enabled and both stores contain events,
When a client fetches the token path,
Then the ICS payload contains only `lilith_events` VEVENTs (each with UID, SEQUENCE, STATUS), a wrong token returns 404, and a POST/PUT/DELETE returns 405.

### AC-CAL-007: LAN honesty — Google Calendar cannot subscribe in v1
Given the user attempts to add the feed URL to Google Calendar's "from URL" subscription,
When Google's servers attempt to poll the LAN-only feed,
Then the fetch fails (unreachable from outside the local network), and Lilith's user-facing copy states this limitation plainly rather than claiming Google subscription support; device-polling clients on the same network (e.g., Apple Calendar) can subscribe.

### AC-CAL-008: No Google write surface exists
Given the complete v6 v1 tool registry and OAuth configuration,
When they are audited,
Then no Google Calendar write scope is requested, no write-back method is registered, and no tool definition exposes a Google Calendar mutation.

## Error Handling

| Error condition | Behavior | User-visible outcome |
|---|---|---|
| Write tool given a mirrored Google event id | Refuse; modify nothing | "That event is on your own calendar — I don't change your calendar. I can create a matching event on mine." (normative content, not final copy) |
| Write tool given an unknown event id | Refuse; modify nothing | Tool `failure` narrative (§15) |
| Cancel of an already-cancelled event | Idempotent success; no change, no sequence bump | Confirmation that the event is already cancelled |
| Feed request with wrong/expired token | HTTP 404, no path disclosure | Client shows subscription error |
| Feed request with non-GET method | HTTP 405 | — |
| ICS serialization failure | HTTP 500; `calendar.feed.served` not emitted; error logged per §16 | Client retains last successful fetch |
| Sync HTTP 410 (expired sync token) | Full resync per §19 (unchanged); mirror rebuilt; L1 recomputes echo tags idempotently | None (background) |
| L1 echo job interrupted | Idempotent re-run on next §17 trigger; no partial-tag corruption | None (background) |
| `agenda` over empty/never-synced domain | §14 absence disclosure (`status="missing"`), never fabricated | Lilith names the absence and offers to sync |

## Implementation TODO

### Database (calendar_db)
- [ ] Migration: `synced_events` mirror table (Google mapping + `provenance`, `echo_of_lilith_event_id`).
- [ ] Migration: `lilith_events` table (iCal UID/SEQUENCE/STATUS semantics, cancel-never-delete constraint path).
- [ ] Migration: `calendar_l1` conflict-flag table + `calendar_l2_summaries`.
- [ ] Feed token storage row inside `calendar_db` (generated `secrets.token_urlsafe(32)`).

### Sync & enhancement
- [ ] §19 event-field mapping into `synced_events` (id, iCal UID, times, status, etag, synced_at) — sync machinery itself unchanged.
- [ ] L1 job: echo detection (UID match → `echo_of_lilith_event_id`) + genuine-overlap conflict flagging; emit `sync.calendar.echo_detected`, `calendar.conflict.flagged`.
- [ ] L2 job: template period agenda summaries (merge non-echo mirror + active Lilith events at summary time); §19 address-context preprocessing before CWM ingestion.

### Tools (YAML contracts per §15, with acknowledge/bridge/handoff/failure narratives)
- [ ] `agenda`, `event_lookup` — `artifact_only` reads returning L2 text.
- [ ] `calendar_event_create`, `calendar_event_update`, `calendar_event_cancel` — scoped to `lilith_events`, mirrored-id refusal, sequence increments.

### ICS feed
- [ ] Local HTTP server (loopback default, LAN opt-in), GET-only, token path, RFC 5545 serialization of `lilith_events` only.
- [ ] Token regeneration setting; honest capability-not-authentication copy; emit `calendar.feed.served`.

### UI
- [ ] `"calendar"` screen replacing `"finance"` in the §26 screen list and §28 stack/orb rules.

### Testing (§08)
- [ ] Unit: store separation (no non-sync writer of Google fields), write-tool scoping and refusal, cancel idempotency, sequence increments.
- [ ] Unit: echo detection, echo exclusion from merge/conflict, overlap flagging.
- [ ] Integration: feed serialization (Lilith-only content, 404/405 paths, cancelled-event publication).
- [ ] Integration: full echo-loop round trip (create → feed → simulated Google echo → sync → single agenda appearance, no self-conflict).

## Out of Scope (v6 v1)

- The Finance App (parked to post-v1; returns when deterministic finance infrastructure exists — see `BUILD_SEQUENCING.md` §5).
- Any Google Calendar write path, write scope, or write-back method.
- Remote/cloud publishing of the ICS feed (would let Google Calendar subscribe; deferred consistently with §29's cloud deferral).
- Additional ingest sources (ICS/CalDAV/Apple Calendar ingest) — Google Calendar is the sole ingest source in v6 v1.
- Lilith managing the user's own calendar — gated on accumulated telemetry, a future documented design session.

## Open Questions

None — all decisions in this spec were confirmed by the stakeholder in the 2026-07-27 design session recorded in the task work order.
