"""Run the whole engine on fake data and write JSON files the demo and slides can read.

Usage:  python run_demo.py      -> writes engine/out/*.json and prints a summary

The hero case (Bakkerij Peeters, see hero.py) is part of the data, so every number
in demo/index.html comes out of this engine (engine/out/demo_case.json).
"""
import copy
import json
from pathlib import Path

from data_gen import headhunter_sourced, make_candidates, make_companies
from hero import HERO_CANDIDATES, HERO_COMPANY
from matching import top_matches
from readiness import THRESHOLD, radar, readiness
from valuation import company_view, financing_check, phased_plan

OUT = Path(__file__).parent / "out"


def main():
    OUT.mkdir(exist_ok=True)
    companies = [copy.deepcopy(HERO_COMPANY)] + make_companies()
    candidates = [copy.deepcopy(k) for k in HERO_CANDIDATES] + make_candidates()

    for c in companies:
        c["readiness"] = readiness(c)
        c.update(company_view(c))

    opted = [c for c in companies if c["opted_in"]]
    for c in opted[1:]:                     # headhunter sources per brief (hero's candidates are fixed)
        candidates.extend(headhunter_sourced(c))
    matches = [top_matches(c, candidates) for c in opted]

    flagged = sum(c["readiness"]["score"] >= THRESHOLD for c in companies)
    funnel = {"business_clients": len(companies), "flagged_by_radar": flagged,
              "conversation_by_rm": round(flagged * 0.5), "opted_in": len(opted),
              "with_3_matches": sum(len(m["matches"]) >= 3 for m in matches),
              "note": "Fake data. Conversation step is an assumed 50% of flagged owners."}

    # ---- the hero case, exactly as the demo screens show it ----
    hero = companies[0]
    hm = matches[0]
    top = hm["matches"][0]
    price = hero["valuation"]["equity_mid"]
    fin = financing_check(hero, top["financing"]["own_funds"], price)
    by_id = {k["candidate_id"]: k for k in candidates}
    demo_case = {
        "company": hero["name"], "owner": hero["owner_name"], "owner_age": hero["owner_age"],
        "region": hero["region"], "employees": hero["employees"],
        "readiness": hero["readiness"],
        "value_range": [hero["valuation"]["equity_low"], hero["valuation"]["equity_high"]],
        "ebitda_2028_base": hero["projections"]["outlook"][-1]["ebitda_base"],
        "max_acquisition_loan": hero["max_acquisition_loan"],
        "pool_size": hm["pool_size"], "passed_filters": hm["passed_filters"], "filtered_out": hm["filtered_out"],
        "matches": [{"name": by_id[m["candidate_id"]].get("name"), "profile": by_id[m["candidate_id"]].get("profile"),
                     "fit": m["fit"], "reasons": m["reasons"]} for m in hm["matches"]],
        "deal": {"successor": by_id[top["candidate_id"]].get("name"), "price": price,
                 "bank_loan": fin["bank_loan"], "vendor_loan": fin["vendor_loan"], "own_funds": fin["equity_needed"],
                 "owner_wealth_plan": fin["seller_receives_now"],
                 "phased_plan": phased_plan(hero, top["financing"]["own_funds"], price=price)},
    }

    files = {"companies.json": companies, "candidates.json": candidates, "radar.json": radar(companies),
             "matches.json": matches, "funnel.json": funnel, "demo_case.json": demo_case}
    for name, data in files.items():
        (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))

    print("Funnel:", funnel)
    print("\nTop 5 on the Readiness Radar:")
    for r in radar(companies, top=5):
        print(f"  {r['score']:>3}  {r['name']:<28} {r['region']:<16} {'; '.join(r['reasons'][:3])}")
    d = demo_case
    print(f"\nHero: {d['company']} ({d['owner']}, {d['owner_age']}), readiness {d['readiness']['score']}: "
          f"{'; '.join(d['readiness']['reasons'][:3])}")
    print(f"  Value €{d['value_range'][0]/1e6:.1f}M – €{d['value_range'][1]/1e6:.1f}M, EBITDA 2028 ~€{d['ebitda_2028_base']/1e3:.0f}k")
    print(f"  Pool {d['pool_size']} -> {d['passed_filters']} passed filters; filtered out: {d['filtered_out']}")
    for m in d["matches"]:
        print(f"  {m['fit']:>3}% {m['name']} ({m['profile']}): {'; '.join(m['reasons'][:3])}")
    x = d["deal"]
    print(f"  Deal with {x['successor']}: €{x['price']/1e6:.2f}M = KBC loan €{x['bank_loan']/1e6:.2f}M + "
          f"vendor €{x['vendor_loan']/1e6:.2f}M + own €{x['own_funds']/1e6:.2f}M; owner wealth plan €{x['owner_wealth_plan']/1e6:.1f}M")


if __name__ == "__main__":
    main()
