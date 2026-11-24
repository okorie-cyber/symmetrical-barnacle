import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import audit  # noqa: E402

P = {"id": "1", "business": "Westex Roofing", "aliases": "Westex", "website": "westexroofing.com", "notes": ""}
GENERIC = {"id": "2", "business": "Helping Hands Heating & Cooling", "aliases": "Helping Hands",
           "website": "helpinghandsair.com", "notes": "generic name - match on domain only"}


class Matching(unittest.TestCase):
    def test_domain_in_sources_is_high(self):
        r = audit.match_business(P, "Try these roofers.", ["Westex https://www.westexroofing.com/about"])
        self.assertEqual(r["confidence"], "high")

    def test_name_in_text_is_medium(self):
        r = audit.match_business(P, "1. **Westex Roofing** - family owned", [])
        self.assertTrue(r["named"])
        self.assertEqual(r["confidence"], "medium")

    def test_no_partial_word_match(self):
        self.assertFalse(audit.match_business(P, "Westexas Roofing Group is popular", [])["named"])

    def test_generic_name_needs_domain(self):
        text = "Helping Hands Heating & Cooling is great"
        self.assertFalse(audit.match_business(GENERIC, text, [])["named"])
        self.assertTrue(audit.match_business(GENERIC, text, ["helpinghandsair.com"])["named"])

    def test_name_made_only_of_generic_words_never_text_matches(self):
        p = {**P, "business": "Roofing Services Co", "aliases": "", "website": ""}
        self.assertFalse(audit.match_business(p, "Roofing Services Co is good", [])["named"])

    def test_extract_names(self):
        names = audit.extract_names("1. **Lone Star Pros** - great\n2. Blue Line Roofing: fast")
        self.assertIn("Lone Star Pros", names)
        self.assertIn("Blue Line Roofing", names)


class EndToEnd(unittest.TestCase):
    def test_mock_and_manual_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            pros = d / "p.csv"
            with open(pros, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["id", "business", "trade", "city", "state", "metro", "website", "aliases", "notes"])
                w.writeheader()
                w.writerow({"id": "1", "business": "Westex Roofing", "trade": "roofer", "city": "Fort Worth", "state": "TX",
                            "metro": "DFW", "website": "westexroofing.com", "aliases": "", "notes": ""})
                w.writerow({"id": "2", "business": "Dominion Roof Systems", "trade": "roofer", "city": "Fort Worth", "state": "TX",
                            "metro": "DFW", "website": "dominionroofsystems.com", "aliases": "", "notes": ""})
            run = [sys.executable, str(HERE / "audit.py")]
            subprocess.run(run + ["prompts", "--prospects", str(pros), "--runs", "1", "--out", str(d / "sheet.csv")], check=True)
            rows = list(csv.DictReader(open(d / "sheet.csv")))
            self.assertEqual(len(rows), 8)
            rows[0].update(engine="chatgpt_app", answer="Top picks: **Dominion Roof Systems** and others",
                           sources="https://dominionroofsystems.com")
            with open(d / "sheet.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
            subprocess.run(run + ["run", "--engine", "manual", "--prospects", str(pros), "--input", str(d / "sheet.csv"),
                                  "--out", str(d / "manual.json")], check=True)
            subprocess.run(run + ["run", "--engine", "mock", "--prospects", str(pros), "--runs", "1", "--out", str(d / "mock.json")],
                           check=True, capture_output=True)
            self.assertEqual(len(json.load(open(d / "manual.json"))), 1)
            subprocess.run(run + ["report", "--prospects", str(pros), "--evidence", str(d / "manual.json"),
                                  "--outdir", str(d / "r")], check=True, capture_output=True)
            westex = (d / "r" / "1-westex-roofing.html").read_text()
            self.assertIn("0 of 1", westex)              # Westex not named
            self.assertIn("Dominion Roof Systems - named 1", westex)  # rival detected
            self.assertNotIn("SAMPLE DATA", westex)
            subprocess.run(run + ["report", "--prospects", str(pros), "--evidence", str(d / "mock.json"),
                                  "--outdir", str(d / "m")], check=True, capture_output=True)
            self.assertIn("SAMPLE DATA", (d / "m" / "1-westex-roofing.html").read_text())


if __name__ == "__main__":
    unittest.main()
