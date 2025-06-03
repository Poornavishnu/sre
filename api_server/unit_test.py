import unittest
from unittest.mock import patch
from api_server import ApiServer
import json


class TestApiServerExtended(unittest.TestCase):
    def setUp(self):
        self.server = ApiServer()
        self.app = self.server.app
        self.app.testing = True
        self.client = self.app.test_client()

    @patch("requests.post")
    def test_receive_metrics_valid(self, mock_post):
        mock_post.return_value.status_code = 204
        mock_post.return_value.text = ""
        payload = {
            "device_id": "test-device-001",
            "hostname": "test-host",
            "cpu_total": 55.5,
            "memory_percent": 68.0,
            "disk_percent": 42.0,
            "tags": {"env": "prod"}
        }
        response = self.client.post("/metrics", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Metrics stored successfully", response.get_data(as_text=True))

    def test_receive_metrics_invalid_json(self):
        response = self.client.post("/metrics", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON format", response.get_data(as_text=True))

    @patch("requests.post")
    def test_influx_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"
        payload = {
            "device_id": "test-device-002",
            "hostname": "host",
            "cpu_total": 40.0,
            "memory_percent": 60.0,
            "disk_percent": 70.0
        }
        response = self.client.post("/metrics", json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to write to InfluxDB", response.get_data(as_text=True))

    def test_history_empty(self):
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    @patch("requests.post")
    def test_history_after_push(self, mock_post):
        mock_post.return_value.status_code = 204
        mock_post.return_value.text = ""
        metric = {
            "device_id": "abc",
            "hostname": "host",
            "cpu_total": 23.0,
            "memory_percent": 45.0,
            "disk_percent": 50.0
        }
        self.client.post("/metrics", json=metric)
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_status_endpoint(self):
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.get_json())

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "OK")

    def test_logging_structure(self):
        self.server.log_action("unit_test", {"key": "value"}, status="PASS")
        with open(self.server.LOG_PATH, "r") as log_file:
            last_log = json.loads(list(log_file)[-1])
            self.assertIn("timestamp", last_log)
            self.assertEqual(last_log["event"], "unit_test")
            self.assertEqual(last_log["status"], "PASS")
            self.assertEqual(last_log["data"], {"key": "value"})


if __name__ == "__main__":
    unittest.main()
