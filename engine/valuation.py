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


def split_price(c, price):
    """Split a price into KBC loan + vendor loan + buyer's own funds."""
    f = FINANCING
    bank = round(min(max_acquisition_loan(c), f["max_bank_share"] * price), -3)
    room = price - bank - f["min_own_share"] * price
    vendor = max(0, min(f["max_vendor_share"] * price, room))
    vendor = vendor // f["vendor_round"] * f["vendor_round"]
    own = max(0, price - bank - vendor)
    return bank, vendor, own


def financing_check(c, own_funds, price=None):
    """Can a buyer with `own_funds` finance this company at `price` (default: mid value)?"""
    price = price or value_range(c)["equity_mid"]
    bank, vendor, own = split_price(c, price)
    return {"price": price, "bank_loan": bank, "vendor_loan": vendor, "equity_needed": own,
            "own_funds": own_funds, "ok": own_funds >= own, "seller_receives_now": price - vendor}


def phased_plan(c, own_funds, minority_share=0.3, trial_months=9, price=None):
    """'Try before you buy': interim trial -> minority stake -> full takeover.

    The price is locked at the start, so the interim manager has no incentive
    to push results down before buying.
    """
    locked_price = price or value_range(c)["equity_mid"]
    steps = [{"step": "Interim trial", "months": trial_months, "share": 0.0,
              "what": "Candidate runs the company as interim managing director, with a purchase "
                      "option at the locked price. Either side can stop at the end."}]
    remaining_own = own_funds
    for name, share in (("Minority stake", minority_share), ("Full takeover", 1 - minority_share)):
        part = locked_price * share
        bank, vendor, own = split_price(c, locked_price)
        step = {"step": name, "share": share, "price": round(part, -3), "bank_loan": round(bank * share, -3),
                "vendor_loan": round(vendor * share, -3), "equity_needed": round(own * share, -3)}
        step["ok"] = remaining_own >= step["equity_needed"]
        remaining_own -= step["equity_needed"]
        steps.append(step)
    return {"locked_price": locked_price, "steps": steps, "ok": all(s.get("ok", True) for s in steps)}


def company_view(c):
    return {"valuation": value_range(c), "projections": projections(c),
            "max_acquisition_loan": max_acquisition_loan(c)}
