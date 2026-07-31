# Realtime Monitor Countdown Design

Status: implemented in `monitor_core.py`, `app.py`, `gui.py`, and
`realtime_monitor.py`. This document records the original design decisions and
the remaining product questions; current usage details live in
[`docs/USAGE.md`](docs/USAGE.md).

## Source Inputs

The only concrete inputs currently present are the `.env` credentials:

- `GOOGLE_ID_01` through `GOOGLE_ID_07`
- matching Google API key variables

This suggests the monitor needs to work against a small pool of Google-backed identities, with one identity active at a time and the next one selected deterministically.

## Goal

Design a realtime monitor that shows:

1. Which Google identity is active now.
2. Which identity will be used next.
3. A live countdown until the next switch or refresh.

## Assumptions

- The monitor rotates through the configured identities in numeric order.
- One countdown governs the next transition, rather than each identity having its own timer.
- The cadence is configurable, but a default interval should exist for local development.
- Secrets from `.env` must never be rendered directly in the UI.

## Data Model

Normalize the `.env` pairs into an ordered account list:

```text
[
  { slot: 1, googleId: "...", apiKey: "..." },
  { slot: 2, googleId: "...", apiKey: "..." },
  ...
]
```

Runtime state:

```text
{
  activeSlot: 1,
  nextSlot: 2,
  nextSwitchAt: <timestamp>,
  secondsRemaining: 59
}
```

## Countdown Behavior

- On startup, select the first configured slot.
- Compute `nextSwitchAt = now + interval`.
- Update `secondsRemaining` every second on the client.
- When the countdown reaches zero:
  - advance to the next configured slot,
  - recompute the next switch timestamp,
  - broadcast the new state to all connected clients.
- After the last slot, wrap back to slot 1.

## Realtime Transport

Use one of these transports:

- WebSocket, if bidirectional control is needed later.
- Server-Sent Events, if the UI is read-only and only needs live state.

For the current goal, SSE is sufficient and simpler:

- server emits a state snapshot on connect,
- server emits a new snapshot whenever the active slot changes,
- client interpolates the per-second countdown locally.

## UI Design

The monitor screen should include:

- a large countdown number,
- the active slot and identity label,
- the next slot preview,
- a compact list of all configured slots with status badges,
- a subtle progress ring or bar tied to the countdown percentage.

Recommended visual hierarchy:

1. Countdown is the primary element.
2. Active/next identity metadata is secondary.
3. Slot list is tertiary and collapses well on mobile.

## State Transitions

1. `idle` -> no active socket or timer yet.
2. `running` -> active slot and countdown visible.
3. `warning` -> final 10 seconds of a cycle.
4. `switching` -> transition moment while the active slot updates.
5. `error` -> invalid `.env` configuration or missing account slots.

## Validation Rules

- At least one complete `GOOGLE_ID_xx` / API key pair must be present.
- Slot numbering should be contiguous or explicitly normalized.
- Missing keys should fail fast with a clear config error.
- Duplicate or malformed identities should be rejected or warned about.

## Implemented components

The implementation now has a shared config/model layer that:

- reads ordered `.env` values,
- normalizes them into `Slot` objects,
- exposes active/next slots and the next switch timestamp,
- reloads when the file mtime changes, and
- emits realtime snapshots to the web, GUI, and terminal frontends.

The web frontend uses SSE and the GUI/terminal use the same model directly.
The implementation is intentionally local and does not make Google API calls.

## Open Questions

- What interval should the countdown use by default?
- Does “next used” mean the next identity in rotation, or the next monitor refresh cycle?
- Should the active identity be chosen by strict numeric order or by availability/health?
