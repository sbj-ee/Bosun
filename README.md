# Bosun

A system tray app that chimes on the hour like a U.S. Navy ship, with two
selectable modes:

- **Ship's Bells** (default) — the traditional 1-8 bell pattern, struck in
  pairs every half hour and reset at the start of each watch (4-hour watches,
  2-hour dog watches).
- **Hourly Whistle Only** — a single bosun's-pipe whistle blast on the hour,
  no half-hour bells.

Both sounds are synthesized in memory with `numpy` — no audio files are
bundled or required.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Run

```bash
python main.py
```

This launches a tray icon. Right-click it to toggle chiming on/off, switch
between Ship's Bells and Hourly Whistle, ring a test chime, or quit.

## Tests

```bash
pytest
```
