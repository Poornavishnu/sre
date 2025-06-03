Edge Monitoring Agent & API Server

This project implements a Python-based API server for receiving and storing edge device system metrics. The metrics are pushed in real-time from Linux-based agents and stored in InfluxDB, making them available for visualization (e.g., via Grafana).


Overview

-Flask API server with endpoints for metrics ingestion, health, and history
-Structured JSON logging with rotating log files
-Rate-limited with flask-limiter (10 requests/min per IP)
-Metrics pushed in InfluxDB line protocol
-EC2-hosted server configured with systemd for persistent service management


File Structure

config/ 
── config.yaml                 # YAML configuration with InfluxDB details
── api_server.py               # Flask API server
── requirements.txt            # Python dependencies
── deploy.sh                   # Deployment script
── api_server.service          # Systemd service definition
── unit_test.py                # Complete pytest-based test suite
── logs/                       # Runtime logs (auto-created)


API Server (api_server.py)

Flask-based REST API with:
POST /metrics
GET /status
GET /history
GET /health
Writes data in InfluxDB line protocol.
Validates tags and metric fields.
Logs structured JSON with timestamps.
Enforces rate limits (10/min) with flask-limiter.


Testing

Written with pytest

Tests validate:

Good/bad metric ingestion
Rate limiting
Logging structure
History and health endpoints
Simulated InfluxDB failures

Run with:
pytest unit_test.py -v

Deployment

Systemd Setup

chmod +x deploy.sh
./deploy.sh

sudo systemctl status api_server

Includes deploy.sh to install dependencies, move files, and enable services.
Logging to logs/api.log with rotation.

Requirements

Flask==3.1.1
requests==2.32.3
PyYAML==6.0.2
flask-limiter==3.5.0
pytest==8.3.5
Install with:
pip install -r requirements.txt

Highlights

Secure tag escaping for InfluxDB compliance
ENV var fallback for API URL and DB config
Full test suite with mocked external calls
Minimal memory footprint on edge devices




Author
Poornavishnu — Edge Signal SRE Project
