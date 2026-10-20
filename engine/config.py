"""Shared settings for the KBC Next Owner demo engine.

All numbers here are ILLUSTRATIVE assumptions for a hackathon demo,
not KBC figures. Replace them with KBC's real rules of thumb if a mentor
gives them to you.
"""

# Sector table: EV/EBITDA multiple range (low, high), typical EBITDA margin,
# and "related" sectors (a buyer from a related sector is a partial fit).
SECTORS = {
    "joinery":        {"label": "Joinery & carpentry",     "multiple": (4.0, 5.5), "margin": 0.11, "related": ["construction"]},
    "construction":   {"label": "Construction",            "multiple": (4.0, 5.5), "margin": 0.09, "related": ["joinery", "installation"]},
    "installation":   {"label": "HVAC & installation",     "multiple": (4.5, 6.0), "margin": 0.10, "related": ["construction"]},
    "wholesale":      {"label": "Wholesale",               "multiple": (4.5, 6.0), "margin": 0.06, "related": ["transport", "retail"]},
    "retail":         {"label": "Retail",                  "multiple": (3.5, 5.0), "margin": 0.07, "related": ["wholesale"]},
    "transport":      {"label": "Transport & logistics",   "multiple": (4.0, 5.5), "margin": 0.08, "related": ["wholesale"]},
    "manufacturing":  {"label": "Manufacturing",           "multiple": (5.0, 7.0), "margin": 0.12, "related": ["installation", "wholesale"]},
    "it_services":    {"label": "IT services",             "multiple": (6.0, 9.0), "margin": 0.15, "related": ["business_services"]},
    "business_services": {"label": "Business services",    "multiple": (5.0, 7.0), "margin": 0.14, "related": ["it_services"]},
    "horeca":         {"label": "Hospitality",             "multiple": (3.0, 4.5), "margin": 0.08, "related": ["retail"]},
    # Used only by the demo hero case (Bakkerij Peeters), not by the random data.
    "food_production": {"label": "Food production",        "multiple": (4.5, 6.6), "margin": 0.12, "related": ["retail", "horeca", "wholesale"]},
}
RANDOM_SECTORS = [s for s in SECTORS if s != "food_production"]

# Province centroids (lat, lon) for distance calculations.
REGIONS = {
    "Antwerp":          (51.22, 4.40),
    "East Flanders":    (51.05, 3.72),
    "West Flanders":    (51.05, 3.10),
    "Flemish Brabant":  (50.88, 4.70),
    "Limburg":          (50.93, 5.33),
    "Brussels":         (50.85, 4.35),
}

CANDIDATE_TYPES = ["experienced_manager", "search_funder", "staff_mbo", "strategic_buyer", "start_it_founder"]

# Financing assumptions (illustrative).
# Price = KBC acquisition loan + vendor loan (seller) + buyer's own funds.
FINANCING = {
    "max_leverage": 3.5,          # acquisition loan <= 3.5x normalised EBITDA
    "loan_years": 7,
    "interest_rate": 0.05,
    "min_dscr": 1.3,              # EBITDA must cover yearly debt service 1.3x
    "max_bank_share": 0.65,       # KBC finances at most 65% of the price
    "max_vendor_share": 0.30,     # seller leaves at most 30% as a (subordinated) vendor loan
    "min_own_share": 0.08,        # buyer always brings at least 8% of the price in cash
    "vendor_round": 50_000,       # vendor loan rounded down to a clean amount
}

CURRENT_YEAR = 2026
SEED = 42
