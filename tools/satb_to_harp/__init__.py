"""SATB → pedal-harp arranger.

Two phases:
  1. analyzer.py   — SATB beat grid → 8-voice ledger (collapse + fill)
  2. consolidator.py — 8-voice ledger → 2-voice ABC (LH/RH)

server.py wraps both behind a small Flask app for browser playback.

See docs/harprules.md for the 8-voice roster and freed-finger fill menu;
HARP_RULES.md for pedal-harp zones, span limits, and the same-letter rule.
"""
