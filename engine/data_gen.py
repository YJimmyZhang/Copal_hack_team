"""Generate fake but realistic demo data: SME companies (with owners) and successor candidates.

No real customer data is used anywhere in this project.
"""
import random

import numpy as np

from config import CANDIDATE_TYPES, CURRENT_YEAR, REGIONS, SECTORS, SEED

FAMILY_NAMES = ["Peeters", "Janssens", "Maes", "Jacobs", "Mertens", "Willems", "Claes", "Goossens",
                "Wouters", "De Smet", "Dubois", "Lambert", "Vermeulen", "Hermans", "Aerts", "Pauwels",
                "Van Damme", "De Clercq", "Martens", "Desmet"]
SECTOR_WORD = {"joinery": "Schrijnwerkerij", "construction": "Bouw", "installation": "Installaties",
               "wholesale": "Groothandel", "retail": "Winkel", "transport": "Transport",
               "manufacturing": "Metaal", "it_services": "IT", "business_services": "Consult",
               "horeca": "Brasserie"}


def _point_in(region, rng):
    lat, lon = REGIONS[region]
    return round(lat + rng.uniform(-0.15, 0.15), 4), round(lon + rng.uniform(-0.2, 0.2), 4)


def make_companies(n=300, seed=SEED):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    companies = []
    for i in range(1, n + 1):
        sector = rng.choice(list(SECTORS))
        region = rng.choice(list(REGIONS))
        lat, lon = _point_in(region, rng)
        employees = int(np.clip(np_rng.lognormal(2.2, 0.7), 2, 120))
        revenue_2025 = employees * rng.uniform(110_000, 220_000)
        growth = rng.gauss(0.02, 0.04)                      # yearly revenue growth
        margin = max(0.02, rng.gauss(SECTORS[sector]["margin"], 0.03))
        years = list(range(CURRENT_YEAR - 5, CURRENT_YEAR))  # 2021..2025
        revenue = {y: round(revenue_2025 / (1 + growth) ** (2025 - y) * rng.uniform(0.97, 1.03)) for y in years}
        ebitda = {y: round(revenue[y] * margin * rng.uniform(0.9, 1.1)) for y in years}

        owner_age = int(np.clip(rng.gauss(55, 9), 32, 75))
        founded = CURRENT_YEAR - rng.randint(5, 45)
        older = owner_age >= 58
        companies.append({
            "company_id": f"C{i:03d}",
            "name": f"{rng.choice(FAMILY_NAMES)} {SECTOR_WORD[sector]}",
            "sector": sector,
            "region": region,
            "lat": lat, "lon": lon,
            "founded_year": founded,
            "employees": employees,
            "revenue": revenue,
            "ebitda": ebitda,
            "net_debt": round(revenue_2025 * rng.uniform(-0.15, 0.25)),   # negative = net cash
            # Owner and behaviour signals
            "owner_age": owner_age,
            "next_gen_in_shares": rng.random() < (0.25 if older else 0.4),
            "years_since_investment_loan": rng.randint(4, 12) if (older and rng.random() < 0.7) else rng.randint(0, 5),
            "capex_trend": round(rng.gauss(-0.15 if older else 0.03, 0.1), 2),        # yearly change in investment
            "cash_buildup": round(max(0, rng.gauss(0.25 if older else 0.08, 0.1)), 2),  # cash as share of revenue
            "dividend_trend": round(rng.gauss(0.10 if older else 0.0, 0.08), 2),
            "owner_pension_saving_up": rng.random() < (0.7 if older else 0.3),
            # Filled in only when the owner opts in (step 3 "Explore")
            "opted_in": False,
            "wishes": None,
        })
    # Some older owners have opted in and set wishes, so the matching demo has cases.
    older_ids = [c for c in companies if c["owner_age"] >= 58 and not c["next_gen_in_shares"]]
    for c in rng.sample(older_ids, k=min(12, len(older_ids))):
        c["opted_in"] = True
        c["wishes"] = {
            "keep_staff": rng.random() < 0.8,
            "transition_months": rng.choice([6, 12, 18, 24]),
            "allowed_types": rng.sample(CANDIDATE_TYPES, k=rng.randint(3, 5)),
            "timing_years": rng.choice([1, 2, 3]),
        }
    return companies


def headhunter_sourced(company, k=4, seed=SEED + 2):
    """Step 4 'Search': the headhunter sources candidates for ONE anonymised brief
    (same or related sector, nearby). Returns new candidate records."""
    rng = random.Random(f"{seed}-{company['company_id']}")
    out = []
    for j in range(k):
        sector = company["sector"] if rng.random() < 0.7 else rng.choice(SECTORS[company["sector"]]["related"])
        lat, lon = company["lat"] + rng.uniform(-0.3, 0.3), company["lon"] + rng.uniform(-0.3, 0.3)
        ctype = rng.choice(["experienced_manager", "search_funder", "strategic_buyer"])
        out.append({
            "candidate_id": f"H{company['company_id'][1:]}{j}",
            "alias": f"Candidate H{company['company_id'][1:]}{j}",
            "type": ctype, "source": "headhunter_brief",
            "region": company["region"], "lat": round(lat, 4), "lon": round(lon, 4),
            "max_distance_km": rng.choice([50, 80, 120]),
            "sectors": [sector], "years_experience": rng.randint(8, 25),
            "management_experience": True,
            "own_funds": round(rng.uniform(150_000, 900_000), -3),
            "intends_keep_staff": rng.random() < 0.85,
            "wanted_transition_months": rng.choice([6, 12, 18]),
            "preferred_employees": (2, 60),
            "values_score": round(rng.uniform(0.6, 1.0), 2),
            "skills_score": round(rng.uniform(0.6, 1.0), 2),
            "state": rng.choice(["qualified", "ready"]),
        })
    return out


def make_candidates(n=80, seed=SEED + 1):
    rng = random.Random(seed)
    candidates = []
    for i in range(1, n + 1):
        ctype = rng.choices(CANDIDATE_TYPES, weights=[35, 10, 15, 25, 15])[0]
        region = rng.choice(list(REGIONS))
        lat, lon = _point_in(region, rng)
        main_sector = rng.choice(list(SECTORS))
        own_funds = {"experienced_manager": (80_000, 400_000), "search_funder": (300_000, 1_500_000),
                     "staff_mbo": (30_000, 150_000), "strategic_buyer": (400_000, 3_000_000),
                     "start_it_founder": (20_000, 150_000)}[ctype]
        candidates.append({
            "candidate_id": f"K{i:03d}",
            "alias": f"Candidate {i:03d}",
            "type": ctype,
            "source": {"experienced_manager": "headhunter", "search_funder": "headhunter",
                       "staff_mbo": "owner_invite", "strategic_buyer": "relationship_manager",
                       "start_it_founder": "start_it"}[ctype],
            "region": region, "lat": lat, "lon": lon,
            "max_distance_km": rng.choice([30, 50, 80, 120]),
            "sectors": [main_sector] + ([rng.choice(SECTORS[main_sector]["related"])] if rng.random() < 0.5 else []),
            "years_experience": rng.randint(3, 30),
            "management_experience": rng.random() < (0.85 if ctype != "start_it_founder" else 0.3),
            "own_funds": round(rng.uniform(*own_funds), -3),
            "intends_keep_staff": rng.random() < 0.75,
            "wanted_transition_months": rng.choice([3, 6, 12, 18]),
            "preferred_employees": (rng.choice([3, 5, 10]), rng.choice([20, 40, 80])),
            # Ready-to-Own track: assessment results (0..1) and pipeline state
            "values_score": round(rng.uniform(0.4, 1.0), 2),
            "skills_score": round(rng.uniform(0.4, 1.0), 2),
            "state": rng.choices(["curious", "qualified", "ready"], weights=[30, 45, 25])[0],
        })
    return candidates
