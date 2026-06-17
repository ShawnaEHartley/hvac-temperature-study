#!/usr/bin/env python3
"""
build_hvac.py
=============
Reads Govee sensor CSVs, fetches/extends Open-Meteo outdoor weather,
and writes payload.json + hvac_dashboard.html.

Usage:
    python build_hvac.py

Outputs:
    payload.json          — clean data payload (no identifying info)
    hvac_dashboard.html   — self-contained 3-tab dashboard

Notes:
    - Bedroom sensors (Chef Brad, Pedro Pascal) are excluded entirely.
    - Heath Ledger and Eddie Redmayne data before RELOC_DATE is excluded
      (they were in bedrooms before that date).
    - Open-Meteo coordinates are used at build time only and never appear
      in any output file.
"""

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import urllib.request

# ── Config ────────────────────────────────────────────────────────────────────

DATA_DIR   = Path(__file__).parent / "sensor_data"
OUTPUT_DIR = Path(__file__).parent

START_DATE = "2026-04-01"
END_DATE   = "2026-06-17"   # inclusive — sensor data through noon today

RELOC_DATE      = "2026-05-16"   # sensor relocation: Heath/Eddie move into living room
PTAC_DATE       = "2026-05-18"   # new PTACs installed
FLOOR_UNIT_DATE = "2026-06-03"   # supplemental floor AC unit added

TZ = ZoneInfo("America/New_York")

# Sensors included in the dashboard (bedroom sensors excluded)
LIVING_ROOM_SENSORS = ["CHRIS HEMSWORTH", "JUDE LAW", "HEATH LEDGER", "EDDIE REDMAYNE"]
# Sensors whose data is excluded BEFORE RELOC_DATE (were in bedrooms)
BEDROOM_BEFORE_RELOC = ["HEATH LEDGER", "EDDIE REDMAYNE"]

# Open-Meteo: build-time coords only, never shipped
_LAT = 40.74
_LON = -74.04


# ── Outdoor weather ────────────────────────────────────────────────────────────

def load_existing_weather() -> pd.Series:
    """Load any existing open-meteo CSVs from sensor_data/."""
    frames = []
    for f in sorted(DATA_DIR.glob("open-meteo*.csv")):
        try:
            raw = pd.read_csv(f, skiprows=3, names=["time", "TempF"])
            raw = raw[raw["time"] != "time"].copy()
            raw["TempF"] = pd.to_numeric(raw["TempF"], errors="coerce")
            raw["time"] = pd.to_datetime(raw["time"], format="%Y-%m-%dT%H:%M", utc=True)
            raw["time"] = raw["time"].dt.tz_convert(TZ)
            raw = raw.dropna(subset=["TempF"])
            raw = raw.set_index("time")["TempF"]
            frames.append(raw)
        except Exception as e:
            print(f"  Warning: could not read {f.name}: {e}")
    if not frames:
        return pd.Series(dtype=float)
    combined = pd.concat(frames)
    combined = combined[~combined.index.duplicated(keep="first")]
    return combined.sort_index()


def fetch_openmeteo(start: str, end: str) -> pd.Series:
    """
    Fetch 15-min outdoor temperature from Open-Meteo Historical Forecast API.
    Returns a Series indexed by timezone-aware NYC timestamps.
    """
    url = (
        f"https://historical-forecast-api.open-meteo.com/v1/forecast"
        f"?latitude={_LAT}&longitude={_LON}"
        f"&start_date={start}&end_date={end}"
        f"&minutely_15=temperature_2m"
        f"&temperature_unit=fahrenheit"
        f"&timezone=America%2FNew_York"
    )
    print(f"  Fetching Open-Meteo {start} → {end} …")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"  Warning: Open-Meteo fetch failed: {e}")
        return pd.Series(dtype=float)

    if "minutely_15" not in data:
        print("  Warning: minutely_15 not in response")
        return pd.Series(dtype=float)

    times = pd.to_datetime(data["minutely_15"]["time"])
    temps = data["minutely_15"]["temperature_2m"]
    s = pd.Series(temps, index=times, dtype=float)
    s.index = s.index.tz_localize(TZ)
    return s


def build_weather(grid: pd.DatetimeIndex) -> pd.Series:
    """
    Return a 15-min outdoor temp series aligned to `grid`.
    Uses existing CSVs where available, fetches the rest.
    """
    existing = load_existing_weather()

    # Determine what we need to fetch
    grid_start = grid[0].date().isoformat()
    grid_end   = grid[-1].date().isoformat()

    if existing.empty:
        fetched = fetch_openmeteo(grid_start, grid_end)
    else:
        covered_end = existing.index.max().date().isoformat()
        if covered_end < grid_end:
            # Only fetch the missing window (day after last covered day)
            fetch_start_dt = existing.index.max().normalize() + pd.Timedelta(days=1)
            fetch_start = fetch_start_dt.date().isoformat()
            fetched = fetch_openmeteo(fetch_start, grid_end)
        else:
            fetched = pd.Series(dtype=float)

    # Combine
    all_wx = pd.concat([existing, fetched]) if not fetched.empty else existing
    all_wx = all_wx[~all_wx.index.duplicated(keep="first")].sort_index()

    # Resample/interpolate to 15-min grid then reindex to our exact grid
    if all_wx.empty:
        return pd.Series([None] * len(grid), index=grid, dtype=object)

    all_wx_15 = all_wx.resample("15min").interpolate(method="time").round(1)
    aligned = all_wx_15.reindex(grid)
    return aligned


# ── Sensor data ────────────────────────────────────────────────────────────────

def load_sensor(name: str) -> pd.Series:
    """
    Load and concatenate all CSVs for a given sensor name.
    Returns a Series of TempF indexed by timezone-aware NYC timestamps.
    """
    files = sorted(DATA_DIR.glob(f"{name}_export_*.csv"))
    if not files:
        print(f"  Warning: no files found for sensor '{name}'")
        return pd.Series(dtype=float)

    frames = []
    for f in files:
        try:
            df = pd.read_csv(f, encoding="utf-8-sig")
            df.columns = ["Timestamp", "TempF", "RH"]
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            # Assume timestamps are in NYC local time (no tz info in Govee CSVs)
            df["Timestamp"] = df["Timestamp"].dt.tz_localize(TZ, ambiguous="NaT", nonexistent="NaT")
            df = df.dropna(subset=["Timestamp"])
            df = df.set_index("Timestamp")["TempF"]
            df = pd.to_numeric(df, errors="coerce").dropna()
            frames.append(df)
        except Exception as e:
            print(f"  Warning: could not read {f.name}: {e}")

    if not frames:
        return pd.Series(dtype=float)

    combined = pd.concat(frames)
    combined = combined[~combined.index.duplicated(keep="first")]
    return combined.sort_index()


# ── Build payload ──────────────────────────────────────────────────────────────

def build_payload() -> dict:
    start = pd.Timestamp(START_DATE, tz=TZ)
    end   = pd.Timestamp(END_DATE + " 23:45", tz=TZ)
    grid  = pd.date_range(start=start, end=end, freq="15min", tz=TZ)

    print("Building grid:", start.date(), "→", end.date(), f"({len(grid)} points)")

    # Outdoor weather
    print("Processing outdoor weather…")
    outdoor = build_weather(grid)

    # Sensors
    sensor_keys = {
        "CHRIS HEMSWORTH": "chris",
        "JUDE LAW":        "jude",
        "EDDIE REDMAYNE":  "eddie",
        "HEATH LEDGER":    "heath",
    }

    sensor_series = {}
    for name, key in sensor_keys.items():
        print(f"Processing {name}…")
        raw = load_sensor(name)

        # Exclude bedroom period for sensors that were relocated
        if name in BEDROOM_BEFORE_RELOC:
            cutoff = pd.Timestamp(RELOC_DATE, tz=TZ)
            raw = raw[raw.index >= cutoff]

        # Clip to our date range
        raw = raw[(raw.index >= start) & (raw.index <= end)]

        # Resample to 15-min grid, interpolate small gaps (up to 4 steps = 1 hr)
        raw_15 = raw.resample("15min").interpolate(method="time", limit=4).round(1)
        aligned = raw_15.reindex(grid)
        sensor_series[key] = aligned

    # Build label list (ISO strings, no tz offset — all NYC local)
    labels = [t.strftime("%Y-%m-%dT%H:%M") for t in grid]

    def series_to_list(s: pd.Series) -> list:
        return [None if (v is None or (isinstance(v, float) and math.isnan(v))) else round(float(v), 1)
                for v in s]

    # Annotation indices
    def ts_to_idx(date_str: str) -> int:
        ts = pd.Timestamp(date_str, tz=TZ)
        diffs = abs(grid - ts)
        return int(diffs.argmin())

    reloc_idx      = ts_to_idx(RELOC_DATE)
    ptac_idx       = ts_to_idx(PTAC_DATE)
    floor_unit_idx = ts_to_idx(FLOOR_UNIT_DATE)

    # Compute stats for Tab 3
    duration_days = (end.date() - start.date()).days + 1
    total_readings = sum(s.notna().sum() for s in sensor_series.values())

    payload = {
        "labels":         labels,
        "outdoor":        series_to_list(outdoor),
        "sensors": {
            "chris": series_to_list(sensor_series["chris"]),
            "jude":  series_to_list(sensor_series["jude"]),
            "eddie": series_to_list(sensor_series["eddie"]),
            "heath": series_to_list(sensor_series["heath"]),
        },
        "annotations": {
            "reloc_idx":      reloc_idx,
            "ptac_idx":       ptac_idx,
            "floor_unit_idx": floor_unit_idx,
            "total":          len(grid),
        },
        "stats": {
            "start_date":     start.strftime("%B %-d, %Y"),
            "end_date":       end.strftime("%B %-d, %Y"),
            "duration_days":  duration_days,
            "total_readings": int(total_readings),
        },
    }

    return payload


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== HVAC Dashboard Build ===")
    payload = build_payload()

    # Write payload.json
    payload_path = OUTPUT_DIR / "payload.json"
    with open(payload_path, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"\nWrote {payload_path.name} ({payload_path.stat().st_size // 1024}KB)")

    # Summary
    ann = payload["annotations"]
    st  = payload["stats"]
    print(f"\n  Date range:    {st['start_date']} → {st['end_date']} ({st['duration_days']} days)")
    print(f"  Total points:  {ann['total']:,} per dataset")
    print(f"  Sensor reads:  ~{st['total_readings']:,} non-null readings across 4 sensors")
    print(f"  reloc_idx:     {ann['reloc_idx']} ({payload['labels'][ann['reloc_idx']]})")
    print(f"  ptac_idx:      {ann['ptac_idx']} ({payload['labels'][ann['ptac_idx']]})")
    print(f"  floor_unit_idx:{ann['floor_unit_idx']} ({payload['labels'][ann['floor_unit_idx']]})")

    # Check for any identifying info in payload
    payload_str = json.dumps(payload)
    check_terms = ["86th", "Ventura", "10028", "40.74", "74.04", "Rose", "shawna", "Shawna"]
    found = [t for t in check_terms if t.lower() in payload_str.lower()]
    if found:
        print(f"\n  ⚠  Identifying terms found in payload: {found}")
        print("     Review before shipping!")
    else:
        print("\n  ✓  No identifying terms found in payload.")

    print("\nDone. Run build_dashboard.py next to generate the HTML.")
