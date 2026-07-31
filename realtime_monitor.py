#!/usr/bin/env python3
"""Realtime countdown monitor for the GOOGLE_ID / API key slot set."""

from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional

from monitor_core import Slot, default_env_path, mask_email, mask_secret, parse_env_pairs


def clear_screen() -> None:
    sys.stdout.write("\033[2J\033[H")


def render_bar(remaining: float, interval: float, width: int = 28) -> str:
    if interval <= 0:
        return "[" + "#" * width + "]"
    progress = max(0.0, min(1.0, 1.0 - (remaining / interval)))
    filled = int(round(progress * width))
    filled = max(0, min(width, filled))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def format_seconds(seconds: float) -> str:
    whole = max(0, int(seconds + 0.999))
    minutes, secs = divmod(whole, 60)
    if minutes:
        return f"{minutes:02d}:{secs:02d}"
    return f"00:{secs:02d}"


def render_state(
    slots: List[Slot],
    active_index: int,
    next_switch_at: float,
    interval: float,
    now: float,
) -> None:
    remaining = max(0.0, next_switch_at - now)
    active = slots[active_index]
    next_slot = slots[(active_index + 1) % len(slots)]

    clear_screen()
    print("Realtime Monitor Countdown")
    print("=" * 29)
    print(f"Active slot : {active.slot}")
    print(f"Active ID   : {mask_email(active.google_id)}")
    print(f"Active token: {mask_secret(active.api_key)}")
    print(f"Next slot   : {next_slot.slot}")
    print(f"Next ID     : {mask_email(next_slot.google_id)}")
    print(f"Next token  : {mask_secret(next_slot.api_key)}")
    print(f"API key var : {active.api_key_name}")
    print()
    print(f"Countdown   : {format_seconds(remaining)}")
    print(f"Progress    : {render_bar(remaining, interval)}")
    print()
    print("Configured slots:")
    for index, slot in enumerate(slots):
        marker = ">" if index == active_index else " "
        print(f" {marker} {slot.slot:02d}  {mask_email(slot.google_id)}")
    print()
    print("Ctrl+C to stop.")
    sys.stdout.flush()


def run_monitor(slots: List[Slot], interval: float, once: bool = False) -> int:
    if interval <= 0:
        raise ValueError("interval must be greater than zero")

    active_index = 0
    next_switch_at = time.monotonic() + interval

    def handle_signal(signum, frame):  # noqa: ANN001,ARG001
        raise KeyboardInterrupt

    previous_handler = signal.signal(signal.SIGINT, handle_signal)
    try:
        while True:
            now = time.monotonic()
            while now >= next_switch_at:
                active_index = (active_index + 1) % len(slots)
                next_switch_at += interval
                now = time.monotonic()

            render_state(slots, active_index, next_switch_at, interval, now)

            if once:
                return 0

            sleep_for = max(0.1, min(1.0, next_switch_at - now))
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130
    finally:
        signal.signal(signal.SIGINT, previous_handler)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the realtime countdown monitor.")
    parser.add_argument(
        "--env",
        default=str(default_env_path()),
        help="Path to the env file containing GOOGLE_ID_* and GOOGLE_API_KEY* entries.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=60.0,
        help="Seconds between slot rotations. Defaults to 60.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Render a single snapshot and exit.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    env_path = Path(args.env)
    slots = parse_env_pairs(env_path)
    return run_monitor(slots, args.interval, once=args.once)


if __name__ == "__main__":
    raise SystemExit(main())
