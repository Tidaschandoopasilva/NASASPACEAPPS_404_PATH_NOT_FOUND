import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app
from app.weather import approach


class WeatherWorkflowTests(unittest.TestCase):
    def test_trend(self):
        self.assertEqual(approach([(10,-80),(11,-78),(12,-76)]),(-74.,4.,2.))

    def test_archive_and_fresh_expediton(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            "os.environ", {"MARS_HABITAT_DB":str(Path(directory)/"test.db")}
        ), TestClient(app) as client:
            weather = client.get("/api/v1/weather").raise_for_status().json()
            self.assertEqual(weather["sol"],1133)
            self.assertEqual(weather["status"],"historical")
            self.assertEqual(weather["condition"],"night")
            first = client.post("/api/v1/habitat/plan",json={}).raise_for_status().json()["habitat"]["id"]
            client.post("/api/v1/habitat/start",json={"id":first}).raise_for_status()
            second = client.post("/api/v1/habitat/plan",json={"new_expedition":True,"center":[62,35],"radius":850}).raise_for_status().json()["habitat"]["id"]
            self.assertNotEqual(first,second)
            self.assertEqual(client.get("/api/v1/habitat").json()["expeditions"],0)
            self.assertEqual(client.post("/api/v1/habitat/record",json={"id":first}).status_code,409)
            self.assertEqual(client.get("/api/v1/habitat/draft").json()["habitat"]["id"],second)
