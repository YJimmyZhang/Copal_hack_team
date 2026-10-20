"""Readiness Radar: which owners are heading towards a succession they haven't planned?

Deliberately rule-based (no trained model): successions are rare and noisy, and a
wrong flag only costs a free readiness check. Every point comes with a reason the
relationship manager can read.
"""
from config import CURRENT_YEAR

# (points, test, reason text)
RULES = [
    (25, lambda c: c["owner_age"] >= 60, lambda c: f"Owner is {c['owner_age']}"),
    (12, lambda c: 55 <= c["owner_age"] < 60, lambda c: f"Owner is {c['owner_age']}"),
    (20, lambda c: not c["next_gen_in_shares"], lambda c: "No next generation among shareholders"),
    (15, lambda c: c["years_since_investment_loan"] >= 5,
         lambda c: f"No investment loan for {c['years_since_investment_loan']} years"),
    (10, lambda c: c["capex_trend"] <= -0.1, lambda c: "Investment spending is falling"),
    (10, lambda c: c["cash_buildup"] >= 0.2, lambda c: "Cash is piling up in the company"),
    (8,  lambda c: c["dividend_trend"] >= 0.08, lambda c: "Owner is taking out more dividends"),
    (5,  lambda c: c["owner_pension_saving_up"], lambda c: "Owner is saving more for pension"),
    (5,  lambda c: CURRENT_YEAR - c["founded_year"] >= 25,
         lambda c: f"Company is {CURRENT_YEAR - c['founded_year']} years old"),
]
MAX_POINTS = sum(r[0] for r in RULES)
THRESHOLD = 60   # score at which the relationship manager gets the case


def readiness(company):
    """Return score (0-100), level and the reasons that fired, strongest first."""
    hits = [(pts, why(company)) for pts, test, why in RULES if test(company)]
    hits.sort(reverse=True)
    score = round(100 * sum(p for p, _ in hits) / MAX_POINTS)
    level = "high" if score >= THRESHOLD else "medium" if score >= 40 else "low"
    return {"score": score, "level": level, "reasons": [r for _, r in hits]}


def radar(companies, top=25):
    """Ranked list for the relationship manager."""
    rows = []
    for c in companies:
        r = readiness(c)
        rows.append({"company_id": c["company_id"], "name": c["name"], "sector": c["sector"],
                     "region": c["region"], "employees": c["employees"], **r})
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:top]
