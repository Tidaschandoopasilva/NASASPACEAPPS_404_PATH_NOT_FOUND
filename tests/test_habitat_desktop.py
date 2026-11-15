"""Exercise the production mesh API through the habitat ledger."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.habitat import BASE_QUARTER, STOCK, measure
from app.main import app
from crew_link import fetch, start


class HabitatDesktopTests(unittest.TestCase):
    def test_expedition_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"MARS_HABITAT_DB": str(Path(directory) / "campaign.sqlite3")}
        ), TestClient(app) as client:
            request = {"center": [62, 35], "radius": 850}
            response = client.post("/api/v1/habitat/plan", json=request)
            self.assertEqual(response.status_code, 200, response.text[:600])
            plan = response.json()
            self.assertTrue(plan["uav_readings"])
            self.assertTrue(plan["ground_checks"])
            self.assertTrue(plan["after"]["path"])
            self.assertFalse(plan["habitat"]["rejections"])
            plan_id = plan["habitat"]["id"]
            self.assertEqual(client.get("/api/v1/habitat").json()["remaining"], STOCK)
            with start("127.0.0.1", 0, "test") as server:
                port = server.server_address[1]
                self.assertEqual(fetch("127.0.0.1", port, "wrong"), {"error":"Access denied"})
                draft = fetch("127.0.0.1", port, "test")["latest"]
                self.assertEqual(draft["state"], "SIMULATED DRAFT")
                self.assertFalse(draft["ground_checks"])
                self.assertEqual(client.post("/api/v1/habitat/record", json={"id":plan_id}).status_code,409)
                self.assertEqual(client.post("/api/v1/habitat/telemetry", json={
                    "id":plan_id,"progress":.7,"sequence":1}).status_code,409)
                self.assertTrue(client.post("/api/v1/habitat/start", json={"id":plan_id}).json()["started"])
                self.assertEqual(client.get("/api/v1/habitat").json()["expeditions"],0)
                reading = client.post("/api/v1/habitat/telemetry", json={
                    "id":plan_id, "progress":.7, "sequence":2}).json()
                self.assertGreater(reading["spent"]["oxygen_l"], 0)
                self.assertGreater(reading["spent"]["robot_wh"], 0)
                self.assertEqual(reading["remaining"]["oxygen_l"],
                                 round(STOCK["oxygen_l"]-reading["spent"]["oxygen_l"],3))
                client.post("/api/v1/habitat/telemetry", json={"id":plan_id,"progress":.3,"sequence":1})
                latest = fetch("127.0.0.1", port, "test")["latest"]
                self.assertEqual(latest["progress"], .7)
                self.assertTrue(latest["ground_checks"])
                self.assertEqual(client.post("/api/v1/habitat/advance", json={"revision":0}).status_code,409)
                final = client.post("/api/v1/habitat/telemetry",
                                    json={"id":plan_id,"progress":1,"sequence":3}).json()
                self.assertEqual(final["spent"],plan["habitat"]["cost"])
                record = client.post("/api/v1/habitat/record", json={"id":plan_id}).json()
                self.assertEqual(record["completed"], 1)
                self.assertTrue(record["atlas_sectors"])
                self.assertTrue(all(s["expedition"]==1 for s in record["atlas_sectors"]))
                for key, amount in plan["habitat"]["cost"].items():
                    self.assertAlmostEqual(record["remaining"][key], STOCK[key]-amount, places=3)
                self.assertEqual(client.post("/api/v1/habitat/record", json={"id":plan_id}).json(), record)
                self.assertEqual(fetch("127.0.0.1", port, "test")["latest"]["state"], "SIMULATED COMPLETE")
            base = client.post("/api/v1/habitat/advance", json={"revision":record["revision"]}).json()
            self.assertAlmostEqual(base["sol_elapsed"]-record["sol_elapsed"], .25)
            self.assertEqual(base["expeditions"], record["expeditions"])
            for key, amount in BASE_QUARTER.items():
                self.assertAlmostEqual(base["remaining"][key],record["remaining"][key]-amount)
            self.assertTrue(client.get(f"/api/v1/habitat/replay/{plan_id}").json()["habitat"]["recorded"])
            self.assertEqual(client.get("/api/v1/ml/evaluation").status_code, 200)

    def test_resource_shortage_explained(self):
        report = {"after":{"path":[[0,0],[1,0],[0,0]]},
                  "decision_audit": {"sorties": [{"sortie":1, "walking_minutes":35, "science_minutes":3}]}}
        _, reasons = measure(report, {"payload_kg":10, "budget":180},
                             {"dx_m":47, "dy_m":44}, {**STOCK,"oxygen_l":STOCK["oxygen_l"]*.20})
        self.assertTrue(any("Habitat oxygen_l" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
