# Product team memory
## Decisions (newest first)
- 20 Oct: Made 5 animated MP4s (demo/videos/, 10-13 s each, 1920x1080) of the demo screens: cursor moves, scrolls, clicks, with captions. For animated PowerPoint slides. Re-record with: node demo/make_videos.js
- 20 Oct: Pitch is 5 min total, ~2 min for product. Show ONE overview slide (demo/overview.png): 6 steps, per step the actor + a mini screen + "what they get", and the 3 engines (Radar, Valuation, Match) underneath. Full click-through demo only as backup / for questions.
- 20 Oct: Style = KBC Touch web look (white, left icon rail, light blue #009fdf, navy #003768, soft cards). Added step 6 "Deal Room" screen for the RM (owner <-> successor, 86% fit, deal checklist, financing EUR 3.0M = 1.95M KBC loan + 0.8M vendor loan + 0.25M own funds).
- 20 Oct: Demo = desktop web pages, one per actor, walking fake company Bakkerij Peeters (owner Jan Peeters, 63; successor Sarah Maes) through the 6 steps. Role switcher is a plain grey demo bar, not part of the design.
- 20 Oct: Split the core programs between two product members (names not yet assigned):
  - Person A, predictions & analysis: Readiness Radar (succession score 0-100 + reasons), Valuation & Projections (value range = EBITDA x sector multiple, 3-5 yr forecast), Match Engine (fit score + shortlist), fake demo data.
  - Person B, customer screens: Relationship Manager Cockpit, Owner Space ("Next Owner" in KBC Business app, the star screen), Headhunter Portal, Ready-to-Own Candidate Portal.
- 20 Oct: Out of scope for the demo (mention in pitch only): financing calculator logic, consent manager, outcome dashboard, accountant flag, training partner link, KBC Securities.

## Current state
- Saved version 1 (20 Oct): demo/index.html = full demo, 5 screens (RM radar, Owner, Headhunter, Candidate, RM Deal Room). demo/overview.html + overview.png = the one-slide summary.
- All numbers are still fixed placeholders; Person A's logic is not plugged in yet.
- Next: A and B agree the "handshake" (Radar -> score + reasons; Valuation -> value range; Match -> fit score per candidate).

## Facts and numbers the other team may use

## Questions for the other team
- Business: which EBITDA multiples per sector should the valuation use? (placeholder now: 4-6)

## Sync 2 handoff (fill in before putting everything together)
