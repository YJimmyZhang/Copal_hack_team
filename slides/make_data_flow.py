"""Builds slides/data_flow.png ("What happens to the data") from engine/out/*.json.

Run after `python engine/run_demo.py`:  python slides/make_data_flow.py
(needs Playwright with Chromium for the PNG render)
"""
import collections
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "engine", "out")
HERE = os.path.dirname(os.path.abspath(__file__))
companies = json.load(open(os.path.join(OUT, "companies.json")))
case = json.load(open(os.path.join(OUT, "demo_case.json")))
funnel = json.load(open(os.path.join(OUT, "funnel.json")))
matches = json.load(open(os.path.join(OUT, "matches.json")))[0]["matches"]

BLUE, ORANGE, GRAY_SOFT = "#2a78d6", "#eb6834", "#e6e9ef"
INK, MUTED, GRID, NAVY = "#1b2333", "#5a6475", "#e3e6ec", "#0d2b6b"

# ---------- Panel 1: readiness histogram ----------
scores = [c["readiness"]["score"] for c in companies]
cnt = collections.Counter(min(s, 99) // 10 * 10 for s in scores)
bins = [cnt.get(b, 0) for b in range(0, 90, 10)]
hero_score = case["readiness"]["score"]
W, H, L, B, T, R = 520, 380, 52, 48, 34, 10
pw, ph = W - L - R, H - B - T
ymax = (max(bins) // 20 + 1) * 20
bw = pw / len(bins)
p1 = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
for v in range(0, ymax + 1, 20):
    y = T + ph - v / ymax * ph
    p1.append(f'<line x1="{L}" x2="{W-R}" y1="{y}" y2="{y}" stroke="{GRID}"/>'
              f'<text x="{L-10}" y="{y+5}" text-anchor="end" font-size="15" fill="{MUTED}">{v}</text>')
for i, n in enumerate(bins):
    x = L + i * bw + 2
    h = n / ymax * ph
    col = BLUE if i >= 6 else GRAY_SOFT
    p1.append(f'<path d="M{x},{T+ph} v{-h+4} q0,-4 4,-4 h{bw-12} q4,0 4,4 v{h-4} z" fill="{col}"/>'
              f'<text x="{x+(bw-4)/2}" y="{T+ph-h-8}" text-anchor="middle" font-size="14" fill="{MUTED}">{n}</text>'
              f'<text x="{x+(bw-4)/2}" y="{T+ph+22}" text-anchor="middle" font-size="14" fill="{MUTED}">{i*10}</text>')
tx = L + 6 * bw
p1.append(f'<line x1="{tx}" x2="{tx}" y1="{T-6}" y2="{T+ph}" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>'
          f'<text x="{tx-8}" y="{T+4}" text-anchor="end" font-size="15" font-weight="700" fill="{INK}">threshold 60</text>')
hb = hero_score // 10
hx = L + hb * bw + bw / 2
hy = T + ph - bins[hb] / ymax * ph
p1.append(f'<line x1="{hx}" x2="{hx}" y1="{hy-46}" y2="{hy-28}" stroke="{NAVY}" stroke-width="2"/>'
          f'<text x="{hx}" y="{hy-52}" text-anchor="middle" font-size="15" font-weight="800" fill="{NAVY}">Peeters {hero_score}</text>')
p1.append(f'<text x="{L+pw/2}" y="{H-4}" text-anchor="middle" font-size="15" fill="{MUTED}">Readiness score (0–100)</text>'
          f'<text x="14" y="{T+ph/2}" transform="rotate(-90 14 {T+ph/2})" text-anchor="middle" font-size="15" fill="{MUTED}">Owners</text></svg>')

# ---------- Panel 2: filter cascade ----------
fo = case["filtered_out"]
order = [("Type not wanted", "Owner excluded this type of successor"), ("Not yet qualified", "Candidate not yet qualified"),
         ("Too far away", "Too far"), ("Financing gap", "Financing gap too large"), ("No food experience", "No experience in this sector")]
pool = case["pool_size"]
steps, keep = [("Candidate pool", pool, 0)], pool
for lab, key in order:
    d = fo.get(key, 0)
    keep -= d
    steps.append((lab, keep, d))
W2, rowh, lab_w = 520, 50, 190
bar_w = W2 - lab_w - 60
p2 = [f'<svg width="{W2}" height="{rowh*len(steps)+60}" viewBox="0 0 {W2} {rowh*len(steps)+60}">']
for i, (name, k, d) in enumerate(steps):
    y = 8 + i * rowh
    kw, dw = max(k / pool * bar_w, 3), d / pool * bar_w
    p2.append(f'<text x="{lab_w-12}" y="{y+25}" text-anchor="end" font-size="16" fill="{INK}">{name}</text>'
              f'<rect x="{lab_w}" y="{y+6}" width="{kw}" height="28" rx="4" fill="{BLUE}"/>')
    if d:
        p2.append(f'<rect x="{lab_w+kw+2}" y="{y+6}" width="{max(dw-2,1)}" height="28" rx="4" fill="{GRAY_SOFT}"/>'
                  f'<text x="{lab_w+kw+dw+8}" y="{y+26}" font-size="15" fill="{MUTED}">−{d}</text>')
    if kw > 40:
        p2.append(f'<text x="{lab_w+8}" y="{y+26}" font-size="15" font-weight="700" fill="#fff">{k}</text>')
    else:
        p2.append(f'<text x="{lab_w+kw+ (dw if d else 0) + (46 if d else 8)}" y="{y+26}" font-size="15" font-weight="800" fill="{NAVY}">{k} left</text>')
p2.append('</svg>')

# ---------- Panel 3: two-sided scores for the final three ----------
names = {"K900": "Sarah Maes", "K901": "Own staff (MBO)", "K902": "Search fund"}
W3, rh = 520, 104
lab3, bw3 = 170, 250
p3 = [f'<svg width="{W3}" height="{rh*len(matches)+40}" viewBox="0 0 {W3} {rh*len(matches)+40}">']
for v in (0, 50, 100):
    x = lab3 + v / 100 * bw3
    p3.append(f'<line x1="{x}" x2="{x}" y1="0" y2="{rh*len(matches)}" stroke="{GRID}"/>'
              f'<text x="{x}" y="{rh*len(matches)+20}" text-anchor="middle" font-size="14" fill="{MUTED}">{v}</text>')
for i, m in enumerate(matches):
    y = i * rh + 14
    p3.append(f'<text x="{lab3-12}" y="{y+30}" text-anchor="end" font-size="16" font-weight="700" fill="{INK}">{names.get(m["candidate_id"], m["alias"])}</text>')
    for j, (val, col) in enumerate(((m["owner_view"], BLUE), (m["candidate_view"], ORANGE))):
        yy = y + j * 30
        p3.append(f'<rect x="{lab3}" y="{yy+4}" width="{val/100*bw3}" height="24" rx="4" fill="{col}"/>'
                  f'<text x="{lab3+val/100*bw3+8}" y="{yy+22}" font-size="15" fill="{INK}">{val}</text>')
    p3.append(f'<text x="{W3-4}" y="{y+36}" text-anchor="end" font-size="22" font-weight="800" fill="{NAVY}">{m["fit"]}%</text>')
p3.append('</svg>')

top3 = ", ".join(f"{m['fit']}%" for m in matches)
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;background:#fff;color:{INK};font-family:Inter,"DejaVu Sans",sans-serif;padding:56px 72px;display:flex;flex-direction:column;gap:28px}}
header{{border-bottom:3px solid {NAVY};padding-bottom:14px}}
h1{{font-size:52px;font-weight:800;color:{NAVY};letter-spacing:-.6px}}
h1 span{{font-weight:400;color:#1f5fbf}}
.sub{{font-size:23px;color:{MUTED};margin-top:6px}}
.panels{{display:flex;gap:40px;flex:1}}
.p{{flex:1;display:flex;flex-direction:column;gap:12px;min-width:0}}
.n{{font-size:18px;font-weight:700;letter-spacing:1.5px;color:#29a3dc}}
h2{{font-size:30px;font-weight:800;color:{NAVY};line-height:1.1}}
.q{{font-size:19px;color:{MUTED}}}
.chart{{flex:1;display:flex;align-items:center}}
.take{{background:#f3f5f9;border-left:5px solid {BLUE};border-radius:8px;padding:14px 18px;font-size:20px;line-height:1.35}}
.take b{{color:{NAVY}}}
.funnel{{font-size:18px}}
.funnel b{{color:{NAVY}}}
.legend{{display:flex;gap:20px;font-size:16px;color:{MUTED}}}
.legend i{{display:inline-block;width:14px;height:14px;border-radius:3px;margin-right:6px;vertical-align:-2px}}
.foot{{font-size:16px;color:{MUTED}}}
</style></head><body>
<header><h1>What happens to the data <span>· one run of the engine</span></h1>
<div class="sub">{funnel['business_clients']} business clients and {pool} candidates (fake data). Hero case: {case['company']}, owner {case['owner']} ({case['owner_age']}).</div></header>
<div class="panels">
 <div class="p"><span class="n">1 · SPOT</span><h2>Score every owner</h2><div class="q">9 rules turn bank and register data into a readiness score with reasons</div>
  <div class="chart">{''.join(p1)}</div>
  <div class="funnel"><b>{funnel['business_clients']}</b> scored → <b>{funnel['flagged_by_radar']}</b> flagged → <b>{funnel['conversation_by_rm']}</b> talks* → <b>{funnel['opted_in']}</b> opted in</div>
  <div class="take"><b>Peeters scores {hero_score}:</b> {', '.join(r.lower() if i else r for i, r in enumerate(case['readiness']['reasons'][:3]))}.</div></div>
 <div class="p"><span class="n">2 · FILTER</span><h2>Remove deal-breakers</h2><div class="q">Hard filters for Bakkerij Peeters, applied in order</div>
  <div class="chart">{''.join(p2)}</div>
  <div class="take"><b>{pool} → {len(matches)}.</b> Accepted type, qualified, close enough, can finance it, and has food experience (Jan's wish).</div></div>
 <div class="p"><span class="n">3 · SCORE</span><h2>Both sides must like it</h2><div class="q">Each finalist scored from both sides (0–100)</div>
  <div class="legend"><span><i style="background:{BLUE}"></i>Owner's view of the candidate</span><span><i style="background:{ORANGE}"></i>Candidate's view of the company</span></div>
  <div class="chart">{''.join(p3)}</div>
  <div class="take"><b>Fit = the lower of the two:</b> {top3}. Sarah Maes is the best match, and KBC can finance her takeover.</div></div>
</div>
<div class="foot">* Conversation step assumed at 50% of flagged owners. All data is generated; multiples, loan terms and thresholds are illustrative (engine/config.py).</div>
</body></html>"""
open(os.path.join(HERE, "data_flow.html"), "w").write(html)

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pwr:
        b = pwr.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1.5)
        pg.goto("file://" + os.path.join(HERE, "data_flow.html"))
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(HERE, "data_flow.png"))
        b.close()
    print("wrote slides/data_flow.png")
except ImportError:
    print("wrote slides/data_flow.html (install Playwright to render the PNG)")
