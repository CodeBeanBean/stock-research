"""Cross-check source columns, scenario calculations and rounding boundaries."""
import copy
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE))
import monitor


class ValuationTests(unittest.TestCase):
    def snapshot(self, pool, prices):
        quotes = {
            stock["quote_sym"]: {
                "latest_price": price,
                "today_change_pct": 0,
                "quote_time": "20261013135000",
            }
            for stock, price in zip(pool, prices)
        }
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "cache"
            with patch.object(monitor, "STOCKS_POOL", pool), \
                 patch.object(monitor, "load_stocks_pool", return_value=pool) as load_pool, \
                 patch.object(monitor, "MODULE_DIR", directory), \
                 patch.object(monitor, "CACHE_DIR", str(cache)), \
                 patch.object(monitor, "SNAPSHOT_FILE", str(cache / "quotes.json")), \
                 patch.object(monitor, "fetch_raw_quotes", return_value=quotes):
                result = monitor.get_market_snapshot(excluded_codes=[])
                load_pool.assert_called_once_with()
                return result

    def test_all_source_columns_match_by_header(self):
        lines = (MODULE.parent / "stock-overview.md").read_text(encoding="utf-8").splitlines()
        table = [line for line in lines if line.startswith("|")]
        headers = [cell.strip() for cell in table[0].strip("|").split("|")]
        source = {}
        for line in table[2:]:
            row = dict(zip(headers, [cell.strip() for cell in line.strip("|").split("|")]))
            source[row["公司"]] = row
        pool = monitor.load_stocks_pool()
        self.assertEqual(set(source), {item["company"] for item in pool})
        for item in pool:
            for scenario in ("bear", "base", "bull"):
                expected = float(re.search(r"[\d.]+", source[item["company"]][scenario.title()]).group())
                self.assertEqual(item[scenario], expected, (item["company"], scenario))

    def test_unchanged_price_has_zero_space_change_for_all_companies(self):
        pool = monitor.load_stocks_pool()
        result = self.snapshot(pool, [item["base_price"] for item in pool])
        for item in result["items"]:
            self.assertEqual(item["delta_upside"], 0, item["company"])
            self.assertEqual(item["delta_upside_str"], "+0.0 个百分点")
        self.assertEqual(result["kpis"]["expanded_count"], 0)
        self.assertEqual(result["kpis"]["compressed_count"], 0)

    def test_distinct_scenarios_and_prices_above_bull(self):
        stock = copy.deepcopy(monitor.STOCKS_POOL[0])
        stock.update(base_price=100, bear=80, base=120, bull=160, report_upside=19.9)
        for price in (100, 200):
            item = self.snapshot([stock], [price])["items"][0]
            self.assertEqual(item["report_upside"], 20)
            for scenario, target in (("bear", 80), ("base", 120), ("bull", 160)):
                expected = (target - price) / price * 100
                self.assertAlmostEqual(item[f"dynamic_{scenario}_upside"], expected)
            self.assertAlmostEqual(item["delta_upside"], (120 - price) / price * 100 - 20)
            if price == 200:
                self.assertEqual(item["dynamic_bull_upside_str"], "-20.0%")


if __name__ == "__main__":
    unittest.main()
