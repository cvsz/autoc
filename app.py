#!/usr/bin/env python3
"""Realtime monitor dashboard for the GOOGLE_ID / API key slot set."""

from __future__ import annotations

import argparse
import json
import os
import sys
import socket
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse

from monitor_core import ReloadingCountdownModel, default_env_path


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Realtime Monitor Countdown</title>
  <style>
    :root {
      --bg0: #0a0f14;
      --bg1: #111922;
      --panel: rgba(14, 19, 26, 0.86);
      --panel-border: rgba(255, 255, 255, 0.08);
      --text: #f3efe6;
      --muted: #a8b0ba;
      --accent: #f0a14b;
      --accent-2: #7fd1b9;
      --danger: #ff6b6b;
      --shadow: 0 20px 80px rgba(0, 0, 0, 0.4);
      --radius: 28px;
      --mono: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      --serif: Georgia, "Times New Roman", serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(240, 161, 75, 0.2), transparent 36%),
        radial-gradient(circle at right 20%, rgba(127, 209, 185, 0.16), transparent 30%),
        linear-gradient(135deg, var(--bg0), var(--bg1));
      font-family: var(--serif);
    }
    .shell {
      min-height: 100vh;
      padding: 24px;
      display: grid;
      place-items: center;
    }
    .card {
      width: min(1120px, 100%);
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: calc(var(--radius) + 4px);
      box-shadow: var(--shadow);
      overflow: hidden;
      backdrop-filter: blur(16px);
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 22px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-family: var(--mono);
      color: var(--muted);
      letter-spacing: 0.02em;
      font-size: 0.88rem;
    }
    body[data-theme="light"] {
      --bg0: #eef4f3;
      --bg1: #dbe8e8;
      --panel: rgba(255, 255, 255, 0.86);
      --panel-border: rgba(15, 35, 40, 0.12);
      --text: #17252a;
      --muted: #5b6c72;
      --shadow: 0 20px 70px rgba(28, 62, 68, 0.18);
    }
    .brand {
      display: inline-flex;
      align-items: center;
      gap: 11px;
      color: var(--text);
      font-family: var(--mono);
    }
    .brand-mark {
      display: grid;
      place-items: center;
      width: 34px;
      height: 34px;
      border-radius: 12px;
      color: #10181b;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      font-weight: 900;
    }
    .brand strong { display: block; font-size: 0.98rem; }
    .brand small { display: block; color: var(--muted); font-size: 0.68rem; margin-top: 2px; }
    .header-actions { display: flex; align-items: center; gap: 9px; }
    .icon-button {
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      padding: 8px 10px;
      color: var(--text);
      background: rgba(255, 255, 255, 0.06);
      cursor: pointer;
      font: 700 0.76rem var(--mono);
      transition: transform 160ms ease, background 160ms ease, border-color 160ms ease;
    }
    .icon-button:hover, .icon-button:focus-visible { transform: translateY(-1px); border-color: var(--accent); background: rgba(240, 161, 75, 0.14); }
    .icon-button:focus-visible, .filter-input:focus-visible { outline: 3px solid rgba(127, 209, 185, 0.45); outline-offset: 2px; }
    .connection-badge { min-width: 124px; justify-content: center; }
    .connection-badge.offline .dot { background: var(--danger); box-shadow: 0 0 0 6px rgba(255, 107, 107, 0.08); }
    .connection-badge.syncing .dot { background: var(--accent); box-shadow: 0 0 0 6px rgba(240, 161, 75, 0.08); }
    .hero-copy { display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; }
    .eyebrow { margin: 0 0 10px; color: var(--accent-2); font: 700 0.74rem var(--mono); letter-spacing: 0.14em; text-transform: uppercase; }
    .hero-copy p { max-width: 520px; margin: 0; color: var(--muted); font: 0.98rem/1.55 var(--mono); }
    .hero-badge { flex: 0 0 auto; padding: 9px 12px; border: 1px solid rgba(127, 209, 185, 0.25); border-radius: 14px; color: var(--accent-2); background: rgba(127, 209, 185, 0.08); font: 700 0.76rem var(--mono); }
    .countdown-caption { margin: 26px 0 0; color: var(--muted); font: 700 0.76rem var(--mono); letter-spacing: 0.13em; text-transform: uppercase; }
    .live-meta { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 12px; color: var(--muted); font: 0.75rem var(--mono); }
    .live-meta span { display: inline-flex; align-items: center; gap: 6px; }
    .live-meta strong { color: var(--text); font-weight: 700; }
    .panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
    .panel-heading h2 { margin: 0; }
    .slot-count { color: var(--muted); font: 700 0.72rem var(--mono); }
    .slot-toolbar { display: flex; gap: 8px; margin-bottom: 12px; }
    .filter-input { width: 100%; border: 1px solid var(--panel-border); border-radius: 11px; padding: 10px 11px; color: var(--text); background: rgba(255, 255, 255, 0.06); font: 0.78rem var(--mono); }
    .filter-input::placeholder { color: var(--muted); }
    .slot-status { color: var(--accent-2); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }
    .empty-state { padding: 18px 8px; color: var(--muted); text-align: center; font: 0.8rem/1.45 var(--mono); }
    .hint { margin: 10px 0 0; color: var(--muted); font: 0.72rem/1.45 var(--mono); }
    .hint kbd { padding: 2px 5px; border: 1px solid var(--panel-border); border-radius: 5px; color: var(--text); background: rgba(255,255,255,0.08); }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; } }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.05);
      color: var(--text);
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--accent-2);
      box-shadow: 0 0 0 6px rgba(127, 209, 185, 0.08);
    }
    .status-warning .dot { background: var(--accent); box-shadow: 0 0 0 6px rgba(240, 161, 75, 0.08); }
    .status-switching .dot { background: var(--danger); box-shadow: 0 0 0 6px rgba(255, 107, 107, 0.08); }
    .content {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 0;
    }
    .hero {
      padding: 32px 30px 30px;
      border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    h1 {
      margin: 0 0 14px;
      font-size: clamp(2rem, 4vw, 4rem);
      line-height: 0.96;
      font-weight: 700;
      letter-spacing: -0.04em;
    }
    .countdown {
      margin: 18px 0 10px;
      font-family: var(--mono);
      font-size: clamp(3.3rem, 10vw, 7rem);
      font-weight: 800;
      letter-spacing: -0.08em;
      color: var(--accent);
    }
    .progress-track {
      width: 100%;
      height: 14px;
      border-radius: 999px;
      overflow: hidden;
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .progress-fill {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
      border-radius: inherit;
      transition: width 240ms linear;
    }
    .meta {
      margin-top: 22px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .tile {
      padding: 16px 18px;
      border-radius: 22px;
      background: rgba(255, 255, 255, 0.045);
      border: 1px solid rgba(255, 255, 255, 0.07);
    }
    .label {
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      margin-bottom: 8px;
    }
    .value {
      font-family: var(--mono);
      font-size: 1.05rem;
      word-break: break-word;
    }
    .side {
      padding: 26px 22px 30px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }
    .panel {
      padding: 18px;
      border-radius: 22px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.07);
    }
    .panel h2 {
      margin: 0 0 14px;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .slot-list {
      display: grid;
      gap: 10px;
    }
    .slot {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.035);
      border: 1px solid transparent;
      font-family: var(--mono);
    }
    .slot.active {
      border-color: rgba(240, 161, 75, 0.42);
      background: rgba(240, 161, 75, 0.08);
    }
    .slot .small {
      color: var(--muted);
      font-size: 0.82rem;
      margin-top: 4px;
    }
    .slot .key-detail { margin-top: 5px; color: var(--text); font-size: 0.72rem; }
    .slot .key-fingerprint { margin-top: 3px; color: var(--muted); font-size: 0.68rem; letter-spacing: 0.04em; }
    .slot strong { font-size: 0.95rem; }
    .slot .num {
      color: var(--accent-2);
      font-weight: 700;
    }
    .footer-note {
      margin-top: auto;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.82rem;
      line-height: 1.5;
    }
    @media (max-width: 900px) {
      .content { grid-template-columns: 1fr; }
      .hero { border-right: 0; border-bottom: 1px solid rgba(255, 255, 255, 0.06); }
    }
    @media (max-width: 640px) {
      .shell { padding: 10px; }
      .card { border-radius: 22px; }
      .topbar { flex-direction: column; }
      .header-actions { justify-content: space-between; flex-wrap: wrap; }
      .hero-copy { flex-direction: column; }
      .meta { grid-template-columns: 1fr; }
      .hero, .side { padding: 18px; }
      .countdown { letter-spacing: -0.05em; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <main class="card" id="card">
      <div class="topbar">
        <div class="brand"><span class="brand-mark">G</span><span><strong>ggtmoni</strong><small>rotation control room</small></span></div>
        <div class="header-actions">
          <div class="badge connection-badge syncing" id="status-badge" aria-live="polite"><span class="dot"></span><span id="status-text">connecting</span></div>
          <button class="icon-button" id="refresh-button" type="button" title="Refresh state (R)">↻ Refresh</button>
          <button class="icon-button" id="theme-toggle" type="button" title="Toggle theme">☼ Theme</button>
        </div>
      </div>
      <div class="content">
        <section class="hero">
          <div class="hero-copy">
            <div>
              <p class="eyebrow">Live rotation status</p>
              <h1>Active now, next queued, countdown live.</h1>
              <p>Track the current identity slot, see what is next, and keep the handoff visible at a glance.</p>
            </div>
            <div class="hero-badge" id="model-status">RUNNING</div>
          </div>
          <p class="countdown-caption">Next switch in</p>
          <div class="countdown" id="countdown">--:--</div>
          <div class="progress-track"><div class="progress-fill" id="progress-fill"></div></div>
          <div class="live-meta">
            <span>Local <strong id="clock-label">--:--:--</strong></span>
            <span>Last sync <strong id="last-sync">waiting</strong></span>
            <span>Interval <strong id="interval-label">--</strong></span>
            <span>Usage <strong id="usage-label">local only</strong></span>
          </div>
          <div class="meta">
            <div class="tile">
              <div class="label">Active slot</div>
              <div class="value" id="active-slot">--</div>
            </div>
            <div class="tile">
              <div class="label">Next used</div>
              <div class="value" id="next-slot">--</div>
            </div>
            <div class="tile">
              <div class="label">Active identity</div>
              <div class="value" id="active-id">--</div>
            </div>
            <div class="tile">
              <div class="label">Next identity</div>
              <div class="value" id="next-id">--</div>
            </div>
            <div class="tile">
              <div class="label">Active token</div>
              <div class="value" id="active-token">--</div>
            </div>
            <div class="tile">
              <div class="label">Next token</div>
              <div class="value" id="next-token">--</div>
            </div>
            <div class="tile">
              <div class="label">Next switch</div>
              <div class="value" id="next-switch">--</div>
            </div>
          </div>
        </section>
        <aside class="side">
          <section class="panel">
            <div class="panel-heading"><h2>Configured slots</h2><span class="slot-count" id="slot-count">--</span></div>
            <div class="slot-toolbar"><input class="filter-input" id="slot-filter" type="search" placeholder="Filter identities…" aria-label="Filter configured identities" /></div>
            <div class="slot-list" id="slot-list"></div>
            <div class="empty-state" id="empty-state" hidden>No matching slots.</div>
          </section>
          <section class="panel footer-note">
            Reads the local <code>.env</code> file, preserves slot order, and never exposes raw API keys. Live updates use SSE.
            <p class="hint">Key details are masked and fingerprinted. Usage means local rotation state only; provider quota usage is not collected.</p>
            <p class="hint"><kbd>R</kbd> refreshes state · <kbd>T</kbd> toggles theme</p>
          </section>
        </aside>
      </div>
    </main>
  </div>
  <script id="bootstrap" type="application/json">__BOOTSTRAP__</script>
  <script>
    const bootstrap = JSON.parse(document.getElementById('bootstrap').textContent);
    const $ = (id) => document.getElementById(id);
    const fmt = (ms) => {
      const total = Math.ceil(Math.max(0, ms) / 1000);
      return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
    };
    const statusBadge = $('status-badge');
    const statusText = $('status-text');
    const countdownEl = $('countdown');
    const progressFill = $('progress-fill');
    const filterInput = $('slot-filter');
    let state = bootstrap;
    let connectionState = 'syncing';
    let lastSyncAt = null;

    function renderSlots() {
      const list = $('slot-list');
      const query = filterInput.value.trim().toLowerCase();
      list.innerHTML = '';
      const visible = state.slots.filter((slot) => `${slot.google_id_masked} ${slot.api_key_name} ${slot.api_key_fingerprint} ${slot.rotation_state}`.toLowerCase().includes(query));
      $('slot-count').textContent = `${visible.length}/${state.slot_count} visible`;
      $('empty-state').hidden = visible.length !== 0;
      for (const slot of visible) {
        const row = document.createElement('div');
        row.className = 'slot' + (slot.slot === state.active_slot ? ' active' : '');
        const details = document.createElement('div');
        const identity = document.createElement('strong');
        const number = document.createElement('span');
        number.className = 'num';
        number.textContent = `#${String(slot.slot).padStart(2, '0')}`;
        identity.append(number, ` ${slot.google_id_masked}`);
        const keyName = document.createElement('div');
        keyName.className = 'small';
        keyName.textContent = slot.api_key_name;
        const keyDetail = document.createElement('div');
        keyDetail.className = 'key-detail';
        keyDetail.textContent = `Key ${slot.api_key_masked} · ${slot.api_key_length} chars`;
        const fingerprint = document.createElement('div');
        fingerprint.className = 'key-fingerprint';
        fingerprint.textContent = `Fingerprint ${slot.api_key_fingerprint}`;
        details.append(identity, keyName, keyDetail, fingerprint);
        const status = document.createElement('div');
        status.className = 'slot-status';
        status.textContent = slot.rotation_state;
        row.append(details, status);
        list.appendChild(row);
      }
    }

    function renderStatic() {
      $('active-slot').textContent = `#${String(state.active_slot).padStart(2, '0')} of ${String(state.slot_count).padStart(2, '0')}`;
      $('next-slot').textContent = `#${String(state.next_slot).padStart(2, '0')}`;
      $('active-id').textContent = state.active_google_id_masked;
      $('next-id').textContent = state.next_google_id_masked;
      $('active-token').textContent = state.active_api_key_masked;
      $('next-token').textContent = state.next_api_key_masked;
      $('next-switch').textContent = state.next_switch_label;
      $('interval-label').textContent = `${state.interval_seconds}s`;
      $('usage-label').textContent = state.usage_mode === 'local-rotation-only' ? 'local only' : state.usage_mode;
      $('model-status').textContent = state.status.toUpperCase();
      renderSlots();
    }

    function applyStatus() {
      statusBadge.classList.remove('offline', 'syncing');
      statusBadge.classList.add(connectionState);
      statusText.textContent = connectionState === 'offline' ? 'offline' : connectionState === 'syncing' ? 'connecting' : 'live';
      $('card').setAttribute('data-connection', connectionState);
    }

    function tick() {
      const now = Date.now();
      const remainingMs = Math.max(0, state.next_switch_at_ms - now);
      countdownEl.textContent = fmt(remainingMs);
      const progress = Math.max(0, Math.min(100, (1 - remainingMs / (state.interval_seconds * 1000)) * 100));
      progressFill.style.width = `${progress.toFixed(2)}%`;
      $('clock-label').textContent = new Date(now).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});
      $('last-sync').textContent = lastSyncAt ? `${Math.max(0, Math.round((now - lastSyncAt) / 1000))}s ago` : 'waiting';
      document.title = `${fmt(remainingMs)} · ggtmoni`;
      requestAnimationFrame(tick);
    }

    async function refreshState() {
      connectionState = 'syncing';
      applyStatus();
      try {
        const response = await fetch('/api/state', {cache: 'no-store'});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        update(await response.json());
      } catch (error) {
        connectionState = 'offline';
        applyStatus();
      }
    }

    function update(next) {
      state = next;
      lastSyncAt = Date.now();
      connectionState = 'live';
      renderStatic();
      applyStatus();
    }

    function toggleTheme() {
      const next = document.body.dataset.theme === 'light' ? 'dark' : 'light';
      document.body.dataset.theme = next;
      localStorage.setItem('ggtmoni-theme', next);
      $('theme-toggle').textContent = next === 'light' ? '☾ Dark' : '☼ Theme';
    }

    const savedTheme = localStorage.getItem('ggtmoni-theme');
    if (savedTheme === 'light' || savedTheme === 'dark') document.body.dataset.theme = savedTheme;
    $('theme-toggle').textContent = document.body.dataset.theme === 'light' ? '☾ Dark' : '☼ Theme';
    $('theme-toggle').addEventListener('click', toggleTheme);
    $('refresh-button').addEventListener('click', refreshState);
    filterInput.addEventListener('input', renderSlots);
    document.addEventListener('keydown', (event) => {
      if (event.target.matches('input, textarea')) return;
      if (event.key.toLowerCase() === 'r') refreshState();
      if (event.key.toLowerCase() === 't') toggleTheme();
    });

    renderStatic();
    applyStatus();
    tick();

    const source = new EventSource('/events');
    source.onopen = () => { connectionState = 'live'; applyStatus(); };
    source.onmessage = (event) => {
      try { update(JSON.parse(event.data)); }
      catch (_) { connectionState = 'offline'; applyStatus(); }
    };
    source.onerror = () => { connectionState = 'offline'; applyStatus(); };
  </script>
</body>
</html>
"""


class MonitorServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, model: ReloadingCountdownModel):
        super().__init__(server_address, RequestHandlerClass)
        self.model = model


class Handler(BaseHTTPRequestHandler):
    server_version = "RealtimeMonitor/1.0"

    def _send(self, status: HTTPStatus, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: Dict[str, object]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self._send(HTTPStatus.OK, "application/json; charset=utf-8", body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            snapshot = self.server.model.snapshot()
            html = HTML_TEMPLATE.replace("__BOOTSTRAP__", json.dumps(snapshot, separators=(",", ":")))
            self._send(HTTPStatus.OK, "text/html; charset=utf-8", html.encode("utf-8"))
            return

        if parsed.path == "/api/state":
            self._send_json(self.server.model.snapshot())
            return

        if parsed.path == "/healthz":
            self._send_json({"status": "ok", "slot_count": len(self.server.model.slots)})
            return

        if parsed.path == "/events":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            try:
                while True:
                    payload = json.dumps(self.server.model.snapshot(), separators=(",", ":"))
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    time.sleep(1.0)
            except (BrokenPipeError, ConnectionResetError):
                return
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return


def best_effort_lan_ip() -> Optional[str]:
    """Return a routable local address when the dashboard binds all interfaces."""
    candidates = (
        ("8.8.8.8", 80),
        ("1.1.1.1", 80),
    )
    for target_host, target_port in candidates:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((target_host, target_port))
                ip = sock.getsockname()[0]
                if ip and ip != "0.0.0.0":
                    return ip
        except OSError:
            continue
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the realtime monitor dashboard.")
    parser.add_argument(
        "--env",
        default=str(default_env_path()),
        help="Path to the env file. Defaults to the app directory .env when frozen.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=float(os.getenv("MONITOR_INTERVAL_SECONDS", "60")),
        help="Seconds between slot rotations. Defaults to MONITOR_INTERVAL_SECONDS or 60.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="Bind host. Defaults to 0.0.0.0 or HOST.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Bind port. Defaults to PORT or 8000.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the native desktop GUI instead of the web dashboard.",
    )
    return parser


def start_web_dashboard(host: str, port: int, model: ReloadingCountdownModel) -> MonitorServer:
    """Bind the dashboard, stepping to the next free port if needed."""
    last_error: Optional[OSError] = None
    for candidate in range(port, min(port + 50, 65536)):
        try:
            server = MonitorServer((host, candidate), Handler, model)
            if candidate != port:
                print(f"Port {port} was busy; using {candidate} instead.", file=sys.stderr)
            return server
        except OSError as exc:
            if exc.errno not in {98, 48}:
                raise
            last_error = exc
    raise OSError(f"unable to bind an open port starting at {port}") from last_error


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.gui:
        try:
            from tkinter import TclError, Tk

            from gui import MonitorGUI

            from monitor_core import load_slots_from_env

            slots, _ = load_slots_from_env(Path(args.env))
            root = Tk()
            MonitorGUI(root, slots, args.interval, Path(args.env))
            root.mainloop()
            return 0
        except ModuleNotFoundError as exc:
            print(f"GUI unavailable ({exc}); starting web dashboard instead.", file=sys.stderr)
        except TclError as exc:
            print(f"GUI unavailable ({exc}); starting web dashboard instead.", file=sys.stderr)
    model = ReloadingCountdownModel(Path(args.env), args.interval)
    server = start_web_dashboard(args.host, args.port, model)
    server.daemon_threads = True
    display_host = args.host
    if args.host in {"0.0.0.0", "::"}:
        display_host = best_effort_lan_ip() or "localhost"
    print(f"Listening on http://{display_host}:{server.server_address[1]}")
    if args.host in {"0.0.0.0", "::"}:
        print("Open it from another device using this machine's LAN IP and the same port.")
    print(f"Loaded {len(model.slots)} slots from {args.env}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
