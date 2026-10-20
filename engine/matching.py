"""Match Engine: two-sided matching between an opted-in owner and the candidate pool.

1. Hard filters (deal-breakers)   2. Owner's view of the candidate
3. Candidate's view of the company   4. Fit = the LOWER of the two (both must like it)
5. Plain-language reasons + financing check
"""
import math

from config import SECTORS
from valuation import financing_check, phased_plan


def distance_km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def sector_fit(company, cand):
    if company["sector"] in cand["sectors"]:
        return 1.0
    if any(s in SECTORS[company["sector"]]["related"] for s in cand["sectors"]):
        return 0.5
    return 0.1


def hard_filters(company, cand, fin, dist):
    w = company["wishes"]
    if cand["type"] not in w["allowed_types"]:
        return "Owner excluded this type of successor"
    if cand["state"] == "curious":
        return "Candidate not yet qualified"
    if dist > cand["max_distance_km"]:
        return f"Too far ({dist:.0f} km)"
    if not fin["ok"]:
        return "Financing gap too large"
    if w.get("require_sector_experience") and sector_fit(company, cand) < 1.0:
        return "No experience in this sector"
    return None


def score_pair(company, cand):
    dist = distance_km(company, cand)
    fin = financing_check(company, cand["own_funds"])
    blocked = hard_filters(company, cand, fin, dist)
    if blocked:
        return {"candidate_id": cand["candidate_id"], "blocked": blocked}

    w = company["wishes"]
    sf = sector_fit(company, cand)
    staff_ok = (not w["keep_staff"]) or cand["intends_keep_staff"]
    transition_ok = abs(w["transition_months"] - cand["wanted_transition_months"]) <= 6

    trial = bool(w.get("allow_trial")) and bool(cand.get("open_to_interim"))
    owner_view = (0.30 * sf + 0.15 * cand["management_experience"] + 0.20 * cand["values_score"]
                  + 0.15 * cand["skills_score"] + 0.10 * staff_ok + 0.10 * transition_ok)
    if trial:  # both open to "try before you buy": lower risk for the owner
        owner_view = min(1.0, owner_view + 0.05)
    lo, hi = cand["preferred_employees"]
    size_ok = lo <= company["employees"] <= hi
    cand_view = (0.35 * sf + 0.25 * (1 - dist / cand["max_distance_km"]) + 0.20 * size_ok
                 + 0.20 * min(1, cand["own_funds"] / max(1, fin["equity_needed"] * 1.5)))
    fit = min(owner_view, cand_view)

    reasons = []
    if sf == 1.0:
        reasons.append(f"Experience in {SECTORS[company['sector']]['label'].lower()}")
    elif sf == 0.5:
        reasons.append("Experience in a related sector")
    reasons.append(f"{dist:.0f} km away")
    reasons.append(f"Financing OK: €{fin['equity_needed']:,.0f} own funds needed, has €{cand['own_funds']:,.0f}")
    if w["keep_staff"] and cand["intends_keep_staff"]:
        reasons.append("Plans to keep all staff")
    if transition_ok:
        reasons.append(f"Agrees with a ~{w['transition_months']}-month handover")
    if cand["state"] == "ready":
        reasons.append("Completed the Ready-to-Own track")
    if trial:
        reasons.append("Both open to a 6-12 month interim trial before buying")
    confidence = "high" if fit >= 0.7 else "medium" if fit >= 0.55 else "low (send to relationship manager)"
    return {"candidate_id": cand["candidate_id"], "alias": cand["alias"], "type": cand["type"],
            "fit": round(fit * 100), "owner_view": round(owner_view * 100), "candidate_view": round(cand_view * 100),
            "confidence": confidence, "reasons": reasons, "financing": fin,
            "trial_possible": trial,
            "phased_plan": phased_plan(company, cand["own_funds"]) if trial else None}


def top_matches(company, candidates, n=3):
    scored = [score_pair(company, c) for c in candidates]
    ok = sorted([s for s in scored if "blocked" not in s], key=lambda s: s["fit"], reverse=True)
    blocked = {}
    for s in scored:
        if "blocked" in s:
            blocked[s["blocked"].split(" (")[0]] = blocked.get(s["blocked"].split(" (")[0], 0) + 1
    return {"company_id": company["company_id"], "pool_size": len(candidates), "passed_filters": len(ok),
            "filtered_out": blocked, "matches": ok[:n]}
