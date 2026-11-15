import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from fastapi.testclient import TestClient

from app.environment import outfit
from app.habitat import crew_use
from app.mission_qa import answer
from app.main import app
from app.survey_atlas import summarize


class HabitatV5Tests(unittest.TestCase):
    def test_thermal_resource_and_preflight(self):
        heater = outfit({"condition":"night","equipment":["heater"]})
        cooler = outfit({"condition":"heat","equipment":["cooler"]})
        self.assertGreater(crew_use(25,10,heater)["suit_wh"],crew_use(25,10)["suit_wh"])
        self.assertGreater(crew_use(25,10,cooler)["water_l"],crew_use(25,10)["water_l"])
        with tempfile.TemporaryDirectory() as directory, patch.dict("os.environ",{
            "MARS_HABITAT_DB": str(Path(directory)/"test.db")
        }), TestClient(app) as client:
            spec = {"center":[65,30],"radius":500,"eva_goals":1,"rover_goals":1,
                    "condition":"night","equipment":[]}
            report = client.post("/api/v1/habitat/plan",json=spec).raise_for_status().json()
            self.assertTrue(any("Suit heater required" in reason for reason in report["habitat"]["rejections"]))
            self.assertEqual(client.post("/api/v1/habitat/start",json={"id":report["habitat"]["id"]}).status_code,409)
            spec["equipment"] = ["heater"]
            report = client.post("/api/v1/habitat/plan",json=spec).raise_for_status().json()
            plan = report["habitat"]
            self.assertFalse(plan["rejections"])
            self.assertEqual(plan["gear"]["active"],["heater"])
            self.assertTrue(report["decision_audit"]["sorties"])
            client.post("/api/v1/habitat/start",json={"id":plan["id"]}).raise_for_status()
            for i in range(1,20):
                reading = client.post("/api/v1/habitat/telemetry",json={
                    "id":plan["id"],"progress":i/20,"sequence":i}).raise_for_status().json()
                if reading["equipment_active"]:
                    break
            else:
                self.fail("Heater never switched on during EVA")
            self.assertEqual(reading["ambient_temperature_c"],-75)
            self.assertEqual(reading["equipment_active"],["heater"])
            self.assertGreater(reading["spent"]["suit_wh"],0)

    def test_atlas_keeps_closures_and_pending_targets(self):
        report={"hazard":[25]*(226*209),"monitor_change_cell":[2,2],
                "sites":[{"cell":[25,25],"kind":"EVA","visit_fraction":None},
                         {"cell":[40,40],"kind":"EVA","visit_fraction":.5}]}
        sectors=summarize(report)
        self.assertEqual(sectors["0:0"]["status"],"hazard")
        self.assertEqual(sectors["4:4"]["status"],"revisit")
        self.assertEqual(sectors["6:6"]["status"],"completed")
        self.assertEqual(sectors["15:15"]["status"],"clear")

    def test_trained_question_routing(self):
        settings={"condition":"night","equipment":[],"objective":"relief"}
        result=answer("do I need a heater",settings)
        self.assertEqual(result["topic"],"heater")
        self.assertIn("required but missing",result["advice"])
        self.assertEqual(answer("recipe for chocolate cheesecake",settings)["topic"],"unsupported")
