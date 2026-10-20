"""Valuation & Projections: an INDICATIVE value range, a 3-year outlook and a financing check.

Shown to the owner as "indicative, to be confirmed by KBC's paid valuation".
"""
from config import FINANCING, SECTORS


def normalised_ebitda(c):
    last3 = sorted(c["ebitda"])[-3:]
    return sum(c["ebitda"][y] for y in last3) / 3


def value_range(c):
    """Equity value range = EV (sector multiple x normalised EBITDA) minus net debt."""
    e = normalised_ebitda(c)
    lo_m, hi_m = SECTORS[c["sector"]]["multiple"]
    low = max(0, lo_m * e - c["net_debt"])
    high = max(0, hi_m * e - c["net_debt"])
    return {"ebitda_normalised": round(e), "multiple_range": [lo_m, hi_m],
            "equity_low": round(low, -3), "equity_mid": round((low + high) / 2, -3), "equity_high": round(high, -3)}


def projections(c, years=3):
    """Revenue/EBITDA outlook from the historical growth rate, with a low/base/high band."""
    ys = sorted(c["revenue"])
    first, last = c["revenue"][ys[0]], c["revenue"][ys[-1]]
    cagr = (last / first) ** (1 / (len(ys) - 1)) - 1
    cagr = max(-0.05, min(0.08, cagr))                     # keep it sober
    margin = normalised_ebitda(c) / last
    out = []
    for k in range(1, years + 1):
        y = ys[-1] + k
        row = {"year": y}
        for name, g in (("low", cagr - 0.03), ("base", cagr), ("high", cagr + 0.03)):
            row[f"revenue_{name}"] = round(last * (1 + g) ** k, -3)
        row["ebitda_base"] = round(row["revenue_base"] * margin, -3)
        out.append(row)
    return {"historical_growth": round(cagr, 3), "outlook": out}


def max_acquisition_loan(c):
    """Loan the company's own EBITDA can carry: min(leverage cap, debt-service cap)."""
    e = normalised_ebitda(c)
    f = FINANCING
    r, n = f["interest_rate"], f["loan_years"]
    annuity_factor = r / (1 - (1 + r) ** -n)               # yearly payment per euro borrowed
    by_dscr = (e / f["min_dscr"]) / annuity_factor
    by_leverage = f["max_leverage"] * e
    return round(max(0, min(by_dscr, by_leverage)), -3)


def financing_check(c, own_funds, price=None):
    """Can a buyer with `own_funds` finance this company at `price` (default: mid value)?"""
    price = price or value_range(c)["equity_mid"]
    loan = min(max_acquisition_loan(c), price)
    vendor = round(FINANCING["vendor_loan_share"] * price, -3)
    gap = max(0, price - loan - vendor)
    return {"price": price, "bank_loan": loan, "vendor_loan": vendor, "equity_needed": gap,
            "own_funds": own_funds, "ok": own_funds >= gap}


def company_view(c):
    return {"valuation": value_range(c), "projections": projections(c),
            "max_acquisition_loan": max_acquisition_loan(c)}
