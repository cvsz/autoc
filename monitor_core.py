#!/usr/bin/env python3
"""Shared monitor state, .env parsing utilities, and countdown logic."""

from __future__ import annotations

import hashlib
import time
import sys
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Slot:
    slot: int
    google_id: str
    api_key_name: str
    api_key: str


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def format_countdown(seconds: float) -> str:
    whole = max(0, int(seconds + 0.999))
    minutes, secs = divmod(whole, 60)
    return f"{minutes:02d}:{secs:02d}"


def parse_env_pairs(env_path: Path) -> List[Slot]:
    if not env_path.exists():
        raise FileNotFoundError(f"missing env file: {env_path}")

    slots: List[Slot] = []
    pending_google_id: Optional[str] = None
    pending_slot_number = 0

    with env_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key.startswith("GOOGLE_ID_"):
                pending_google_id = value
                pending_slot_number += 1
                continue

            if key.startswith("GOOGLE_API_KEY"):
                if pending_google_id is None:
                    continue
                slots.append(
                    Slot(
                        slot=pending_slot_number,
                        google_id=pending_google_id,
                        api_key_name=key,
                        api_key=value,
                    )
                )
                pending_google_id = None

    if pending_google_id is not None:
        raise ValueError("found GOOGLE_ID_* without a matching GOOGLE_API_KEY* line")

    if not slots:
        raise ValueError("no Google slots found in env file")

    return slots


def load_slots_from_env(env_path: Path) -> Tuple[List[Slot], float]:
    """Load slots and return the file mtime for watcher logic."""
    slots = parse_env_pairs(env_path)
    return slots, env_path.stat().st_mtime


def default_env_path() -> Path:
    """Return the preferred .env path for source runs and frozen executables.

    When the app is bundled into a Windows standalone executable, the config
    file should live next to the executable. During source runs, keep the
    current working directory behavior so local workflows stay simple.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name(".env")
    return Path.cwd() / ".env"


def mask_secret(value: str, visible: int = 4) -> str:
    if not value:
        return "(empty)"
    if len(value) <= visible * 2:
        return "*" * len(value)
    return f"{value[:visible]}…{value[-visible:]}"


def fingerprint_secret(value: str) -> str:
    """Return a non-reversible identifier useful for key inventory views."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12].upper()


def mask_email(value: str) -> str:
    if "@" not in value:
        return mask_secret(value)
    local, domain = value.split("@", 1)
    if not local:
        return f"…@{domain}"
    if len(local) <= 2:
        local_masked = local[0] + "…"
    else:
        local_masked = f"{local[:2]}…"
    return f"{local_masked}@{domain}"


class CountdownModel:
    def __init__(self, slots: List[Slot], interval: float) -> None:
        if interval <= 0:
            raise ValueError("interval must be greater than zero")
        if not slots:
            raise ValueError("at least one slot is required")
        self.slots = slots
        self.interval = interval
        self.started_at = time.time()

    def snapshot(self) -> Dict[str, object]:
        now = time.time()
        elapsed = max(0.0, now - self.started_at)
        cycle = int(elapsed // self.interval)
        active_index = cycle % len(self.slots)
        cycle_start = self.started_at + (cycle * self.interval)
        next_switch_at = cycle_start + self.interval
        remaining = max(0.0, next_switch_at - now)
        active = self.slots[active_index]
        next_slot = self.slots[(active_index + 1) % len(self.slots)]
        status = "warning" if remaining <= 10 else "running"
        if remaining <= 1:
            status = "switching" if remaining > 0 else "running"

        return {
            "server_now_ms": int(now * 1000),
            "started_at_ms": int(self.started_at * 1000),
            "interval_seconds": self.interval,
            "active_index": active_index,
            "active_slot": active.slot,
            "active_google_id_masked": mask_email(active.google_id),
            "active_api_key_name": active.api_key_name,
            "active_api_key_masked": mask_secret(active.api_key),
            "next_slot": next_slot.slot,
            "next_google_id_masked": mask_email(next_slot.google_id),
            "next_api_key_name": next_slot.api_key_name,
            "next_api_key_masked": mask_secret(next_slot.api_key),
            "next_switch_at_ms": int(next_switch_at * 1000),
            "seconds_remaining": remaining,
            "remaining_text": format_countdown(remaining),
            "progress": clamp(1.0 - (remaining / self.interval), 0.0, 1.0),
            "status": status,
            "slot_count": len(self.slots),
            "next_switch_label": time.strftime("%H:%M:%S", time.localtime(next_switch_at)),
            "usage_mode": "local-rotation-only",
            "usage_note": "Provider quota telemetry is not collected by autoc.",
            "slots": [
                {
                    "slot": slot.slot,
                    "google_id_masked": mask_email(slot.google_id),
                    "api_key_name": slot.api_key_name,
                    "api_key_masked": mask_secret(slot.api_key),
                    "api_key_length": len(slot.api_key),
                    "api_key_fingerprint": fingerprint_secret(slot.api_key),
                    "rotation_state": (
                        "active"
                        if slot.slot == active.slot
                        else "next"
                        if slot.slot == next_slot.slot
                        else "queued"
                    ),
                }
                for slot in self.slots
            ],
        }


class ReloadingCountdownModel:
    def __init__(self, env_path: Path, interval: float) -> None:
        self.env_path = Path(env_path)
        self.interval = interval
        self._lock = Lock()
        self._mtime = 0.0
        self._model: CountdownModel
        self._slots: List[Slot]
        self.reload(force=True)

    @property
    def slots(self) -> List[Slot]:
        return self._slots

    def reload(self, force: bool = False) -> None:
        slots, mtime = load_slots_from_env(self.env_path)
        if not force and mtime == self._mtime:
            return
        self._slots = slots
        self._model = CountdownModel(slots, self.interval)
        self._mtime = mtime

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            try:
                current_mtime = self.env_path.stat().st_mtime
            except FileNotFoundError:
                current_mtime = 0.0
            if current_mtime and current_mtime != self._mtime:
                self.reload(force=True)
            return self._model.snapshot()
