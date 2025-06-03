# Edge Device Monitoring System

This project provides a production-grade, high-availability monitoring agent for edge devices. It collects system resource metrics (CPU, memory, disk), if enabled  (it applies threshold-based alerting), and forwards metrics to a central server for visualization and analysis.

---

## Project Structure

### Core Components

- **monitor.py** – Main monitoring agent that:
  - Loads configuration from `config/config.yaml`
  - Collects metrics using `psutil`
  - Checks for threshold violations
  - Logs locally and pushes data to a cloud API if configured

- **api_server.py** – Flask-based REST API server that:
  - Receives metrics from devices
  - Stores metrics in InfluxDB
  - Logs events
  - Provides simple API endpoints for health and recent data

- **metrics.py** – Functions to collect system metrics:
  - `cpu_total`, `cpu_per_core`
  - `memory_total`, `memory_used`, `memory_percent`
  - `disk_total`, `disk_used`, `disk_percent`

- **logger.py** – Logs JSON-formatted events and metrics to rotating log files.

- **device_identity.py** – Determines unique identity of device using hostname or patterns.

- **system_check.py** – Detects available system capabilities and filters unsupported metrics.

- **config_loader.py** – Loads and parses YAML configuration.

- **constants.py** – Holds default intervals and configuration keys.

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- `pip` and `psutil`, `PyYAML`, `requests` installed

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Device
Edit `config/config.yaml`:
```yaml
device_type: edge-node
metrics_interval: 10
metrics_to_collect:
  - cpu
  - memory
  - disk
cloud_endpoint: "http://<server-ip>:5001/metrics"
thresholds:
  cpu: 85
  memory: 75
  disk: 90
tags:
  location: "store-101"
  zone: "east"
```

### Run Agent
```bash
python monitor.py
```

### Run API Server (on central server)
```bash
python api_server.py
```

### Systemd Installation (Optional)
Use `prepare_bundle.sh` to install as a service:
```bash
chmod +x prepare_bundle.sh
./prepare_bundle.sh
```

---

##  Metrics & Logging

- Metrics are pushed to `/metrics` endpoint as JSON.
- Logs stored in `logs/` directory per device.
- Alerts triggered if resource usage exceeds configured thresholds.

---

## Testing
Unit tests are in the `tests/` folder. Run them using:
```bash
pytest tests/
```

---

## Dashboarding
Used Grafana + InfluxDB to visualize metrics:
- CPU per core and total
- Memory usage (total/used/free/%)
- Disk usage (free/overall)

---

## Edge Use Case
Designed for smart gateways, NVRs, and retail PoS edge devices with:
- Low overhead
- Threshold alerts
- Push-based cloud reporting


