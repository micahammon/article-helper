import json
import unittest
from pathlib import Path


class TestRulesMapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rules_path = Path(__file__).resolve().parents[1] / "rules_data.json"
        cls.data = json.loads(rules_path.read_text(encoding="utf-8"))

    def test_institution_prompt_separates_bed_home_work(self):
        node = self.data["decision_tree"]["institution_type_check"]
        details = node.get("details", "")
        self.assertIn("Bed/home/work", details)

        options = node.get("options", {})
        self.assertIn("Yes, it is (school, church, hospital, prison, university)", options)
        self.assertIn("No, it's a different kind of institution (e.g., government, company, museum)", options)

    def test_lookup_context_caveats_for_communication(self):
        lookup = self.data["lookup_table"]
        self.assertIn("by radio", lookup["radio"]["explanation"])
        self.assertIn("by phone", lookup["phone"]["explanation"])
        self.assertIn("by post", lookup["post"]["explanation"])

    def test_lookup_context_caveats_for_special_nouns(self):
        lookup = self.data["lookup_table"]
        self.assertIn("physical object", lookup["bed"]["explanation"])
        self.assertIn("building/house", lookup["home"]["explanation"])
        self.assertIn("job/task", lookup["work"]["explanation"])


if __name__ == "__main__":
    unittest.main()
