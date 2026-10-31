import copy
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import roadmap


class TestRoadmap(unittest.TestCase):
    def test_generated_file_is_current(self):
        self.assertEqual(roadmap.OUTPUT.read_text(encoding="utf-8"), roadmap.render())

    def test_metrics_are_live(self):
        doc = roadmap.snapshot()
        values = {m["id"]: m["value"] for m in doc["metrics"]}
        self.assertEqual(values, roadmap.metric_values())
        self.assertEqual(values["solved"], len(json.loads((ROOT / "data/solved.json").read_text())))
        self.assertIsNone(next(m for m in doc["metrics"] if m["id"] == "solved")["target"])
        self.assertEqual(sum(doc["counts"].values()), len(doc["items"]))

    def _broken(self, mutate):
        doc = json.loads(roadmap.SOURCE.read_text(encoding="utf-8"))
        mutate(doc)
        original = roadmap.SOURCE.read_text
        text = json.dumps(doc)
        with mock.patch.object(type(roadmap.SOURCE), "read_text",
                               lambda self, **k: text if self == roadmap.SOURCE else original.__func__(self, **k)):
            with self.assertRaises(roadmap.RoadmapError):
                roadmap.load()

    def test_rejects_bad_items(self):
        def first(doc, key, value):
            doc["items"][0][key] = value
        self._broken(lambda d: first(d, "evidence", "missing/file.md"))
        self._broken(lambda d: first(d, "track", "nope"))
        self._broken(lambda d: first(d, "horizon", "someday"))
        self._broken(lambda d: first(d, "problems", ["M999"]))
        self._broken(lambda d: d["items"].append(copy.deepcopy(d["items"][0])))
        self._broken(lambda d: next(i for i in d["items"] if i["horizon"] == "now").pop("exit"))
        self._broken(lambda d: d["metrics"].append({"id": "made_up", "label": "x", "baseline": 0,
                                                     "target": 1, "unit": "x"}))


if __name__ == "__main__":
    unittest.main()
