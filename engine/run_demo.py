"""Run the whole engine on fake data and write JSON files the app can read.

Usage:  python run_demo.py      -> writes engine/out/*.json and prints a summary
"""
import json
from pathlib import Path

from data_gen import headhunter_sourced, make_candidates, make_companies
from matching import top_matches
from readiness import THRESHOLD, radar, readiness
from valuation import company_view

OUT = Path(__file__).parent / "out"


def main():
    OUT.mkdir(exist_ok=True)
    companies = make_companies()
    candidates = make_candidates()

    # Enrich every company with readiness + valuation
    for c in companies:
        c["readiness"] = readiness(c)
        c.update(company_view(c))

    opted = [c for c in companies if c["opted_in"]]
    # Step 4: the headhunter sources a few candidates per anonymised brief; they join the shared pool.
    for c in opted:
        candidates.extend(headhunter_sourced(c))
    matches = [top_matches(c, candidates) for c in opted]
    matches.sort(key=lambda m: m["matches"][0]["fit"] if m["matches"] else 0, reverse=True)

    # Funnel (signal -> opted in -> matched). Middle steps are illustrative.
    flagged = sum(c["readiness"]["score"] >= THRESHOLD for c in companies)
    funnel = {"business_clients": len(companies), "flagged_by_radar": flagged,
              "conversation_by_rm": round(flagged * 0.5), "opted_in": len(opted),
              "with_3_matches": sum(len(m["matches"]) >= 3 for m in matches),
              "note": "Fake data. Conversation step is an assumed 50% of flagged owners."}

    files = {"companies.json": companies, "candidates.json": candidates, "radar.json": radar(companies),
             "matches.json": matches, "funnel.json": funnel}
    for name, data in files.items():
        (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))

    print("Funnel:", funnel)
    print("\nTop 5 on the Readiness Radar:")
    for r in radar(companies, top=5):
        print(f"  {r['score']:>3}  {r['name']:<28} {r['region']:<16} {'; '.join(r['reasons'][:3])}")
    m = next(x for x in matches if x["matches"])
    c = next(x for x in companies if x["company_id"] == m["company_id"])
    v = c["valuation"]
    print(f"\nExample owner: {c['name']} ({c['sector']}, {c['employees']} staff, owner {c['owner_age']})")
    print(f"  Indicative value: €{v['equity_low']:,.0f} - €{v['equity_high']:,.0f}   max acquisition loan €{c['max_acquisition_loan']:,.0f}")
    print(f"  Pool {m['pool_size']} -> {m['passed_filters']} passed filters; filtered out: {m['filtered_out']}")
    for x in m["matches"]:
        print(f"  {x['fit']:>3}% {x['alias']} ({x['type']}, {x['confidence']}): {'; '.join(x['reasons'])}")
    t = next((x for mm in matches for x in mm["matches"] if x["trial_possible"]), None)
    if t:
        print(f"\nTry-before-you-buy plan for {t['alias']} (locked price €{t['phased_plan']['locked_price']:,.0f}):")
        for s in t["phased_plan"]["steps"]:
            if s["share"] == 0:
                print(f"  {s['step']} ({s['months']} months): {s['what']}")
            else:
                print(f"  {s['step']} {s['share']:.0%}: price €{s['price']:,.0f} = loan €{s['bank_loan']:,.0f}"
                      f" + vendor €{s['vendor_loan']:,.0f} + own €{s['equity_needed']:,.0f}  {'OK' if s['ok'] else 'GAP'}")


if __name__ == "__main__":
    main()
