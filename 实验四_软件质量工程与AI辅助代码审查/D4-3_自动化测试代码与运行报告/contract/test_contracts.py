import json
import unittest
from pathlib import Path


CONTRACT_DIR = Path(__file__).parent / "contracts"


class ContractVerifierTest(unittest.TestCase):
    def test_all_contract_files_are_valid_json(self):
        for path in CONTRACT_DIR.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("consumer", data)
            self.assertIn("provider", data)
            self.assertIn("response", data)

    def test_success_responses_define_required_fields(self):
        for path in CONTRACT_DIR.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            fields = data["response"]["required_fields"]
            self.assertGreaterEqual(len(fields), 4)
            self.assertEqual(len(fields), len(set(fields)))

    def test_error_schema_is_uniform(self):
        for path in CONTRACT_DIR.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["response"]["error_schema"], ["code", "message", "details"])

    def test_three_consumer_provider_pairs_exist(self):
        pairs = {
            (json.loads(p.read_text(encoding="utf-8"))["consumer"], json.loads(p.read_text(encoding="utf-8"))["provider"])
            for p in CONTRACT_DIR.glob("*.json")
        }
        self.assertEqual(len(pairs), 3)


if __name__ == "__main__":
    unittest.main()
