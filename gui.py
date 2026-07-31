#!/usr/bin/env python3
"""Native desktop GUI for the realtime countdown monitor."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from monitor_core import CountdownModel, Slot, default_env_path, load_slots_from_env

try:
    from tkinter import BOTH, Canvas, END, StringVar, Tk, TclError, ttk

    TK_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - environment dependent
    BOTH = Canvas = END = StringVar = Tk = TclError = ttk = None  # type: ignore[assignment]
    TK_AVAILABLE = False


@dataclass
class Theme:
    bg: str = "#0b1117"
    panel: str = "#121a24"
    panel_alt: str = "#16202c"
    text: str = "#f3efe6"
    muted: str = "#9ea7b3"
    accent: str = "#f0a14b"
    accent_2: str = "#7fd1b9"
    danger: str = "#ff6b6b"


class MonitorGUI:
    def __init__(self, root: Tk, slots: list[Slot], interval: float, env_path: Path) -> None:
        self.root = root
        self.env_path = env_path
        self.env_mtime = 0.0
        self.theme = Theme()
        self.model = CountdownModel(slots, interval)
        self.current_state: dict[str, object] = self.model.snapshot()
        self.countdown_var = StringVar()
        self.status_var = StringVar()
        self.active_var = StringVar()
        self.next_var = StringVar()
        self.active_id_var = StringVar()
        self.next_id_var = StringVar()
        self.active_token_var = StringVar()
        self.next_token_var = StringVar()
        self.switch_var = StringVar()
        self.error_var = StringVar()
        self.filter_var = StringVar()
        self.slot_count_var = StringVar()

        self._configure_window()
        self._build_layout()
        self._set_model(slots, interval, refresh_mtime=False)
        self._tick()

    def _configure_window(self) -> None:
        self.root.title("Realtime Monitor Countdown")
        self.root.geometry("1100x720")
        self.root.minsize(940, 620)
        self.root.configure(bg=self.theme.bg)

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=self.theme.bg)
        style.configure("Panel.TFrame", background=self.theme.panel, relief="flat")
        style.configure(
            "TLabel",
            background=self.theme.bg,
            foreground=self.theme.text,
            font=("Helvetica", 11),
        )
        style.configure(
            "Title.TLabel",
            background=self.theme.bg,
            foreground=self.theme.text,
            font=("Georgia", 28, "bold"),
        )
        style.configure(
            "Mono.TLabel",
            background=self.theme.panel,
            foreground=self.theme.text,
            font=("Courier New", 18, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background=self.theme.panel,
            foreground=self.theme.muted,
            font=("Helvetica", 10),
        )
        style.configure(
            "Accent.TLabel",
            background=self.theme.panel,
            foreground=self.theme.accent,
            font=("Courier New", 34, "bold"),
        )
        style.configure(
            "Error.TLabel",
            background=self.theme.panel,
            foreground=self.theme.danger,
            font=("Helvetica", 10, "bold"),
        )
        style.configure(
            "TProgressbar",
            troughcolor=self.theme.panel_alt,
            background=self.theme.accent,
            bordercolor=self.theme.panel_alt,
            lightcolor=self.theme.accent_2,
            darkcolor=self.theme.accent,
            thickness=18,
        )
        style.configure(
            "Treeview",
            background=self.theme.panel,
            fieldbackground=self.theme.panel,
            foreground=self.theme.text,
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=self.theme.panel_alt,
            foreground=self.theme.text,
            font=("Helvetica", 10, "bold"),
        )

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill=BOTH, expand=True)

        header = ttk.Frame(container, style="Panel.TFrame", padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="Realtime Monitor Countdown", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Native GUI dashboard for slot rotation, live countdown, and env reload.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(6, 0))
        controls = ttk.Frame(header, style="Panel.TFrame")
        controls.pack(anchor="e", pady=(12, 0))
        ttk.Label(controls, text="● LIVE", style="Accent.TLabel").pack(side="left", padx=(0, 18))
        ttk.Button(controls, text="Refresh now", command=self.refresh_from_disk).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="Reset timer", command=self.reset_timer).pack(side="left")

        body = ttk.Frame(container)
        body.pack(fill=BOTH, expand=True, pady=(18, 0))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body, style="Panel.TFrame", padding=22)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right = ttk.Frame(body, style="Panel.TFrame", padding=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        hero = ttk.Frame(left, style="Panel.TFrame")
        hero.pack(fill="x")
        hero.columnconfigure(0, weight=1)
        hero.columnconfigure(1, weight=1)

        self.canvas = Canvas(
            hero,
            width=240,
            height=240,
            background=self.theme.panel,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=0, column=0, rowspan=3, padx=(0, 18), pady=(0, 4), sticky="w")
        self._draw_ring(0.0, "running")

        text_panel = ttk.Frame(hero, style="Panel.TFrame")
        text_panel.grid(row=0, column=1, sticky="nsew")

        ttk.Label(text_panel, textvariable=self.countdown_var, style="Accent.TLabel").pack(anchor="w")
        ttk.Label(text_panel, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w", pady=(4, 8))
        ttk.Label(text_panel, textvariable=self.switch_var, style="Muted.TLabel").pack(anchor="w")
        ttk.Label(text_panel, textvariable=self.error_var, style="Error.TLabel", wraplength=380, justify="left").pack(
            anchor="w",
            pady=(12, 0),
        )

        self.progress = ttk.Progressbar(left, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(16, 14))

        info_grid = ttk.Frame(left, style="Panel.TFrame")
        info_grid.pack(fill="x", pady=(8, 0))
        info_grid.columnconfigure(0, weight=1)
        info_grid.columnconfigure(1, weight=1)

        self._metric(info_grid, 0, 0, "Active slot", self.active_var)
        self._metric(info_grid, 0, 1, "Next used", self.next_var)
        self._metric(info_grid, 1, 0, "Active identity", self.active_id_var)
        self._metric(info_grid, 1, 1, "Next identity", self.next_id_var)
        self._metric(info_grid, 2, 0, "Active token", self.active_token_var)
        self._metric(info_grid, 2, 1, "Next token", self.next_token_var)

        slot_heading = ttk.Frame(right, style="Panel.TFrame")
        slot_heading.pack(fill="x")
        ttk.Label(slot_heading, text="Configured slots", style="Mono.TLabel").pack(side="left")
        ttk.Label(slot_heading, textvariable=self.slot_count_var, style="Muted.TLabel").pack(side="right")
        filter_row = ttk.Frame(right, style="Panel.TFrame")
        filter_row.pack(fill="x", pady=(12, 0))
        filter_entry = ttk.Entry(filter_row, textvariable=self.filter_var)
        filter_entry.pack(side="left", fill="x", expand=True)
        filter_entry.insert(0, "Filter identities…")
        filter_entry.bind("<FocusIn>", lambda _event: self._clear_filter_placeholder(filter_entry))
        filter_entry.bind("<KeyRelease>", lambda _event: self._refresh_state())
        ttk.Button(filter_row, text="Clear", command=lambda: self._clear_filter(filter_entry)).pack(side="left", padx=(8, 0))
        self.tree = ttk.Treeview(
            right,
            columns=("slot", "identity", "key", "fingerprint"),
            show="headings",
            height=16,
            selectmode="browse",
        )
        self.tree.heading("slot", text="Slot")
        self.tree.heading("identity", text="Identity")
        self.tree.heading("key", text="Key")
        self.tree.heading("fingerprint", text="Fingerprint")
        self.tree.column("slot", width=60, anchor="center", stretch=False)
        self.tree.column("identity", width=220, anchor="w")
        self.tree.column("key", width=180, anchor="w")
        self.tree.column("fingerprint", width=130, anchor="w")
        self.tree.pack(fill=BOTH, expand=True, pady=(10, 0))

        self.footer = ttk.Label(
            right,
            text="Ctrl+C is not needed here. Close the window to stop the monitor.",
            style="Muted.TLabel",
            wraplength=360,
            justify="left",
        )
        self.footer.pack(anchor="w", pady=(12, 0))

    def _metric(self, parent: ttk.Frame, row: int, col: int, label: str, variable: StringVar) -> None:
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        ttk.Label(frame, text=label, style="Muted.TLabel").pack(anchor="w")
        ttk.Label(frame, textvariable=variable, style="TLabel").pack(anchor="w", pady=(5, 0))

    def _clear_filter_placeholder(self, entry: ttk.Entry) -> None:
        if self.filter_var.get() == "Filter identities…":
            self.filter_var.set("")

    def _clear_filter(self, entry: ttk.Entry) -> None:
        self.filter_var.set("")
        entry.focus_set()
        self._refresh_state()

    def _set_model(self, slots: list[Slot], interval: float, refresh_mtime: bool = True) -> None:
        self.model = CountdownModel(slots, interval)
        self.current_state = self.model.snapshot()
        if refresh_mtime:
            try:
                self.env_mtime = self.env_path.stat().st_mtime
            except FileNotFoundError:
                self.env_mtime = 0.0
        self.error_var.set("")
        self._refresh_state()

    def _draw_ring(self, progress: float, status: str) -> None:
        self.canvas.delete("all")
        color = self.theme.accent_2
        if status == "warning":
            color = self.theme.accent
        elif status == "switching":
            color = self.theme.danger

        self.canvas.create_oval(18, 18, 222, 222, outline="#243140", width=18)
        extent = max(0.0, min(360.0, progress * 360.0))
        self.canvas.create_arc(
            18,
            18,
            222,
            222,
            start=90,
            extent=-extent,
            style="arc",
            outline=color,
            width=18,
        )
        self.canvas.create_text(
            120,
            102,
            text=self.countdown_var.get() or "--:--",
            fill=self.theme.text,
            font=("Courier New", 28, "bold"),
        )
        self.canvas.create_text(
            120,
            142,
            text=self.status_var.get().replace("Status: ", "").upper() or "LOADING",
            fill=self.theme.muted,
            font=("Helvetica", 9, "bold"),
        )

    def _refresh_state(self) -> None:
        state = self.current_state
        self.countdown_var.set(str(state["remaining_text"]))
        self.status_var.set(f"Status: {state['status']}")
        self.active_var.set(f"#{int(state['active_slot']):02d} of {int(state['slot_count']):02d}")
        self.next_var.set(f"#{int(state['next_slot']):02d}")
        self.active_id_var.set(str(state["active_google_id_masked"]))
        self.next_id_var.set(str(state["next_google_id_masked"]))
        self.active_token_var.set(str(state["active_api_key_masked"]))
        self.next_token_var.set(str(state["next_api_key_masked"]))
        self.switch_var.set(f"Next switch at {state['next_switch_label']}")
        query = self.filter_var.get().strip().lower()
        if query == "filter identities…":
            query = ""
        visible_slots = [
            slot for slot in state["slots"]
            if not query or query in str(slot["google_id_masked"]).lower() or query in str(slot["api_key_name"]).lower()
        ]
        self.slot_count_var.set(f"{len(visible_slots)}/{int(state['slot_count'])} visible")
        self.progress["value"] = float(state["progress"]) * 100.0
        self._draw_ring(float(state["progress"]), str(state["status"]))

        for row in self.tree.get_children():
            self.tree.delete(row)

        active_slot = int(state["active_slot"])
        for slot in visible_slots:
            slot_num = int(slot["slot"])
            marker = "active" if slot_num == active_slot else "queued"
            self.tree.insert(
                "",
                END,
                values=(
                    f"{slot_num:02d} ({marker})",
                    str(slot["google_id_masked"]),
                    f"{slot['api_key_name']} · {slot['api_key_masked']} ({slot['api_key_length']})",
                    str(slot["api_key_fingerprint"]),
                ),
            )

    def refresh_from_disk(self) -> None:
        try:
            slots, mtime = load_slots_from_env(self.env_path)
        except Exception as exc:  # noqa: BLE001
            self.error_var.set(f"Config error: {exc}")
            return

        self.env_mtime = mtime
        self._set_model(slots, self.model.interval, refresh_mtime=False)

    def reset_timer(self) -> None:
        self.model = CountdownModel(self.model.slots, self.model.interval)
        self._refresh_state()

    def _tick(self) -> None:
        try:
            current_mtime = self.env_path.stat().st_mtime
        except FileNotFoundError:
            current_mtime = 0.0

        if current_mtime and current_mtime != self.env_mtime:
            self.refresh_from_disk()

        try:
            self.current_state = self.model.snapshot()
            self.error_var.set("")
        except Exception as exc:  # noqa: BLE001
            self.error_var.set(f"Monitor error: {exc}")
            self.status_var.set("Status: error")
            self.countdown_var.set("--:--")
            self.switch_var.set("Next switch at --:--:--")
            self._draw_ring(0.0, "switching")
            self.root.after(500, self._tick)
            return

        self._refresh_state()
        self.root.after(500, self._tick)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the native GUI countdown monitor.")
    parser.add_argument(
        "--env",
        default=str(default_env_path()),
        help="Path to the env file. Defaults to the app directory .env when frozen.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=float(os.getenv("MONITOR_INTERVAL_SECONDS", "60")),
        help="Seconds between slot rotations.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not TK_AVAILABLE:
        raise SystemExit("tkinter is not installed in this environment; use app.py for the web dashboard.")
    env_path = Path(args.env)
    slots, _ = load_slots_from_env(env_path)

    try:
        root = Tk()
    except TclError as exc:
        raise SystemExit(f"Unable to open GUI window: {exc}") from exc
    MonitorGUI(root, slots, args.interval, env_path)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
