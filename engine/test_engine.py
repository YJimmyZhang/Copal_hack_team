"""Tests for the Next Owner engine. Standard library only.

Run from the engine folder:  python -m unittest -v
"""
import copy
import unittest

from config import FINANCING
from data_gen import make_candidates, make_companies
from hero import HERO_CANDIDATES, HERO_COMPANY
from matching import score_pair, top_matches
from readiness import MAX_POINTS, THRESHOLD, readiness
from valuation import financing_check, phased_plan, split_price, value_range


def hero():
    return copy.deepcopy(HERO_COMPANY)


class TestReadiness(unittest.TestCase):
    def test_score_is_between_0_and_100_with_reasons(self):
        for c in make_companies(n=100):
            r = readiness(c)
            self.assertGreaterEqual(r["score"], 0)
            self.assertLessEqual(r["score"], 100)
            # every point comes with a reason, so a non-zero score always has reasons
            if r["score"] > 0:
                self.assertTrue(r["reasons"])

    def test_older_owner_without_heir_scores_higher(self):
        young = dict(hero(), owner_age=40, next_gen_in_shares=True)
        self.assertGreater(readiness(hero())["score"], readiness(young)["score"])

    def test_threshold_is_reachable(self):
        self.assertLess(THRESHOLD, 100)
        self.assertGreater(MAX_POINTS, 0)


class TestValuationAndFinancing(unittest.TestCase):
    def test_value_range_is_ordered(self):
        for c in make_companies(n=100) + [hero()]:
            v = value_range(c)
            self.assertLessEqual(v["equity_low"], v["equity_mid"])
            self.assertLessEqual(v["equity_mid"], v["equity_high"])

    def test_price_split_adds_up_and_respects_limits(self):
        f = FINANCING
        for c in make_companies(n=100) + [hero()]:
            price = value_range(c)["equity_mid"]
            if price <= 0:
                continue
            bank, vendor, own = split_price(c, price)
            self.assertAlmostEqual(bank + vendor + own, price, delta=1)
            self.assertLessEqual(bank, f["max_bank_share"] * price + 1000)
            self.assertLessEqual(vendor, f["max_vendor_share"] * price + 1)
            self.assertGreaterEqual(own, f["min_own_share"] * price - 1000)

    def test_financing_ok_only_when_own_funds_cover_the_gap(self):
        c = hero()
        need = financing_check(c, 0, 3_000_000)["equity_needed"]
        self.assertTrue(financing_check(c, need, 3_000_000)["ok"])
        self.assertFalse(financing_check(c, need - 1, 3_000_000)["ok"])

    def test_phased_plan_adds_up_to_the_full_deal(self):
        plan = phased_plan(hero(), 250_000, price=3_000_000)
        bought = [s for s in plan["steps"] if s["share"] > 0]
        self.assertAlmostEqual(sum(s["share"] for s in bought), 1.0)
        self.assertAlmostEqual(sum(s["price"] for s in bought), 3_000_000, delta=1000)


class TestMatching(unittest.TestCase):
    def setUp(self):
        self.company = hero()
        self.pool = [copy.deepcopy(k) for k in HERO_CANDIDATES] + make_candidates()

    def test_fit_is_the_lower_of_both_views(self):
        for k in self.pool:
            s = score_pair(self.company, k)
            if "blocked" not in s:
                self.assertEqual(s["fit"], min(s["owner_view"], s["candidate_view"]))

    def test_blocked_candidates_never_appear_in_results(self):
        res = top_matches(self.company, self.pool, n=50)
        blocked = {k["candidate_id"] for k in self.pool if "blocked" in score_pair(self.company, k)}
        self.assertFalse(blocked & {m["candidate_id"] for m in res["matches"]})
        self.assertEqual(res["passed_filters"] + sum(res["filtered_out"].values()), len(self.pool))

    def test_matches_are_sorted_and_explained(self):
        res = top_matches(self.company, self.pool, n=10)
        fits = [m["fit"] for m in res["matches"]]
        self.assertEqual(fits, sorted(fits, reverse=True))
        for m in res["matches"]:
            self.assertTrue(m["reasons"])
            self.assertTrue(m["financing"]["ok"])

    def test_owner_wishes_are_respected(self):
        for m in top_matches(self.company, self.pool, n=50)["matches"]:
            self.assertIn(m["type"], self.company["wishes"]["allowed_types"])


class TestHeroCaseMatchesTheDemo(unittest.TestCase):
    """The numbers shown in demo/index.html must come out of the engine."""

    def test_demo_numbers(self):
        c = hero()
        self.assertEqual(readiness(c)["score"], 78)
        v = value_range(c)
        self.assertEqual((round(v["equity_low"] / 1e5) / 10, round(v["equity_high"] / 1e5) / 10), (2.4, 3.6))
        pool = [copy.deepcopy(k) for k in HERO_CANDIDATES] + make_candidates()
        self.assertEqual([m["fit"] for m in top_matches(c, pool)["matches"]], [86, 79, 71])
        fin = financing_check(c, 250_000, 3_000_000)
        self.assertEqual((fin["bank_loan"], fin["vendor_loan"], fin["equity_needed"]), (1_950_000, 800_000, 250_000))


if __name__ == "__main__":
    unittest.main()
