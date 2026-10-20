# Product team memory
## Decisions (newest first)
- 20 Oct 14:30: One story everywhere = Bakkerij Peeters. Engine has a fixed hero case (engine/hero.py), so demo, slides and code show the same numbers: readiness 78, value EUR 2.4-3.6M, EBITDA ~EUR 620k by 2028, matches 86 / 79 / 71, deal EUR 3.0M = 1.95M KBC loan + 0.8M vendor loan + 0.25M own funds, owner wealth plan EUR 2.2M.
- 20 Oct: Financing rule (illustrative, check with KBC mentor): KBC loan <= 65% of price and <= what EBITDA repays (3.5x EBITDA, DSCR 1.3, 7 yrs at 5%); vendor loan <= 30%; buyer brings >= 8% own cash.
- 20 Oct: Jan Peeters wants a successor with food experience -> owner wish "sector experience required" is a hard filter in the Match Engine.
- 20 Oct: No trained prediction model on purpose (successions are rare and noisy). Readiness = 9 weighted rules with reasons. Optional AI (e.g. Jev) only for turning free text (wishes, CVs) into fields.
- 20 Oct: "Try before you buy": optional 6-12 month interim trial, then 30% stake, then 100%, price locked at the start.
- 20 Oct: KBC equity stake is NOT in the model (capital-heavy, lender/shareholder conflict). Q&A answer: possible later via a separate co-investment fund for search funders.
- 20 Oct: Roles: Person A = Jimmy (engine/: Readiness Radar, Valuation & financing, Match Engine, fake data). Person B = Semen (demo/: customer screens).
- 20 Oct: Made 5 animated MP4s (demo/videos/) of the demo screens for PowerPoint. Re-record with: node demo/make_videos.js
- 20 Oct: Pitch is 5 min total, ~2 min for product. Overview slide = demo/overview.png. Full click-through demo only as backup.
- 20 Oct: Style = KBC Touch web look (white, left icon rail, light blue #009fdf, navy #003768, soft cards). Demo has 6 steps incl. Deal Room.
- 20 Oct: Out of scope for the demo (pitch only): consent manager, outcome dashboard, accountant flag, training partner link, KBC Securities.

## Current state
- main has everything: demo/ (Semen), engine/ (Jimmy), slides/ (PNG + HTML sources), README.
- Demo numbers now come from the engine: python engine/run_demo.py -> engine/out/demo_case.json. Demo screens still have the numbers typed in (they match), so the MP4s stay valid.
- Slides for the deck (slides/): engine_flow_short (5 steps), ecosystem (KBC in the middle + what KBC earns), data_flow (one engine run on Peeters). Backup: engine_flow_detail, ecosystem_detail, data_architecture.
- Still to do before 16:00: make the repo public, Aikido scan + screenshot, submit on Builderbase.

## Facts and numbers the other team may use
- Hero case: Bakkerij Peeters, Antwerp, 32 staff, revenue ~EUR 4.5M, EBITDA ~EUR 559k (avg last 3 yrs), owner Jan Peeters 63.
- Engine run (fake data): 301 business clients -> 80 flagged (score >= 60) -> 13 opted in. For Peeters: 131 candidates -> 3 finalists.
- KBC already sells: business valuation (EUR 3,500 excl. VAT), takeover advice for buyers (EUR 350 excl. VAT). KBC says ~half of owners over 50 want to hand over within 5 years.

## Questions for the other team
- Business: confirm sector multiples (bakery/food now 4.5-6.6x EBITDA) and the financing rule above with a KBC mentor.
- Business: how big is the success fee? Can you give a per-deal revenue figure (loan interest + fees + assets) for the "What KBC earns" strip?

## Sync 2 handoff (fill in before putting everything together)
