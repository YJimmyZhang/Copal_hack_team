# KBC Next Owner

Team Copal · Tectonic Hackathon finals · KBC case (entrepreneurship & business growth)

**KBC spots business owners heading for a succession they haven't planned, opens the conversation, finds and prepares the right successor, and finances the handover.**

Many healthy Flemish SMEs close because nobody takes over. Advice exists; what is missing is a way to find the *right* successor and make the deal financeable. KBC sees both sides: the owner's business and the candidates' financing capacity.

## What's in this repo

| Folder | What it is |
|---|---|
| `demo/` | Click-through concept demo (KBC Touch style): relationship manager radar, owner's Next Owner space, headhunter portal, Ready-to-Own candidate portal, deal room. Plus an overview slide and MP4 walkthroughs. |
| `engine/` | The analysis engine in plain Python: fake data generator, Readiness Radar, valuation & financing, two-sided Match Engine. |
| `slides/` | Slide images used in the pitch (PNG) and their HTML sources. |
| `memory/` | Shared team notes (brief, product, business). |

## How to run

**Demo:** open `demo/index.html` in a browser. Use the grey bar at the top to switch between roles.

**Engine** (Python 3.10+; install with `pip install -r requirements.txt`):

```bash
cd engine
python run_demo.py
```

This generates fake data, runs all steps and writes `engine/out/*.json`. `engine/out/demo_case.json` holds every number shown in the demo for the hero case, Bakkerij Peeters.

**Slides** (optional, needs Playwright with Chromium): `python slides/make_data_flow.py` rebuilds the data chart from the engine output; `python slides/render_all.py` renders all slide HTML files to PNG.

## How the engine decides

1. **Readiness Radar** (`readiness.py`): 9 weighted rules (owner 60+, no family heir among shareholders, no investment loan for years, investment falling, cash piling up…) give a score 0–100 with the reasons. 60+ goes to the relationship manager. No trained model on purpose: successions are rare and noisy, and a wrong flag only costs a free conversation.
2. **Valuation & financing** (`valuation.py`): indicative value = sector multiple × average EBITDA − net debt; a 3-year outlook; the maximum takeover loan the company's own profit can repay; the split of the price into KBC loan, vendor loan and the buyer's own cash; an optional "try before you buy" plan (interim trial → 30% → 100%).
3. **Match Engine** (`matching.py`): hard filters (successor type the owner accepts, qualified, distance, financing, sector experience if the owner asks), then a score from the owner's side and from the candidate's side. **Fit = the lower of the two**, so a match only ranks high if both would like it. Every match comes with plain-language reasons.

Example output for the hero case: readiness 78 · value €2.4M–€3.6M · 131 candidates → 3 finalists · Sarah Maes 86% fit · €3.0M = €1.95M KBC loan + €0.8M vendor loan + €0.25M own funds.

## What is real and what is not

- **Real:** the engine logic (scoring, filters, financing split, matching) runs on data.
- **Fake:** all data is generated. No real customer data is used anywhere.
- **Assumptions:** sector multiples, loan terms and thresholds in `engine/config.py` are illustrative and should be replaced with KBC's own figures.
- **Not built (pitch only):** consent manager, live KBC data feeds, the headhunter and training-partner integrations, real login.
- No API keys or secrets are stored in this repo.
