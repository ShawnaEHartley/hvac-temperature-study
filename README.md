# NYC Apartment Temperature Study

A self-contained data dashboard documenting 75 days of indoor temperature monitoring in a top-floor NYC luxury high-rise with PTAC units.

**[View the dashboard →](https://ShawnaEHartley.github.io/hvac-temperature-study)**

## What this is

A personal data investigation into chronic overheating in an apartment with floor-to-ceiling windows and a flat roof. The building installed new PTACs in May 2026. Temperatures didn't improve. This dashboard documents why.

Key events captured in the data:
- **April heat wave** — old PTACs on HIGH at 60°F setting, shades closed all week; indoor temps hit 86°F
- **May 16** — sensors relocated into a living room grid to map the cooling gradient
- **May 18** — new PTACs installed; performance nearly identical to the old units under comparable outdoor conditions
- **June 3** — portable floor AC unit added; the sharpest temperature drop in the dataset

## How it's built

- **Sensors:** 4 Govee temperature sensors, 15-minute cadence
- **Outdoor weather:** Open-Meteo Historical Forecast API, aligned to the same 15-minute grid
- **Pipeline:** `build_hvac.py` — reads Govee CSV exports, fetches weather, outputs `payload.json`
- **Dashboard:** `build_dashboard.py` — reads `payload.json`, writes a self-contained `index.html` with no external dependencies
- **Stack:** Python + pandas for the pipeline; vanilla HTML/Canvas/JS for the dashboard

## Running locally

```bash
pip install pandas
python build_hvac.py       # regenerate payload.json (requires Govee CSV exports)
python build_dashboard.py  # regenerate index.html from payload.json
```

The dashboard (`index.html`) is fully self-contained — open it directly in any browser.

---

Data: [Open-Meteo](https://open-meteo.com) · Built by [Shawna Hartley](https://shawna.dev)
