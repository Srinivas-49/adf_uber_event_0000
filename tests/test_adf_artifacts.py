import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "adf_uber_event_0000"

class TestPipeline(unittest.TestCase):
    def test_lookup_and_foreach(self):
        data = json.loads((ROOT / "pipeline/HTTP_to_ADLS.json").read_text())
        activities = {a["name"]: a for a in data["properties"]["activities"]}
        self.assertIn("Lookup1", activities)
        self.assertIn("foreachjson", activities)
        self.assertEqual(activities["foreachjson"]["type"], "ForEach")

    def test_parameterized_sink(self):
        data = json.loads((ROOT / "dataset/Json3.json").read_text())
        self.assertIn("parameters", data["properties"])

if __name__ == "__main__":
    unittest.main()
