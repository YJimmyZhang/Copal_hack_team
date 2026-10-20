"""The demo hero case: Bakkerij Peeters (owner Jan Peeters, 63) and its three candidates.

These are fixed fake records, so the engine's own scoring produces exactly the numbers
shown in demo/index.html and the slides:
readiness 78 · value €2.4M–€3.6M · EBITDA ~€620k by 2028 · matches 86 / 79 / 71 ·
price €3.0M = €1.95M KBC loan + €0.8M vendor loan + €0.25M own funds.
"""
from config import CURRENT_YEAR

YEARS = list(range(CURRENT_YEAR - 5, CURRENT_YEAR))          # 2021..2025
REVENUE_2025 = 4_500_000
GROWTH = 0.035

HERO_COMPANY = {
    "company_id": "C000",
    "name": "Bakkerij Peeters",
    "owner_name": "Jan Peeters",
    "sector": "food_production",
    "region": "Antwerp", "lat": 51.2194, "lon": 4.4025,
    "founded_year": 2010,
    "employees": 32,
    "revenue": {y: round(REVENUE_2025 / (1 + GROWTH) ** (2025 - y)) for y in YEARS},
    "ebitda": {2021: 495_000, 2022: 518_000, 2023: 540_000, 2024: 559_000, 2025: 578_000},
    "net_debt": 102_450,
    "owner_age": 63,
    "next_gen_in_shares": False,
    "years_since_investment_loan": 6,
    "capex_trend": -0.40,
    "cash_buildup": 0.22,
    "dividend_trend": 0.05,
    "owner_pension_saving_up": True,
    "opted_in": True,
    "wishes": {"keep_staff": True, "transition_months": 12, "timing_years": 2, "role_after_sale": "adviser",
               "allowed_types": ["experienced_manager", "staff_mbo", "search_funder", "strategic_buyer"],
               "allow_trial": True, "require_sector_experience": True},
}

HERO_CANDIDATES = [
    {"candidate_id": "K900", "alias": "Candidate 1", "name": "Sarah Maes", "type": "experienced_manager",
     "profile": "Ops manager, food", "source": "headhunter_brief",
     "region": "Antwerp", "lat": 51.300, "lon": 4.460, "max_distance_km": 80,
     "sectors": ["food_production"], "years_experience": 14, "management_experience": True,
     "own_funds": 250_000, "intends_keep_staff": True, "wanted_transition_months": 12,
     "preferred_employees": (10, 60), "values_score": 0.33, "skills_score": 0.60,
     "state": "ready", "open_to_interim": True},
    {"candidate_id": "K901", "alias": "Candidate 2", "name": "(own staff)", "type": "staff_mbo",
     "profile": "Own staff (MBO)", "source": "owner_invite",
     "region": "Antwerp", "lat": 51.228, "lon": 4.410, "max_distance_km": 30,
     "sectors": ["food_production"], "years_experience": 11, "management_experience": False,
     "own_funds": 300_000, "intends_keep_staff": True, "wanted_transition_months": 6,
     "preferred_employees": (10, 60), "values_score": 0.83, "skills_score": 0.80,
     "state": "qualified", "open_to_interim": False},
    {"candidate_id": "K902", "alias": "Candidate 3", "name": "(search fund)", "type": "search_funder",
     "profile": "Search fund", "source": "headhunter_brief",
     "region": "Flemish Brabant", "lat": 50.990, "lon": 4.520, "max_distance_km": 120,
     "sectors": ["food_production", "wholesale"], "years_experience": 9, "management_experience": True,
     "own_funds": 1_200_000, "intends_keep_staff": False, "wanted_transition_months": 12,
     "preferred_employees": (10, 80), "values_score": 0.15, "skills_score": 0.55,
     "state": "qualified", "open_to_interim": True},
]
