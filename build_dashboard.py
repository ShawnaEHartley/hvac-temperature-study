#!/usr/bin/env python3
"""
build_dashboard.py
==================
Reads payload.json and writes index.html —
a self-contained 3-tab portfolio dashboard with no external dependencies.

Usage:
    python build_dashboard.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
PAYLOAD_PATH = ROOT / "payload.json"
OUTPUT_PATH  = ROOT / "index.html"


def build():
    payload = json.loads(PAYLOAD_PATH.read_text())
    stats   = payload["stats"]
    ann     = payload["annotations"]

    # Inline payload — strip labels to save space (we'll rebuild from start + step)
    payload_json = json.dumps(payload, separators=(",", ":"))

    html = HTML_TEMPLATE.replace("/*PAYLOAD*/", payload_json)
    OUTPUT_PATH.write_text(html, encoding="utf-8")

    size_kb = OUTPUT_PATH.stat().st_size // 1024
    print(f"Wrote {OUTPUT_PATH.name} ({size_kb}KB)")
    print(f"  {stats['start_date']} → {stats['end_date']} ({stats['duration_days']} days)")
    print(f"  {stats['total_readings']:,} sensor readings · {ann['total']:,} time points")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%231B2327'/><text x='16' y='22' font-family='system-ui,sans-serif' font-size='13' font-weight='500' fill='%23F6F7F7' text-anchor='middle' letter-spacing='0.5'>SH</text></svg>" />
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%231B2327'/><text x='16' y='22' font-family='system-ui,sans-serif' font-size='13' font-weight='500' fill='%23F6F7F7' text-anchor='middle' letter-spacing='0.5'>SH</text></svg>" />
<meta name="robots" content="noindex,nofollow">
<title>Indoor Temperature Study — NYC Luxury High-Rise</title>
<style>
/* ── Reset & Base ── */
*{box-sizing:border-box;margin:0;padding:0}
html{font-size:16px}
body{font-family:'Georgia',serif;background:#F7F4EE;color:#2C2416;line-height:1.7;min-height:100vh}
a{color:#7A6A56;text-decoration:underline;text-underline-offset:3px}

/* ── Layout ── */
.page{max-width:960px;margin:0 auto;padding:0 24px 80px}

/* ── Tabs ── */
.tab-bar{display:flex;gap:0;border-bottom:1.5px solid #D8D0C4;margin-bottom:40px;position:sticky;top:0;background:#F7F4EE;z-index:10;padding-top:16px}
.tab-btn{background:none;border:none;border-bottom:2.5px solid transparent;font-family:inherit;font-size:.85rem;letter-spacing:.08em;text-transform:uppercase;color:#9A8A76;padding:10px 20px 10px 0;cursor:pointer;margin-bottom:-1.5px;transition:color .15s,border-color .15s}
.tab-btn:hover{color:#2C2416}
.tab-btn.active{color:#2C2416;border-bottom-color:#2C2416}
.tab-panel{display:none}
.tab-panel.active{display:block}

/* ── Story Tab ── */
.story-header{padding:48px 0 36px;border-bottom:1px solid #D8D0C4;margin-bottom:48px}
.story-header h1{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:normal;letter-spacing:-.02em;line-height:1.25;margin-bottom:12px}
.story-header .byline{font-size:.85rem;color:#9A8A76;letter-spacing:.06em;text-transform:uppercase}

.hero{background:#2C2416;color:#F7F4EE;border-radius:4px;padding:36px 40px;margin-bottom:48px}
.hero-lead{font-size:1rem;letter-spacing:.08em;text-transform:uppercase;color:#C4B49A;margin-bottom:20px}
.hero-stats{display:grid;grid-template-columns:1fr 1fr;gap:20px 32px}
@media(max-width:560px){.hero-stats{grid-template-columns:1fr}}
.hero-stat{}
.hero-num{font-size:2.4rem;font-weight:normal;letter-spacing:-.03em;line-height:1;color:#F7F4EE;margin-bottom:4px}
.hero-desc{font-size:.82rem;line-height:1.55;color:#C4B49A}

.story-section{margin-bottom:44px}
.story-section h2{font-size:1.05rem;letter-spacing:.1em;text-transform:uppercase;color:#9A8A76;margin-bottom:14px;font-weight:normal}
.story-section p{font-size:1rem;line-height:1.8;color:#3A3026;margin-bottom:12px}
.story-section p:last-child{margin-bottom:0}

/* ── Data Tab ── */
.chart-header{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:14px}
.chart-title{font-size:1.05rem;letter-spacing:.06em;text-transform:uppercase;color:#9A8A76;font-weight:normal}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:14px}
.ctrl-group{display:flex;gap:5px;flex-wrap:wrap}
.zbtn{background:none;border:1px solid #D8D0C4;border-radius:3px;padding:4px 10px;font-family:inherit;font-size:.75rem;color:#7A6A56;cursor:pointer;letter-spacing:.04em;transition:all .12s;white-space:nowrap}
.zbtn:hover{background:#EEE8DE;border-color:#C4B49A}
.zbtn.active{background:#2C2416;border-color:#2C2416;color:#F7F4EE}
.ctrl-sep{width:1px;height:20px;background:#D8D0C4;margin:0 4px;align-self:center}
.sensor-toggle{display:flex;align-items:center;gap:5px;padding:4px 10px;border:1px solid #D8D0C4;border-radius:3px;font-family:inherit;font-size:.75rem;color:#7A6A56;cursor:pointer;transition:all .12s;letter-spacing:.04em;background:none}
.sensor-toggle.off{opacity:.45}
.date-input{font-family:inherit;font-size:.75rem;color:#5A4E40;border:1px solid #D8D0C4;border-radius:3px;padding:4px 7px;background:#FEFCF9;cursor:pointer}
.date-input:focus{outline:none;border-color:#C4B49A}
.sensor-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
/* key-date button: label + info icon */
.kd-btn{display:inline-flex;align-items:center;gap:0;background:none;border:1px solid #D8D0C4;border-radius:3px;font-family:inherit;font-size:.75rem;color:#7A6A56;cursor:pointer;letter-spacing:.04em;transition:all .12s;white-space:nowrap;padding:0;overflow:hidden}
.kd-btn:hover{border-color:#C4B49A}
.kd-btn.active{border-color:#2C2416}
.kd-label{padding:4px 8px;transition:background .12s,color .12s}
.kd-btn.active .kd-label{background:#2C2416;color:#F7F4EE}
.kd-info{padding:4px 7px;border-left:1px solid #D8D0C4;color:#C4B49A;font-size:.72rem;line-height:1;transition:background .12s}
.kd-btn:hover .kd-info{background:#EEE8DE}
.kd-btn.active .kd-info{border-left-color:#4A3C2A;color:#C4B49A}
/* info tooltip */
#info-tip{position:fixed;z-index:200;background:#2C2416;color:#F7F4EE;font-family:Georgia,serif;font-size:.8rem;line-height:1.6;padding:12px 15px;border-radius:4px;max-width:280px;pointer-events:none;opacity:0;transition:opacity .15s;box-shadow:0 4px 18px rgba(0,0,0,.22)}
#info-tip.show{opacity:1}
/* week label in controls bar */
.week-label{font-size:.78rem;color:#9A8A76;letter-spacing:.04em}
/* prev/next arrows flanking the chart */
.chart-outer{display:flex;align-items:center;gap:6px;margin-bottom:8px}
.chart-outer .chart-wrap{flex:1;margin-bottom:0}
.chart-nav{flex-shrink:0;background:none;border:1px solid #D8D0C4;border-radius:3px;width:28px;height:48px;font-size:1.2rem;color:#9A8A76;cursor:pointer;display:none;align-items:center;justify-content:center;transition:all .12s;line-height:1;padding:0}
.chart-nav.visible{display:flex}
.chart-nav:hover{background:#EEE8DE;border-color:#C4B49A;color:#5A4E40}
.chart-nav:disabled{opacity:.25;cursor:default}

.chart-wrap{position:relative;background:#FEFCF9;border:1px solid #D8D0C4;border-radius:4px;overflow:hidden}
#mainChart{display:block;width:100%;cursor:crosshair}

.chart-note{font-size:.75rem;color:#9A8A76;margin-bottom:32px;line-height:1.55}

/* Floor Plan */
.floorplan-wrap{margin:40px 0}
.floorplan-wrap h3{font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;color:#9A8A76;margin-bottom:12px;font-weight:normal}
.floorplan-outer{display:flex;gap:24px;align-items:flex-start;flex-wrap:wrap}
.floorplan-svg-wrap{flex:0 0 auto;max-width:480px}
.floorplan-legend{flex:1;min-width:180px}
.fp-legend-item{display:flex;align-items:center;gap:10px;margin-bottom:11px;font-size:.82rem;line-height:1.4}
.fp-dot{width:11px;height:11px;border-radius:50%;flex-shrink:0}
.fp-label strong{display:block;color:#2C2416}
.fp-label span{color:#9A8A76;font-size:.76rem}

/* Hypothesis section */
.hyp-section{background:#FEFCF9;border:1px solid #D8D0C4;border-radius:4px;padding:24px 28px;margin-top:32px}
.hyp-section h3{font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;color:#9A8A76;margin-bottom:12px;font-weight:normal}
.hyp-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}
@media(max-width:600px){.hyp-grid{grid-template-columns:1fr}}
.hyp-card{}
.hyp-sensor{font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;font-weight:normal;margin-bottom:6px}
.hyp-card p{font-size:.82rem;color:#5A4E40;line-height:1.6}

/* Build Tab */
.build-section{margin-bottom:40px}
.build-section h2{font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;color:#9A8A76;margin-bottom:14px;font-weight:normal}
.build-stat-row{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:32px}
@media(max-width:540px){.build-stat-row{grid-template-columns:1fr 1fr}}
.build-stat{background:#FEFCF9;border:1px solid #D8D0C4;border-radius:4px;padding:18px}
.build-stat .num{font-size:1.9rem;font-weight:normal;letter-spacing:-.02em;color:#2C2416;line-height:1}
.build-stat .lbl{font-size:.76rem;color:#9A8A76;margin-top:4px;line-height:1.4}
.build-block{background:#FEFCF9;border:1px solid #D8D0C4;border-radius:4px;padding:20px 24px;margin-bottom:14px}
.build-block h3{font-size:.85rem;letter-spacing:.06em;text-transform:uppercase;color:#7A6A56;margin-bottom:8px;font-weight:normal}
.build-block p,.build-block li{font-size:.9rem;color:#3A3026;line-height:1.7}
.build-block ul{padding-left:18px;margin-top:4px}
.build-block li{margin-bottom:4px}

.footer{margin-top:60px;padding-top:20px;border-top:1px solid #D8D0C4;font-size:.78rem;color:#9A8A76;text-align:center}

/* ── Mobile / touch ── */
html{-webkit-text-size-adjust:100%}
body{overflow-x:hidden}
#mainChart{touch-action:pan-y}          /* browser owns vertical scroll; we handle horizontal scrub */
.mobile-only{display:none}
.kd-select{font-family:inherit;font-size:.8rem;color:#5A4E40;border:1px solid #D8D0C4;border-radius:3px;padding:8px 10px;background:#FEFCF9;cursor:pointer;max-width:100%}
@media (max-width:640px){
  .page{padding:0 16px 60px}
  .tab-bar{margin-bottom:28px}
  .tab-btn{padding:13px 18px 13px 0;font-size:.8rem}
  .story-header{padding:32px 0 28px;margin-bottom:32px}
  .hero{padding:26px 20px;margin-bottom:36px}
  .hero-num{font-size:2rem}
  .story-section{margin-bottom:34px}
  .story-section p{font-size:.95rem;line-height:1.75}

  /* Data-tab controls: swap key-date buttons for the dropdown, enlarge targets */
  .desktop-only{display:none !important}
  select.mobile-only{display:block}
  .chart-header{gap:12px}
  .chart-title{flex:1 1 100%}
  #metric-toggle{flex:1 1 100%;gap:6px}
  #metric-toggle .zbtn{flex:1 1 0;text-align:center}
  #preset-row{gap:10px}
  .kd-select{flex:1 1 100%;font-size:16px;padding:11px 12px}
  .zbtn,.sensor-toggle{padding:10px 14px;font-size:.82rem}
  #sensor-toggles{gap:8px}
  .date-input{font-size:16px;padding:9px 10px}
  .chart-note{font-size:.78rem}

  /* Floor plan + cards stack full width */
  .floorplan-svg-wrap{max-width:100%;width:100%}
  .floorplan-legend{min-width:0;width:100%}
  .hyp-section{padding:20px 18px}
  .build-block{padding:18px 18px}
}
</style>
</head>
<body>
<div class="page">
  <div class="tab-bar">
    <button class="tab-btn active" onclick="showTab('story',this)">The Story</button>
    <button class="tab-btn" onclick="showTab('data',this)">The Data</button>
    <button class="tab-btn" onclick="showTab('build',this)">How I Built It</button>
  </div>

  <!-- ══════════════════════════════════════════════
       TAB 1: THE STORY
  ══════════════════════════════════════════════ -->
  <div class="tab-panel active" id="panel-story">
    <div class="story-header">
      <h1>It stays hotter inside<br>even when the outdoor temp drops.</h1>
      <div class="byline">Indoor temperature study · NYC luxury high-rise · PTAC units</div>
    </div>

    <div class="hero">
      <div class="hero-lead">The numbers that tell the story</div>
      <div class="hero-stats">
        <div class="hero-stat">
          <div class="hero-num">30°F</div>
          <div class="hero-desc">May 30 evening — outdoor cooled to 54°F while the living room held at 84°F. The building couldn't shed heat even with a 30° differential to the outside.</div>
        </div>
        <div class="hero-stat">
          <div class="hero-num">85°F</div>
          <div class="hero-desc">On a hot day with the PTACs set to 75, the living room still peaks in the mid-80s — right around the outdoor high. The AC can't pull it into a comfortable range; it just tracks the temperature outside.</div>
        </div>
        <div class="hero-stat">
          <div class="hero-num">≈ same</div>
          <div class="hero-desc">New PTACs installed May 2026 performed about the same as the old ones under comparable heat. Swapping the equipment didn't fix it.</div>
        </div>
        <div class="hero-stat">
          <div class="hero-num">Jun 3</div>
          <div class="hero-desc">A second, power-hungry floor unit finally cooled the space — but at a cost in electricity and noise. That cost is itself the finding.</div>
        </div>
      </div>
    </div>

    <div class="story-section">
      <h2>The Problem</h2>
      <p>Top-floor unit in a NYC luxury high-rise with PTAC units. Floor-to-ceiling windows on two walls, flat roof above. The building installed new PTACs in May 2026. Temperatures didn't improve. The building's own HVAC technician confirmed the cause is structural — the roof and windows absorb and radiate heat far faster than the equipment can remove it.</p>
      <p>The problem isn't broken equipment. The equipment works. The problem is the building's thermal envelope — and no amount of PTAC maintenance changes that. Humidity isn't the culprit either: indoor moisture held near a comfortable 46%, so the failure is purely thermal — it's the heat, not the air quality.</p>
    </div>

    <div class="story-section">
      <h2>The Action</h2>
      <p>Deployed Govee temperature and humidity sensors throughout the living room. Pulled 15-minute readings from <span id="s-start-date"></span> through <span id="s-end-date"></span> — <span id="s-duration"></span> days of continuous monitoring. Layered in Open-Meteo outdoor temperature and humidity at the same 15-minute cadence, aligned to the same timezone, so every indoor/outdoor comparison is apples-to-apples.</p>
      <p>As the study evolved, sensor placement changed. Before May 16, two sensors covered the living room and kitchen. On May 16 all four sensors were concentrated in the living room to map the cooling gradient from the PTAC side to the far end. Those changes are marked on the timeline.</p>
    </div>

    <div class="story-section">
      <h2>The Outcome</h2>
      <p>Used the data in conversations with the building and HVAC professionals to explore options beyond the current PTACs — including rewiring for a higher-capacity unit. The data made the case clearly: the existing setup can't keep pace with outdoor temperatures on warm days, regardless of which units are installed.</p>
    </div>

    <div class="story-section">
      <h2>The Tradeoff</h2>
      <p>The floor unit added June 3 finally cooled the space. But it draws significant electricity and is loud enough that it runs part-time, not continuously. Managing the heat load means keeping shades down, running the unit strategically, and accepting elevated temperatures during parts of the day.</p>
      <p>Livability in this apartment means trading off temperature, power cost, noise, and effort. That's not a complaint — it's the finding. The fact that it takes all of that to stay comfortable is precisely what the data shows about the building's envelope performance.</p>
    </div>

    <div class="story-section">
      <h2>The Real Problem</h2>
      <p>The hardest part isn't the peak temperature — it's that I'm not home when it happens. I leave in the morning and can't lower the shades when the afternoon sun comes in, can't adjust the units, can't react. On July 8 the outdoor high never even reached 90°F, yet with the shades up and no one home, the living room climbed to 89°F and stayed above 85°F for more than two hours. My dog is home during those hours. That's not a comfort issue — it's a safety one.</p>
      <p>This is where the problem becomes one of automation. A structural fix — better glazing, roof insulation — is the root solution. Short of that, what's missing is control I can't exercise remotely: shades that close automatically on solar gain, a thermostat that pre-cools before the peak, temperature alerts when a room crosses a safe threshold. The data doesn't just show the building runs hot. It shows the failure happens exactly when no one can step in.</p>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════
       TAB 2: THE DATA
  ══════════════════════════════════════════════ -->
  <div class="tab-panel" id="panel-data">

    <div class="chart-header" style="margin-top:8px">
      <div class="chart-title" id="chart-title">Temperature over time</div>
      <div class="ctrl-group" id="metric-toggle">
        <button class="zbtn active" data-metric="temp" onclick="setMetric('temp',this)">Temperature</button>
        <button class="zbtn" data-metric="rh" onclick="setMetric('rh',this)">Humidity</button>
      </div>
    </div>

    <div class="controls" id="preset-row" style="gap:6px">
      <button class="zbtn desktop-only" id="z-all" onclick="showFullStudy()">Full study</button>
      <div class="ctrl-sep desktop-only"></div>
      <div class="ctrl-group desktop-only" id="kd-btns"></div>
      <select class="kd-select mobile-only" id="kd-select" onchange="onJumpSelect(this.value)" aria-label="Jump to date"></select>
      <div class="ctrl-sep desktop-only" id="sep-sensors"></div>
      <span style="font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:#9A8A76;margin-right:2px">Sensors</span>
      <div class="ctrl-group" id="sensor-toggles"></div>
    </div>
    <div class="controls" style="gap:8px;margin-top:-6px">
      <span style="font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:#9A8A76">Range</span>
      <input type="date" id="date-start" class="date-input" onchange="applyDateRange()">
      <span style="font-size:.78rem;color:#9A8A76">–</span>
      <input type="date" id="date-end" class="date-input" onchange="applyDateRange()">
    </div>
    <div class="controls" id="axis-row" style="gap:8px;margin-top:-6px">
      <span style="font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:#9A8A76">Y-axis</span>
      <div class="ctrl-group" id="axis-toggle">
        <button class="zbtn active" data-axis="fixed" onclick="setAxis('fixed',this)">Fixed</button>
        <button class="zbtn" data-axis="auto" onclick="setAxis('auto',this)">Auto-fit</button>
      </div>
    </div>
    <div id="info-tip"></div>

    <div class="chart-outer">
      <button class="chart-nav" id="btn-prev" onclick="shiftDay(-1)">&#8249;</button>
      <div class="chart-wrap" id="chartWrap">
        <canvas id="mainChart"></canvas>
      </div>
      <button class="chart-nav" id="btn-next" onclick="shiftDay(1)">&#8250;</button>
    </div>
    <div class="chart-note" id="chart-note">
      Vertical lines mark study events: sensor relocation (May 16), new PTACs installed (May 18), floor unit added (Jun 3). Outdoor weather from Open-Meteo (dashed). 72°F comfort and 78°F habitability reference lines shown.
    </div>

    <!-- Floor Plan -->
    <div class="floorplan-wrap">
      <h3>Living room layout — sensor positions</h3>
      <div class="floorplan-outer">
        <div class="floorplan-svg-wrap">
          <svg id="floorplanSvg" viewBox="0 0 460 300" width="100%" style="display:block;border:1px solid #D8D0C4;border-radius:4px;background:#FEFCF9"></svg>
        </div>
        <div class="floorplan-legend" id="fp-legend"></div>
      </div>
      <p style="font-size:.75rem;color:#9A8A76;margin-top:10px;line-height:1.55">Room ~13'8" × 19'3". Right and bottom walls are full windows. The transect (Jude → Eddie → Heath) runs diagonally from the PTAC across the room to the floor unit — tracking the cooling gradient. Chris sits off the transect on the interior wall as a baseline.</p>
    </div>

    <!-- Hypothesis -->
    <div class="hyp-section">
      <h3>Spatial hypothesis — what the layout predicts</h3>
      <div class="hyp-grid">
        <div class="hyp-card">
          <div class="hyp-sensor" style="color:#C4553A">Jude (nearest PTAC)</div>
          <p>Predicted coolest on the transect before June 3 (in the direct airstream). After June 3, possibly warmer relative to Heath as the floor unit's influence takes over from the opposite end. Watch for the airflow caveat: a sharp drop may reflect blown air, not room temperature.</p>
        </div>
        <div class="hyp-card">
          <div class="hyp-sensor" style="color:#D4892A">Eddie (middle, window wall)</div>
          <p>The window wall position may make Eddie the stubborn warm spot after June 3 — too far from the floor unit to benefit much, on maximum solar exposure. If one sensor stays hot after June 3, expect it to be Eddie.</p>
        </div>
        <div class="hyp-card">
          <div class="hyp-sensor" style="color:#5A8A6A">Heath (nearest floor unit)</div>
          <p>Predicted hottest before June 3 (farthest from the PTAC, on the window wall). Should flip to coolest after June 3 as the floor unit comes online at the opposite corner. A dramatic post-June-3 drop in Heath is the clearest signal the floor unit is working — if it shows up.</p>
        </div>
      </div>
      <p style="font-size:.8rem;color:#7A6A56;margin-top:14px;line-height:1.6">Chris (interior control, off the transect) should be the most stable line across June 3 — least solar gain, equidistant from both units. Divergence from the transect sensors is the gradient; convergence would suggest full room mixing.</p>
    </div>

  </div>

  <!-- ══════════════════════════════════════════════
       TAB 3: HOW I BUILT IT
  ══════════════════════════════════════════════ -->
  <div class="tab-panel" id="panel-build">
    <div style="padding-top:8px">
      <div class="build-stat-row" id="build-stats"></div>

      <div class="build-section">
        <h2>Data</h2>
        <div class="build-block">
          <h3>Sensors</h3>
          <p>Four Govee temperature/humidity sensors, nicknamed after actors. Readings at 15-minute intervals. Exported as CSV from the Govee app.</p>
          <ul>
            <li><strong>Chris Hemsworth</strong> — living room, interior wall (control position throughout the study)</li>
            <li><strong>Jude Law</strong> — kitchen counter Apr 1–May 15; relocated to living room near PTAC on May 16</li>
            <li><strong>Eddie Redmayne</strong> — living room (middle of transect, window wall) from May 16 onward</li>
            <li><strong>Heath Ledger</strong> — living room (far end, near floor unit) from May 16 onward</li>
          </ul>
        </div>
        <div class="build-block">
          <h3>Outdoor weather</h3>
          <p>Open-Meteo Historical Forecast API. 15-minute cadence (<code>minutely_15=temperature_2m,relative_humidity_2m</code>), Fahrenheit, aligned to America/New_York timezone — matching the indoor sensor cadence directly. Coordinates supplied as a build-time input only; not stored in any output.</p>
        </div>
      </div>

      <div class="build-section">
        <h2>Pipeline</h2>
        <div class="build-block">
          <h3>Python</h3>
          <p>A Python script (<code>build_hvac.py</code>) handles all data processing:</p>
          <ul>
            <li>Reads Govee CSV exports, handles the UTF-8-BOM encoding and 15-min timestamp format</li>
            <li>Concatenates multiple export files per sensor (sensors were re-exported at different points in the study)</li>
            <li>Excludes bedroom sensor data entirely — only living room periods are included</li>
            <li>Deduplicates and resamples to a clean 15-min grid; interpolates small gaps (up to 1 hour) to smooth over brief sensor outages</li>
            <li>Fetches Open-Meteo for any uncovered outdoor window; reuses cached CSV exports otherwise</li>
            <li>Aligns all series to the same timezone-aware 15-min grid</li>
            <li>Outputs <code>payload.json</code> with a built-in anonymization check — scans for identifying strings before writing</li>
          </ul>
        </div>
      </div>

      <div class="build-section">
        <h2>Frontend</h2>
        <div class="build-block">
          <h3>Vanilla HTML + Canvas</h3>
          <p>Single self-contained HTML file. No frameworks, no CDN, no external dependencies. Chart rendered with the browser's Canvas 2D API.</p>
          <ul>
            <li>Multi-sensor line chart with adaptive x-axis (hourly ticks when zoomed to a day, daily ticks when zoomed out)</li>
            <li>Hover crosshair with tooltip showing all sensor readings at the cursor position</li>
            <li>Zoom presets snap to key study windows (April heat wave, the April 13 overnight, before/after June 3 floor unit)</li>
            <li>Per-sensor toggle to isolate individual lines</li>
            <li>Vertical annotation lines mark study events (sensor relocation, new PTACs, floor unit added)</li>
            <li>Floor plan showing room geometry and sensor positions (static Tier 1)</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    Indoor temperature study · a NYC luxury high-rise with PTAC units · <span id="footer-range"></span>
  </div>
</div>

<script>
const DATA = /*PAYLOAD*/;

// ── Sensor config ───────────────────────────────────────────────────────────
const SENSORS = [
  { key:'chris', label:'Chris Hemsworth', sub:'interior control',   color:'#6B7C93', lw:1.8 },
  { key:'jude',  label:'Jude Law',        sub:'nearest PTAC',       color:'#C4553A', lw:1.8 },
  { key:'eddie', label:'Eddie Redmayne',  sub:'transect middle',    color:'#D4892A', lw:1.8 },
  { key:'heath', label:'Heath Ledger',    sub:'nearest floor unit', color:'#5A8A6A', lw:1.8 },
];
const OUTDOOR = { key:'outdoor', label:'Outdoor', sub:'Open-Meteo', color:'#9AACB8', lw:1.5 };

const ANN = DATA.annotations;
const EVENTS = [
  { idx: ANN.reloc_idx,      short:'May 16', label:'May 16 — sensors\nrelocated to living room', color:'#7A8F7A' },
  { idx: ANN.ptac_idx,       short:'May 18', label:'May 18 — new\nPTACs installed',              color:'#6B7C93' },
  { idx: ANN.floor_unit_idx, short:'Jun 3',  label:'Jun 3 — floor\nunit added',                  color:'#C4553A' },
];

// ── Demand Response events ───────────────────────────────────────────────────
// Windows when PTACs were intentionally minimized (thermostat set to 85°F) to
// shed load. Shaded like night bands to explain the temperature spikes.
const DR_EVENTS = [
  { start:'2026-07-01T10:00', end:'2026-07-01T22:00' },
  { start:'2026-07-02T15:00', end:'2026-07-02T21:00' },
  { start:'2026-07-03T10:00', end:'2026-07-03T22:00' },
];
const DR_BANDS = DR_EVENTS
  .map(d => ({ s: DATA.labels.indexOf(d.start), e: DATA.labels.indexOf(d.end) }))
  .filter(b => b.s >= 0 && b.e >= 0);

const N = DATA.labels.length;
const COMFORT      = 72;
const HABITABILITY = 78;

// ── Metrics (temperature ↔ humidity) ────────────────────────────────────────
// Each metric supplies its own data arrays, axis unit, gridline step, default
// range and reference lines. The whole chart engine is metric-agnostic and
// reads everything through M().
const METRICS = {
  temp: {
    title:   'Temperature over time',
    unit:    '°F', axisSuffix: '°',
    sensors: DATA.sensors,    outdoor: DATA.outdoor,
    step: 5,  decimals: 1, defLo: 60, defHi: 95, clampLo: null, clampHi: null,
    fixed: true,   // hold the temp axis steady at 60–95°F across date shifts
    refs: [
      { v: COMFORT,      color: '#C4B49A', label: '72°F comfort' },
      { v: HABITABILITY, color: '#C4884A', label: '78°F habitability' },
    ],
    note: 'Vertical lines mark study events: sensor relocation (May 16), new PTACs installed (May 18), floor unit added (Jun 3). Outdoor weather from Open-Meteo (dashed). 72°F comfort and 78°F habitability reference lines shown. Warm amber bands (Jul 1–3) mark Demand Response events, when the thermostat was intentionally set to 85°F to reduce grid load.',
  },
  rh: {
    title:   'Relative humidity over time',
    unit:    '%', axisSuffix: '%',
    sensors: DATA.sensors_rh, outdoor: DATA.outdoor_rh,
    step: 10, decimals: 0, defLo: 20, defHi: 80, clampLo: 0, clampHi: 100,
    refs: [
      { v: 40, color: '#C4B49A', label: '40% (dry limit)' },
      { v: 60, color: '#C4884A', label: '60% (muggy)' },
    ],
    note: 'Vertical lines mark study events: sensor relocation (May 16), new PTACs installed (May 18), floor unit added (Jun 3). Outdoor humidity from Open-Meteo (dashed). The 40–60% band is the comfort range — below is dry, above feels muggy and invites mold. Warm amber bands (Jul 1–3) mark Demand Response events, when the thermostat was set to 85°F to reduce grid load.',
  },
};
let metric = 'temp';
function M() { return METRICS[metric]; }
let autoFitY = false;   // false = fixed axis (default); true = rescale Y to the visible data

// ── State ──────────────────────────────────────────────────────────────────
let viewStart = 0;
let viewEnd   = N - 1;
let hoverIdx  = -1;
const vis = { outdoor:true, chris:true, jude:true, eddie:true, heath:true };

// ── Metric toggle ────────────────────────────────────────────────────────────
function setMetric(m, btn) {
  if (m === metric) return;
  metric = m;
  document.querySelectorAll('#metric-toggle .zbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('chart-title').textContent = M().title;
  document.getElementById('chart-note').textContent  = M().note;
  // The fixed/auto axis control only applies to temperature (humidity always auto-fits)
  document.getElementById('axis-row').style.display = (m === 'temp') ? '' : 'none';
  hoverIdx = -1;
  draw();
}

function setAxis(mode, btn) {
  autoFitY = (mode === 'auto');
  document.querySelectorAll('#axis-toggle .zbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  hoverIdx = -1;
  draw();
}

// On phones the Y-axis selector sits below the chart; on desktop it stays in the controls
function placeAxisRow() {
  const row = document.getElementById('axis-row');
  if (window.matchMedia('(max-width: 640px)').matches) {
    document.querySelector('.chart-outer').after(row);
  } else {
    document.getElementById('info-tip').before(row);
  }
}

// ── Tabs ───────────────────────────────────────────────────────────────────
function showTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  btn.classList.add('active');
  if (name === 'data') requestAnimationFrame(resizeAndDraw);
}

// ── Key dates ──────────────────────────────────────────────────────────────
function labelToIdx(prefix) {
  const i = DATA.labels.findIndex(l => l.startsWith(prefix));
  return i >= 0 ? i : 0;
}

const WEEK = 96 * 7; // points in 7 days
let weekMode = false;

// Default zoom window: narrower on phones so the chart stays readable
function defaultSpan() {
  return window.matchMedia('(max-width: 640px)').matches ? 96 * 3 : WEEK;
}

const KEY_DATES = [
  {
    id: 'apr13', date: '2026-04-13', label: 'Apr 13–16',
    info: 'An early April heat wave — outdoor temps hit the low 90s. Old PTACs running on HIGH at 60°F setting, shades closed around the clock. Indoor temps still peaked near 86°F and couldn\'t recover below 73°F even overnight. The clearest early proof that the equipment can\'t keep up when the building\'s thermal mass is fully loaded.'
  },
  {
    id: 'may16', date: '2026-05-16', label: 'May 16',
    info: 'Sensors relocated from the kitchen and bedrooms into the living room, spreading coverage to map the full cooling gradient across the space. The study shifts from "is there a problem?" to "where exactly is it, and how does it move?"'
  },
  {
    id: 'may18', date: '2026-05-18', label: 'May 18',
    info: 'New PTACs installed by the building — the equipment upgrade. This is the experiment: does replacing the hardware fix it? The data shows new and old units perform about the same under comparable outdoor temperatures. The problem isn\'t the equipment.'
  },
  {
    id: 'jun3', date: '2026-06-03', label: 'Jun 3',
    info: 'A portable floor AC unit added at the opposite end of the room. The before/after contrast is the sharpest transition in the dataset — temperatures finally come down. But the cost in electricity and noise is the real finding: it takes all of that just to stay comfortable.'
  },
];

function buildControls() {
  // Key date buttons
  const kd = document.getElementById('kd-btns');
  KEY_DATES.forEach(d => {
    const wrap = document.createElement('button');
    wrap.className = 'kd-btn';
    wrap.id = 'kd-' + d.id;
    wrap.innerHTML = `<span class="kd-label">${d.label}</span><span class="kd-info" data-id="${d.id}">ⓘ</span>`;
    // Label click → jump to week view
    wrap.querySelector('.kd-label').addEventListener('click', e => { e.stopPropagation(); jumpToDate(d.id); });
    // Info icon → tooltip
    const icon = wrap.querySelector('.kd-info');
    icon.addEventListener('mouseenter', e => showTip(e, d.info));
    icon.addEventListener('mouseleave', hideTip);
    icon.addEventListener('click', e => { e.stopPropagation(); });
    kd.appendChild(wrap);
  });

  // Mobile "jump to" dropdown — mirrors the desktop key-date buttons
  const sel = document.getElementById('kd-select');
  sel.innerHTML = '<option value="">Jump to date…</option>'
    + '<option value="all">Full study</option>'
    + KEY_DATES.map(d => `<option value="${d.id}">${d.label}</option>`).join('');

  // Sensor toggles
  const st = document.getElementById('sensor-toggles');
  [...SENSORS, OUTDOOR].forEach(s => {
    const b = document.createElement('button');
    b.className = 'sensor-toggle';
    b.id = 'tog-' + s.key;
    b.innerHTML = `<span class="sensor-dot" style="background:${s.color}"></span>${s.label.split(' ')[0]}`;
    b.onclick = () => toggleSensor(s.key);
    st.appendChild(b);
  });
}

// ── Info tooltip ───────────────────────────────────────────────────────────
const tip = document.getElementById('info-tip');
function showTip(e, text) {
  tip.textContent = text;
  tip.classList.add('show');
  positionTip(e);
}
function hideTip() { tip.classList.remove('show'); }
function positionTip(e) {
  const pad = 12;
  let x = e.clientX + pad, y = e.clientY + pad;
  const tw = tip.offsetWidth || 280, th = tip.offsetHeight || 80;
  if (x + tw > window.innerWidth - 8) x = e.clientX - tw - pad;
  if (y + th > window.innerHeight - 8) y = e.clientY - th - pad;
  tip.style.left = x + 'px';
  tip.style.top  = y + 'px';
}
document.addEventListener('mousemove', e => { if (tip.classList.contains('show')) positionTip(e); });

// ── Week view controls ─────────────────────────────────────────────────────
function jumpToDate(id) {
  const d = KEY_DATES.find(x => x.id === id);
  if (!d) return;
  const dayIdx = labelToIdx(d.date); // index of 00:00 on that date
  // Show the target date near the start of the window (1 day of lead on mobile, 2 on desktop)
  const span = defaultSpan();
  const lead = (span >= WEEK ? 2 : 1) * 96;
  const start = Math.max(0, dayIdx - lead);
  const end   = Math.min(N - 1, start + span - 1);
  viewStart = start;
  viewEnd   = end;
  weekMode  = true;
  setActiveKd(id);
  updateWeekNav();
  syncDateInputs();
  hoverIdx = -1;
  draw();
}

function showFullStudy() {
  viewStart = 0;
  viewEnd   = N - 1;
  weekMode  = false;
  setActiveKd(null);
  document.getElementById('z-all').classList.add('active');
  updateWeekNav();
  syncDateInputs();
  hoverIdx = -1;
  draw();
}

function shiftDay(dir) {
  // dir: +1 = next day, -1 = prev day — preserves current window size
  const shift = dir * 96;
  const span  = viewEnd - viewStart;
  let s = viewStart + shift;
  let e = viewEnd   + shift;
  if (s < 0) { s = 0; e = span; }
  if (e > N - 1) { e = N - 1; s = Math.max(0, e - span); }
  viewStart = s;
  viewEnd   = e;
  // Deactivate key date buttons (we've scrolled away from the anchor)
  setActiveKd(null);
  updateWeekNav();
  syncDateInputs();
  hoverIdx = -1;
  draw();
}

function updateWeekNav() {
  const prevBtn = document.getElementById('btn-prev');
  const nextBtn = document.getElementById('btn-next');
  if (weekMode) {
    prevBtn.classList.add('visible');
    nextBtn.classList.add('visible');
    prevBtn.disabled = (viewStart === 0);
    nextBtn.disabled = (viewEnd >= N - 1);
  } else {
    prevBtn.classList.remove('visible');
    nextBtn.classList.remove('visible');
  }
}

function fmtDate(lbl) {
  // "2026-05-16T00:00" → "May 16"
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const m = parseInt(lbl.slice(5,7)) - 1;
  const d = parseInt(lbl.slice(8,10));
  return months[m] + ' ' + d;
}

function onJumpSelect(v) {
  if (v === '') return;
  if (v === 'all') showFullStudy(); else jumpToDate(v);
}

function setActiveKd(id) {
  document.getElementById('z-all').classList.toggle('active', id === null && !weekMode);
  KEY_DATES.forEach(d => {
    const el = document.getElementById('kd-' + d.id);
    if (el) el.classList.toggle('active', d.id === id);
  });
  // Keep the mobile dropdown in sync: a key date, Full study, or neutral (manually scrolled)
  const sel = document.getElementById('kd-select');
  if (sel) sel.value = (id !== null) ? id : (weekMode ? '' : 'all');
}

function toggleSensor(key) {
  const allKeys = [...SENSORS.map(s => s.key), OUTDOOR.key];
  const allOn = allKeys.every(k => vis[k]);
  if (allOn) {
    // from default state: solo the clicked sensor
    allKeys.forEach(k => { vis[k] = (k === key); });
  } else {
    // already in a selection: toggle just this one
    vis[key] = !vis[key];
    // if everything is now off, reset to all on
    if (!allKeys.some(k => vis[k])) allKeys.forEach(k => { vis[k] = true; });
  }
  allKeys.forEach(k => {
    const b = document.getElementById('tog-' + k);
    if (b) b.classList.toggle('off', !vis[k]);
  });
  draw();
}

function applyDateRange() {
  const s = document.getElementById('date-start').value;
  const e = document.getElementById('date-end').value;
  if (!s || !e || s > e) return;
  const si = DATA.labels.findIndex(l => l.startsWith(s));
  let ei = -1;
  for (let i = N - 1; i >= 0; i--) { if (DATA.labels[i].startsWith(e)) { ei = i; break; } }
  if (si < 0 || ei < 0 || si > ei) return;
  viewStart = si; viewEnd = ei;
  weekMode = true;
  setActiveKd(null);
  updateWeekNav();
  hoverIdx = -1;
  draw();
}

function syncDateInputs() {
  document.getElementById('date-start').value = DATA.labels[viewStart].slice(0, 10);
  document.getElementById('date-end').value   = DATA.labels[viewEnd].slice(0, 10);
}

// ── Chart geometry ─────────────────────────────────────────────────────────
const MARGIN = { top:24, right:44, bottom:52, left:46 };

function getGeo(canvas) {
  const w = canvas.width, h = canvas.height;
  return {
    x0: MARGIN.left,       y0: MARGIN.top,
    x1: w - MARGIN.right,  y1: h - MARGIN.bottom,
    w:  w - MARGIN.left - MARGIN.right,
    h:  h - MARGIN.top  - MARGIN.bottom,
  };
}

function iToX(i, geo) {
  return geo.x0 + (i - viewStart) / (viewEnd - viewStart) * geo.w;
}

function vToY(v, geo, yMin, yMax) {
  return geo.y1 - (v - yMin) / (yMax - yMin) * geo.h;
}

function xToI(x, geo) {
  const frac = (x - geo.x0) / geo.w;
  return Math.round(viewStart + frac * (viewEnd - viewStart));
}

// ── Y-axis range ───────────────────────────────────────────────────────────
function computeYRange() {
  const m = M();
  if (m.fixed && !autoFitY) return { lo: m.defLo, hi: m.defHi };   // steady axis unless auto-fit is on
  let lo = m.defLo, hi = m.defHi;
  const slice = (arr) => arr ? arr.slice(viewStart, viewEnd+1).filter(v => v != null) : [];
  const all = [
    vis.outdoor ? slice(m.outdoor) : [],
    vis.chris   ? slice(m.sensors.chris) : [],
    vis.jude    ? slice(m.sensors.jude)  : [],
    vis.eddie   ? slice(m.sensors.eddie) : [],
    vis.heath   ? slice(m.sensors.heath) : [],
  ].flat();
  if (all.length) {
    lo = Math.floor(Math.min(...all) - 2);
    hi = Math.ceil(Math.max(...all)  + 2);
  }
  // Snap to a nice grid for this metric
  lo = Math.floor(lo / m.step) * m.step;
  hi = Math.ceil(hi  / m.step) * m.step;
  // Clamp to the metric's physical bounds (e.g. RH is 0–100%)
  if (m.clampLo != null) lo = Math.max(m.clampLo, lo);
  if (m.clampHi != null) hi = Math.min(m.clampHi, hi);
  return { lo, hi };
}

// ── X-axis labels ──────────────────────────────────────────────────────────
function xAxisTicks(geo) {
  const span   = viewEnd - viewStart;
  const labels = DATA.labels;
  const ticks  = [];

  if (span <= 96) {
    // Hourly ticks
    for (let i = viewStart; i <= viewEnd; i++) {
      const lbl = labels[i];
      if (lbl && lbl.endsWith(':00')) {
        const h = parseInt(lbl.slice(11, 13));
        ticks.push({ i, text: h === 0 ? lbl.slice(5,10) : `${h}:00` });
      }
    }
  } else if (span <= 96 * 14) {
    // Daily ticks at noon
    for (let i = viewStart; i <= viewEnd; i++) {
      const lbl = labels[i];
      if (lbl && lbl.endsWith('T12:00')) ticks.push({ i, text: lbl.slice(5,10) });
    }
  } else {
    // Weekly ticks (every 7 days at noon)
    let lastDay = -1;
    for (let i = viewStart; i <= viewEnd; i++) {
      const lbl = labels[i];
      if (!lbl || !lbl.endsWith('T00:00')) continue;
      const d = new Date(lbl);
      if (d.getDay() === 1 || (lastDay === -1)) { // Monday
        ticks.push({ i, text: lbl.slice(5,10) });
        lastDay = d.getDate();
      }
    }
    // Ensure we have at least a few ticks
    if (ticks.length < 3) {
      ticks.length = 0;
      for (let i = viewStart; i <= viewEnd; i++) {
        const lbl = labels[i];
        if (lbl && lbl.endsWith('T00:00')) ticks.push({ i, text: lbl.slice(5,10) });
      }
    }
  }
  return ticks;
}

// ── Draw ───────────────────────────────────────────────────────────────────
const canvas = document.getElementById('mainChart');
const ctx    = canvas.getContext('2d');

function resizeAndDraw() {
  const wrap = document.getElementById('chartWrap');
  const dpr  = window.devicePixelRatio || 1;
  const w = wrap.clientWidth;
  const h = Math.max(320, Math.round(w * 0.45));
  canvas.width  = w * dpr;
  canvas.height = h * dpr;
  canvas.style.height = h + 'px';
  ctx.scale(dpr, dpr);
  draw();
}

function drawNightBands(geo) {
  // Shade 10 pm – 6 am (hour >= 22 or hour < 6) with a subtle blue-gray wash
  ctx.save();
  ctx.fillStyle = 'rgba(155, 175, 205, 0.11)';
  let inNight = false, bandX = 0;
  for (let i = viewStart; i <= viewEnd + 1; i++) {
    const hour = (i < N) ? parseInt(DATA.labels[i].slice(11, 13)) : -1;
    const night = (hour >= 22 || hour < 6);
    if (night && !inNight) { bandX = iToX(i, geo); inNight = true; }
    else if (!night && inNight) {
      ctx.fillRect(bandX, geo.y0, iToX(i, geo) - bandX, geo.h);
      inNight = false;
    }
  }
  if (inNight) ctx.fillRect(bandX, geo.y0, iToX(viewEnd, geo) - bandX, geo.h);
  ctx.restore();
}

function drawDrBands(geo) {
  // Shade Demand Response windows with a warm amber wash + label.
  DR_BANDS.forEach(b => {
    const s = Math.max(b.s, viewStart), e = Math.min(b.e, viewEnd);
    if (s > e) return;
    const x0 = iToX(s, geo), x1 = iToX(e, geo);
    ctx.save();
    ctx.fillStyle = 'rgba(196, 85, 58, 0.10)';
    ctx.fillRect(x0, geo.y0, x1 - x0, geo.h);
    // Left edge marker
    ctx.strokeStyle = 'rgba(196, 85, 58, 0.35)';
    ctx.setLineDash([2, 3]); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x0, geo.y0); ctx.lineTo(x0, geo.y1); ctx.stroke();
    // Label near the bottom of the plot, if the band is wide enough
    if (x1 - x0 > 40) {
      ctx.fillStyle = '#B24A34';
      ctx.font = 'bold 9px Georgia, serif';
      ctx.textAlign = 'center';
      ctx.fillText('DR EVENT', (x0 + x1) / 2, geo.y1 - 6);
    }
    ctx.restore();
  });
}

function draw() {
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.width / dpr, H = canvas.height / dpr;
  ctx.clearRect(0, 0, W, H);

  const m = M();
  const geo = getGeo({ width: W, height: H });
  const { lo, hi } = computeYRange();

  // ── Background ──
  ctx.fillStyle = '#FEFCF9';
  ctx.fillRect(0, 0, W, H);

  // ── Clip to plot area ──
  ctx.save();
  ctx.beginPath();
  ctx.rect(geo.x0, geo.y0, geo.w, geo.h);
  ctx.clip();

  // ── Night bands (10 pm – 6 am each day) ──
  drawNightBands(geo);

  // ── Demand Response event bands (Jul 1–3) ──
  drawDrBands(geo);

  // ── Gridlines ──
  ctx.strokeStyle = '#EDE8DF';
  ctx.lineWidth = 1;
  for (let t = Math.ceil(lo / m.step) * m.step; t <= hi; t += m.step) {
    const y = vToY(t, geo, lo, hi);
    ctx.beginPath(); ctx.moveTo(geo.x0, y); ctx.lineTo(geo.x1, y); ctx.stroke();
  }

  // ── Reference lines ──
  ctx.font = '10px Georgia, serif';
  m.refs.forEach(ref => {
    if (ref.v < lo || ref.v > hi) return;
    const y = vToY(ref.v, geo, lo, hi);
    ctx.save();
    ctx.strokeStyle = ref.color; ctx.setLineDash([3, 5]); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(geo.x0, y); ctx.lineTo(geo.x1, y); ctx.stroke();
    ctx.restore();
    ctx.fillStyle = ref.color;
    ctx.fillText(ref.label, geo.x1 - ctx.measureText(ref.label).width - 4, y - 4);
  });

  // ── Annotation lines ──
  EVENTS.forEach(ev => {
    if (ev.idx < viewStart || ev.idx > viewEnd) return;
    const x = iToX(ev.idx, geo);
    ctx.save();
    ctx.strokeStyle = ev.color;
    ctx.setLineDash([5, 4]);
    ctx.lineWidth = 1.2;
    ctx.globalAlpha = 0.7;
    ctx.beginPath(); ctx.moveTo(x, geo.y0); ctx.lineTo(x, geo.y1); ctx.stroke();
    ctx.restore();
    // Label at top
    ctx.save();
    ctx.fillStyle = ev.color;
    ctx.font = 'bold 9.5px Georgia, serif';
    ctx.globalAlpha = 0.85;
    ctx.textAlign = 'center';
    ctx.fillText(ev.short, x, geo.y0 + 11);
    ctx.restore();
  });

  // ── Sensor lines ──
  const datasets = [
    ...SENSORS.map(s => ({ ...s, data: m.sensors[s.key], dash: [] })),
    { ...OUTDOOR, data: m.outdoor, dash: [6, 5] },
  ];

  datasets.forEach(ds => {
    if (!vis[ds.key]) return;
    const d = ds.data;
    ctx.save();
    ctx.strokeStyle = ds.color;
    ctx.lineWidth = ds.lw;
    ctx.setLineDash(ds.dash);
    ctx.lineJoin = 'round';
    ctx.beginPath();
    let started = false;
    for (let i = viewStart; i <= viewEnd; i++) {
      const v = d[i];
      if (v == null) { started = false; continue; }
      const x = iToX(i, geo), y = vToY(v, geo, lo, hi);
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();
  });

  // ── Hover crosshair ──
  if (hoverIdx >= viewStart && hoverIdx <= viewEnd) {
    const x = iToX(hoverIdx, geo);
    ctx.save();
    ctx.strokeStyle = 'rgba(44,36,22,0.25)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.beginPath(); ctx.moveTo(x, geo.y0); ctx.lineTo(x, geo.y1); ctx.stroke();

    // Dots on each line
    datasets.forEach(ds => {
      if (!vis[ds.key]) return;
      const v = ds.data[hoverIdx];
      if (v == null) return;
      const y = vToY(v, geo, lo, hi);
      ctx.fillStyle = ds.color;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }

  ctx.restore(); // unclip

  // ── Y axis labels ──
  ctx.fillStyle = '#9A8A76';
  ctx.font = '11px Georgia, serif';
  ctx.textAlign = 'right';
  for (let t = Math.ceil(lo / m.step) * m.step; t <= hi; t += m.step) {
    const y = vToY(t, geo, lo, hi);
    ctx.fillText(t + m.axisSuffix, geo.x0 - 6, y + 4);
  }

  // ── X axis labels ──
  ctx.fillStyle = '#9A8A76';
  ctx.font = '11px Georgia, serif';
  ctx.textAlign = 'center';
  xAxisTicks(geo).forEach(tick => {
    const x = iToX(tick.i, geo);
    if (x < geo.x0 + 10 || x > geo.x1 - 10) return;
    ctx.fillText(tick.text, x, geo.y1 + 16);
  });

  // ── X axis line ──
  ctx.strokeStyle = '#D8D0C4';
  ctx.lineWidth = 1;
  ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(geo.x0, geo.y1); ctx.lineTo(geo.x1, geo.y1); ctx.stroke();

  // ── Tooltip ──
  if (hoverIdx >= viewStart && hoverIdx <= viewEnd) {
    drawTooltip(geo, lo, hi);
  }
}

function drawTooltip(geo, lo, hi) {
  const lbl = DATA.labels[hoverIdx] || '';
  const dateStr = lbl.replace('T', ' ');
  const x0 = iToX(hoverIdx, geo);

  // Build rows
  const m = M();
  const rows = [];
  SENSORS.forEach(s => {
    if (!vis[s.key]) return;
    const v = m.sensors[s.key][hoverIdx];
    if (v != null) rows.push({ color: s.color, name: s.label.split(' ')[0], val: v.toFixed(m.decimals) + m.unit });
  });
  if (vis.outdoor) {
    const v = m.outdoor[hoverIdx];
    if (v != null) rows.push({ color: OUTDOOR.color, name: 'Outdoor', val: v.toFixed(m.decimals) + m.unit });
  }
  if (!rows.length) return;

  const padding = 10, rowH = 17, headerH = 18;
  const TW = 155, TH = padding * 2 + headerH + rows.length * rowH;

  let tx = x0 + 12;
  if (tx + TW > geo.x1 - 4) tx = x0 - TW - 12;
  const ty = geo.y0 + 12;

  ctx.save();
  ctx.fillStyle = 'rgba(44,36,22,0.88)';
  roundRect(ctx, tx, ty, TW, TH, 4);
  ctx.fill();

  ctx.fillStyle = '#C4B49A';
  ctx.font = '10px Georgia, serif';
  ctx.textAlign = 'left';
  ctx.fillText(dateStr, tx + padding, ty + padding + 10);

  rows.forEach((r, i) => {
    const ry = ty + padding + headerH + i * rowH;
    ctx.fillStyle = r.color;
    ctx.beginPath(); ctx.arc(tx + padding + 4, ry + 6, 3.5, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#F7F4EE';
    ctx.font = '11px Georgia, serif';
    ctx.fillText(r.name, tx + padding + 13, ry + 10);
    ctx.textAlign = 'right';
    ctx.fillText(r.val, tx + TW - padding, ry + 10);
    ctx.textAlign = 'left';
  });
  ctx.restore();
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y); ctx.arcTo(x+w, y, x+w, y+r, r);
  ctx.lineTo(x + w, y + h - r); ctx.arcTo(x+w, y+h, x+w-r, y+h, r);
  ctx.lineTo(x + r, y + h); ctx.arcTo(x, y+h, x, y+h-r, r);
  ctx.lineTo(x, y + r); ctx.arcTo(x, y, x+r, y, r);
  ctx.closePath();
}

// ── Mouse events ───────────────────────────────────────────────────────────
canvas.addEventListener('mousemove', e => {
  const dpr  = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const mx   = (e.clientX - rect.left);
  const geo  = getGeo({ width: canvas.width / dpr, height: canvas.height / dpr });
  if (mx < geo.x0 || mx > geo.x1) { hoverIdx = -1; draw(); return; }
  const i = Math.max(viewStart, Math.min(viewEnd, xToI(mx, geo)));
  if (i !== hoverIdx) { hoverIdx = i; draw(); }
});

canvas.addEventListener('mouseleave', () => { hoverIdx = -1; draw(); });

// Touch: tap to read a value, horizontal drag to scrub, vertical drag scrolls the page.
function hoverFromClientX(clientX) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const mx = clientX - rect.left;
  const geo = getGeo({ width: canvas.width/dpr, height: canvas.height/dpr });
  if (mx < geo.x0 || mx > geo.x1) return;
  const i = Math.max(viewStart, Math.min(viewEnd, xToI(mx, geo)));
  if (i !== hoverIdx) { hoverIdx = i; draw(); }
}
let tStartX = 0, tStartY = 0, tScrub = false;
canvas.addEventListener('touchstart', e => {
  const t = e.touches[0];
  tStartX = t.clientX; tStartY = t.clientY; tScrub = false;
}, { passive: true });
canvas.addEventListener('touchmove', e => {
  const t = e.touches[0];
  const dx = Math.abs(t.clientX - tStartX), dy = Math.abs(t.clientY - tStartY);
  if (!tScrub) {
    if (dx > dy && dx > 6) tScrub = true;        // horizontal intent → scrub the chart
    else if (dy > dx && dy > 6) {                // vertical intent → let the page scroll
      if (hoverIdx !== -1) { hoverIdx = -1; draw(); }
      return;
    } else return;
  }
  e.preventDefault();                            // we own the horizontal gesture now
  hoverFromClientX(t.clientX);
}, { passive: false });
canvas.addEventListener('touchend', e => {
  if (!tScrub) {                                 // a tap, not a drag → inspect that point
    const t = e.changedTouches[0];
    if (Math.abs(t.clientX - tStartX) < 8 && Math.abs(t.clientY - tStartY) < 8)
      hoverFromClientX(t.clientX);
  }
  tScrub = false;
}, { passive: true });

// ── Floor Plan ─────────────────────────────────────────────────────────────
function drawFloorPlan() {
  const svg = document.getElementById('floorplanSvg');
  const W = 460, H = 300;
  const pad = 28;
  const rw = W - pad*2, rh = H - pad*2;

  // Sensor positions on grid (col 1-10, row A-D)
  // x = (col - 0.5) / 10,  y = (row_index + 0.5) / 4
  const rowIdx = { A:0, B:1, C:2, D:3 };
  function cellXY(col, row) {
    return [
      pad + ((col - 0.5) / 10) * rw,
      pad + ((rowIdx[row] + 0.5) / 4) * rh
    ];
  }

  const [chx, chy] = cellXY(5, 'A');
  const [jux, juy] = cellXY(9, 'A');
  const [edx, edy] = cellXY(6, 'B');
  const [hex, hey] = cellXY(2, 'C');

  let s = ``;

  // Room outline
  s += `<rect x="${pad}" y="${pad}" width="${rw}" height="${rh}" fill="#FEFCF9" stroke="#C4B49A" stroke-width="1.5"/>`;

  // Window walls — right edge (col 10) and bottom edge (row D)
  const wt = 4;
  // Right wall (window)
  s += `<rect x="${W-pad-wt}" y="${pad}" width="${wt}" height="${rh}" fill="#D4C9B8" opacity="0.6"/>`;
  // Bottom wall (window)
  s += `<rect x="${pad}" y="${H-pad-wt}" width="${rw}" height="${wt}" fill="#D4C9B8" opacity="0.6"/>`;

  // Window labels
  s += `<text x="${W-pad+6}" y="${pad + rh/2}" font-family="Georgia,serif" font-size="9" fill="#9A8A76" transform="rotate(90,${W-pad+10},${pad+rh/2})">windows</text>`;
  s += `<text x="${pad + rw/2}" y="${H-pad+16}" font-family="Georgia,serif" font-size="9" fill="#9A8A76" text-anchor="middle">windows</text>`;

  // Interior wall labels
  s += `<text x="${pad-6}" y="${pad + rh/2}" font-family="Georgia,serif" font-size="9" fill="#C4B49A" text-anchor="middle" transform="rotate(-90,${pad-10},${pad+rh/2})">interior</text>`;
  s += `<text x="${pad + rw/2}" y="${pad-8}" font-family="Georgia,serif" font-size="9" fill="#C4B49A" text-anchor="middle">interior wall ← no windows →</text>`;

  // PTAC unit (top-right corner)
  const ptacX = W - pad - 18, ptacY = pad + 4;
  s += `<g class="fp-marker" style="cursor:pointer" data-tip="PTAC">`;
  s += `<rect x="${ptacX}" y="${ptacY}" width="16" height="20" rx="2" fill="#A0B0C0" stroke="#6B7C93" stroke-width="1"/>`;
  s += `<text x="${ptacX+8}" y="${ptacY+13}" font-family="Georgia,serif" font-size="7.5" fill="#fff" text-anchor="middle" font-weight="bold">PTAC</text></g>`;

  // Floor unit (bottom-left corner, added Jun 3)
  const fuX = pad + 4, fuY = H - pad - 24;
  s += `<g class="fp-marker" style="cursor:pointer" data-tip="Floor AC (added Jun 3)">`;
  s += `<rect x="${fuX}" y="${fuY}" width="18" height="20" rx="2" fill="#C4896A" stroke="#C4553A" stroke-width="1" stroke-dasharray="3,2"/>`;
  s += `<text x="${fuX+9}" y="${fuY+13}" font-family="Georgia,serif" font-size="7" fill="#fff" text-anchor="middle" font-weight="bold">Floor</text>`;
  s += `<text x="${fuX+9}" y="${fuY+20}" font-family="Georgia,serif" font-size="7" fill="#fff" text-anchor="middle" font-weight="bold">AC</text></g>`;

  // Transect line (light dashed, Jude → Eddie → Heath)
  s += `<line x1="${jux}" y1="${juy}" x2="${edx}" y2="${edy}" stroke="#D8D0C4" stroke-width="1" stroke-dasharray="3,3"/>`;
  s += `<line x1="${edx}" y1="${edy}" x2="${hex}" y2="${hey}" stroke="#D8D0C4" stroke-width="1" stroke-dasharray="3,3"/>`;

  // Sensor dots
  const sensors = [
    { x:chx, y:chy, color:'#6B7C93', name:'Chris',  cell:'A5', tip:'Chris Hemsworth' },
    { x:jux, y:juy, color:'#C4553A', name:'Jude',   cell:'A9', tip:'Jude Law' },
    { x:edx, y:edy, color:'#D4892A', name:'Eddie',  cell:'B6', tip:'Eddie Redmayne' },
    { x:hex, y:hey, color:'#5A8A6A', name:'Heath',  cell:'C2', tip:'Heath Ledger' },
  ];

  sensors.forEach(sen => {
    s += `<g class="fp-marker" style="cursor:pointer" data-tip="${sen.tip}">`;
    s += `<circle cx="${sen.x}" cy="${sen.y}" r="8" fill="${sen.color}" opacity="0.9"/>`;
    s += `<text x="${sen.x}" y="${sen.y + 4}" font-family="Georgia,serif" font-size="8" fill="#fff" text-anchor="middle" font-weight="bold">${sen.name}</text></g>`;
  });

  svg.innerHTML = s;

  // Hover tooltips on floor-plan markers (reuses the styled #info-tip)
  svg.querySelectorAll('.fp-marker').forEach(el => {
    const text = el.getAttribute('data-tip');
    el.addEventListener('mouseenter', e => showTip(e, text));
    el.addEventListener('mouseleave', hideTip);
  });

  // Legend
  const leg = document.getElementById('fp-legend');
  leg.innerHTML = '';
  const legItems = [
    { color:'#6B7C93', name:'Chris Hemsworth', detail:'A5 — interior wall, control' },
    { color:'#C4553A', name:'Jude Law',         detail:'A9 — near PTAC (post May 16)' },
    { color:'#D4892A', name:'Eddie Redmayne',   detail:'B6 — transect middle, window wall' },
    { color:'#5A8A6A', name:'Heath Ledger',     detail:'C2 — near floor unit, window wall' },
    { color:'#A0B0C0', name:'PTAC',             detail:'A10 — top-right corner' },
    { color:'#C4553A', name:'Floor AC (Jun 3)', detail:'D1 — bottom-left, vents out window' },
  ];
  legItems.forEach(li => {
    leg.innerHTML += `<div class="fp-legend-item">
      <span class="fp-dot" style="background:${li.color}${li.name.includes('Floor') ? ';border:1.5px dashed #C4553A;background:#C4896A' : ''}"></span>
      <div class="fp-label"><strong>${li.name}</strong><span>${li.detail}</span></div>
    </div>`;
  });
}

// ── Build tab stats ────────────────────────────────────────────────────────
function buildBuildStats() {
  const st = DATA.stats;
  const el = document.getElementById('build-stats');
  el.innerHTML = `
    <div class="build-stat"><div class="num">${st.duration_days}</div><div class="lbl">days of monitoring<br>${st.start_date} – ${st.end_date}</div></div>
    <div class="build-stat"><div class="num">${(st.total_readings/1000).toFixed(1)}k</div><div class="lbl">sensor readings<br>15-minute cadence</div></div>
    <div class="build-stat"><div class="num">4</div><div class="lbl">sensors<br>living room coverage</div></div>
  `;

  // Inline stats in story tab
  document.getElementById('s-start-date').textContent = st.start_date;
  document.getElementById('s-end-date').textContent   = st.end_date;
  document.getElementById('s-duration').textContent   = st.duration_days;
  document.getElementById('footer-range').textContent = st.start_date + ' – ' + st.end_date;
}

// ── Init ───────────────────────────────────────────────────────────────────
buildControls();
// Default: last few days (3 on mobile, 7 on desktop), most recent data flush right
viewStart = Math.max(0, N - defaultSpan());
viewEnd   = N - 1;
weekMode  = true;
setActiveKd(null);
updateWeekNav();
// Set date input bounds + initial values
const minDate = DATA.labels[0].slice(0, 10);
const maxDate = DATA.labels[N - 1].slice(0, 10);
['date-start','date-end'].forEach(id => {
  const el = document.getElementById(id);
  el.min = minDate; el.max = maxDate;
});
syncDateInputs();
buildBuildStats();
drawFloorPlan();
placeAxisRow();
resizeAndDraw();

window.addEventListener('resize', () => {
  placeAxisRow();
  if (document.getElementById('panel-data').classList.contains('active')) resizeAndDraw();
});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
