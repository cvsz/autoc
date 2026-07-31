# Architecture

## Runtime flow

```text
.env
  -> monitor_core.parse_env_pairs()
  -> ordered Slot objects
  -> CountdownModel / ReloadingCountdownModel
  -> web dashboard, Tkinter GUI, or terminal renderer
```

`monitor_core.py` is the source of truth for parsing, masking, countdown
state, and file reload behavior. Frontends should not duplicate pairing or
rotation rules.

## Components

### `monitor_core.py`

- `Slot` stores a slot number, identity, key variable name, and key value.
- `parse_env_pairs()` preserves file order and validates complete pairs.
- `mask_email()` and `mask_secret()` provide display-safe representations.
- `CountdownModel` computes active/next slots, progress, and timestamps.
- `ReloadingCountdownModel` rebuilds the model when `.env` changes.

### `app.py`

Runs a `ThreadingHTTPServer`. The HTML is embedded in the module so the web
dashboard has no frontend build step. `/events` emits JSON snapshots over SSE;
the browser interpolates the countdown locally between snapshots. `/healthz`
provides a small process-monitoring response without exposing slot values.

### `gui.py`

Uses Tkinter/ttk and the shared model. It polls the model, refreshes when the
file changes, and displays a masked slot table.

### `realtime_monitor.py`

Renders the shared slot state as a terminal view. It supports a one-shot mode
for smoke tests and scripts.

## State semantics

The first slot is active at startup. Every interval advances to the next slot,
wrapping after the final slot. `running` becomes `warning` in the final ten
seconds and briefly reports `switching` at the transition boundary.

## Security boundaries

The process must read raw values to pair and rotate them, but renderers should
use masked fields. Snapshot inventory exposes only key masks, lengths, and
short SHA-256 fingerprints; it does not expose raw keys or raw identities. The
HTTP server has no authentication or encryption. The `.env` file and process
host are therefore the primary security boundaries. Provider usage telemetry is
explicitly outside this application's current boundary.

## Testing strategy

Tests use temporary synthetic `.env` files and patch time/filesystem behavior
where needed. Add parser tests for configuration changes and model tests for
state changes; avoid real credentials and network calls.
