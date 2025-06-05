"""API Server for receiving and forwarding system metrics to InfluxDB."""

import os
import json
import logging
from datetime import datetime, timezone
from collections import deque
from logging.handlers import RotatingFileHandler

import requests
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config_loader import ConfigLoader

class ApiServer:
    """Flask-based API server that receives metrics and pushes them to InfluxDB."""

    CONFIG_PATH = "config.yaml"
    LOG_PATH = "logs/api.log"
    MAX_HISTORY = 10

    def __init__(self):
        self.config_loader = ConfigLoader(self.CONFIG_PATH)
        self.config = self.config_loader.get_config()
        influx = self.config.get("influxdb", {})
        influx_url = os.getenv("INFLUX_URL") or influx.get("url", "http://localhost:8086")
        influx_db = os.getenv("INFLUX_DB") or influx.get("database", "metrics")
        self.influx_url = f"{influx_url}/write?db={influx_db}"

        self.app = Flask(__name__)
        self.limiter = Limiter(key_func=get_remote_address)
        self.limiter.init_app(self.app)

        self.metrics_buffer = deque(maxlen=self.MAX_HISTORY)
        self.latest_metrics = {}

        self.setup_logging()
        self.setup_routes()

    def setup_logging(self):
        """Configure structured logging."""
        os.makedirs(os.path.dirname(self.LOG_PATH), exist_ok=True)
        self.logger = logging.getLogger("ApiServer")
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        handler = RotatingFileHandler(self.LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3)
        self.logger.addHandler(handler)

    def log_action(self, action, data=None, status="OK"):
        """Log a structured JSON message."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": action,
            "status": status,
            "data": data
        }
        self.logger.info(json.dumps(log_entry))

    def escape_influx_tag(self, val):
        """Escape special characters in InfluxDB tags."""
        return str(val).replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")

    def receive_metrics(self):
        """Process incoming metrics POST request."""
        try:
            if not request.is_json:
                return jsonify({"error": "Invalid JSON format"}), 400

            metrics = request.get_json()
            required_fields = ["device_id", "hostname", "cpu_total", "memory_percent", "disk_percent"]
            if not all(k in metrics for k in required_fields):
                self.log_action("POST /metrics", metrics, status="INVALID")
                return jsonify({"error": "Missing fields"}), 400

            tags = metrics.get("tags", {})
            if not isinstance(tags, dict):
                tags = {}
            tags["device_id"] = metrics["device_id"]
            tags["host"] = metrics["hostname"]
            tags["device_type"] = metrics.get("device_type", "unknown")

            tag_str = ",".join(
                f"{self.escape_influx_tag(k)}={self.escape_influx_tag(v)}"
                for k, v in tags.items()
            )

            field_parts = [
                f"cpu={metrics['cpu_total']}",
                f"memory={metrics['memory_percent']}",
                f"disk={metrics['disk_percent']}",
                f"memory_total={metrics.get('memory_total', 0)}",
                f"memory_used={metrics.get('memory_used', 0)}",
                f"disk_total={metrics.get('disk_total', 0)}",
                f"disk_used={metrics.get('disk_used', 0)}",
                f"heartbeat={metrics.get('heartbeat', 1)}"
            ]

            cpu_per_core = metrics.get("cpu_per_core")
            if isinstance(cpu_per_core, list):
                field_parts.extend(
                    f"cpu_core_{i}={core}" for i, core in enumerate(cpu_per_core)
                )

            field_str = ",".join(field_parts)
            line = f"system_metrics,{tag_str} {field_str}"

            self.log_action("INFLUX LINE", {"line": line})

            try:
                res = requests.post(self.influx_url, data=line, timeout=5)
                self.log_action("INFLUX RESPONSE", {
                    "status_code": res.status_code,
                    "text": res.text
                })
                if res.status_code != 204:
                    return jsonify({"error": "Failed to write to InfluxDB"}), 500
            except requests.RequestException as e:
                self.log_action("InfluxDB error", str(e), status="FAIL")
                return jsonify({"error": "Failed to reach InfluxDB"}), 500

            self.metrics_buffer.append(metrics)
            self.latest_metrics = metrics

            self.log_action("POST /metrics", {
                "device_id": metrics["device_id"],
                "hostname": metrics["hostname"],
                "cpu_total": metrics["cpu_total"],
                "cpu_per_core": metrics.get("cpu_per_core"),
                "memory_percent": metrics["memory_percent"],
                "disk_percent": metrics["disk_percent"],
                "tags": metrics.get("tags", {})
            })

            return jsonify({"message": "Metrics stored successfully"}), 200

        except (KeyError, TypeError, ValueError) as e:
            self.log_action("POST /metrics", status="ERROR", data={"error": str(e)})
            return jsonify({"error": "Invalid data format"}), 400
        except Exception as e:
            self.log_action("POST /metrics", status="ERROR", data={"error": str(e)})
            return jsonify({"error": "Internal server error"}), 500

    def setup_routes(self):
        """Define API endpoints."""
        @self.app.route("/metrics", methods=["POST"])
        @self.limiter.limit("10/minute")
        def receive_metrics_wrapper():
            return self.receive_metrics()

        @self.app.route("/history", methods=["GET"])
        def get_history():
            return jsonify(list(self.metrics_buffer))

        @self.app.route("/status", methods=["GET"])
        def get_status():
            return jsonify({
                "status": "ok",
                "last_updated": self.latest_metrics.get("timestamp")
            })

        @self.app.route("/health", methods=["GET"])
        def health():
            return "OK", 200

        @self.app.route("/", methods=["GET"])
        def home():
            return "Metric receiver is running!"


if __name__ == "__main__":
    server = ApiServer()
    print("API server running at http://0.0.0.0:5001")
    server.app.run(host="0.0.0.0", port=5001)
