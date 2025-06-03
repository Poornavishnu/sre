


# Edge Monitoring Agent & API Server

This project implements a Python-based API server for receiving and storing edge device system metrics. The metrics are pushed in real-time from Linux-based agents and stored in InfluxDB, making them available for visualization (e.g., via Grafana).


## Overview

-Flask API server with endpoints for metrics ingestion, health, and history
-Structured JSON logging with rotating log files
-Rate-limited with flask-limiter (10 requests/min per IP)
-Metrics pushed in InfluxDB line protocol
-EC2-hosted server configured with systemd for persistent service management


## Grafana Dashboards

![Screenshot 2025-06-02 at 6 31 14 PM](https://github.com/user-attachments/assets/4035c02c-7de2-419d-8f62-841ce7a07a19)

![Screenshot 2025-06-02 at 6 31 42 PM](https://github.com/user-attachments/assets/60731f0a-7fdb-4676-86ae-e6bec5235f91)



## File Structure

edge-server/
── api_server.py               # Flask API server
── requirements.txt            # Python dependencies
── deploy.sh                   # Deployment script
── api_server.service          # Systemd service definition
── unit_test.py                # Complete pytest-based test suite
── logs/                       # Runtime logs (auto-created)
── config.yaml                 # YAML configuration with InfluxDB details


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


## Testing

Written with pytest

Tests validate:

Good/bad metric ingestion
Rate limiting
Logging structure
History and health endpoints
Simulated InfluxDB failures

Run with:
pytest unit_test.py -v

## Deployment

Systemd Setup
```
chmod +x deploy.sh

./deploy.sh

sudo systemctl status api_server
```
Includes deploy.sh to install dependencies, move files, and enable services.
Logging to logs/api.log with rotation.

## Requirements

Flask==3.1.1
requests==2.32.3
PyYAML==6.0.2
flask-limiter==3.5.0
pytest==8.3.5
Install with:
pip install -r requirements.txt

## Highlights

-Secure tag escaping for InfluxDB compliance
-ENV var fallback for API URL and DB config
-Full test suite with mocked external calls
Minimal memory footprint on edge devices

########################################################



### Flask_api server Troubleshoot
```
location: /home/ubuntu/edge-server
logs: /home/ubuntu/edge-server/logs/api.log

tail -f  /home/ubuntu/edge-server/logs/api.log 

start/stop/status - check 

sudo systemctl stop api_server
sudo systemctl start api_server
sudo systemctl status api_server

```

Flask_api server logs we see for post from edge device.



![image](https://github.com/user-attachments/assets/001c8612-724c-4692-b95a-38d3d6bd2a45)


```
{"timestamp": "2025-06-02T17:25:44.225076+00:00", "event": "INFLUX LINE", "status": "OK", "data": {"line": "system_metrics,location=store-101,zone=east,device_id=edge-4a47aae248a3,host=MacBookAir,device_type=unknown cpu=27.8,memory=81.1,disk=38.1,memory_total=8589934592,memory_used=3232989184,disk_total=245107195904,disk_used=14836686848,heartbeat=1,cpu_core_0=33.3,cpu_core_1=35.3,cpu_core_2=28.0,cpu_core_3=24.0,cpu_core_4=17.6,cpu_core_5=4.1,cpu_core_6=3.9,cpu_core_7=0.0"}}
{"timestamp": "2025-06-02T17:25:44.231463+00:00", "event": "INFLUX RESPONSE", "status": "OK", "data": {"status_code": 204, "text": ""}}
{"timestamp": "2025-06-02T17:25:44.232254+00:00", "event": "POST /metrics", "status": "OK", "data": {"device_id": "edge-4a47aae248a3", "hostname": "MacBookAir", "cpu_total": 27.8, "cpu_per_core": [33.3, 35.3, 28.0, 24.0, 17.6, 4.1, 3.9, 0.0], "memory_percent": 81.1, "disk_percent": 38.1, "tags": {"location": "store-101", "zone": "east"}}}
```




If the InfluxDB is down we get this error  “{"error":"Failed to reach InfluxDB"}

![image](https://github.com/user-attachments/assets/e487333a-ee06-43a4-82f3-79eb189d5dfd)



if its up we see {"message":"Metrics stored successfully"}



![image](https://github.com/user-attachments/assets/6c2a0750-a71a-43b9-8901-06bfc83386d5)


From edge device if its sending the metrics we see this error for the influxDB or the api server is stopped. 

```
{"timestamp": "2025-06-02T17:34:58.033780+00:00", "event": "InfluxDB error", "status": "FAIL", "data": "HTTPConnectionPool(host='localhost', port=8086): Max retries exceeded with url: /write?db=metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7b810070bdf0>: Failed to establish a new connection: [Errno 111] Connection refused'))"}
```
We can troubleshoot the error like this identifying its influx issue.


we see this log at the edge-device logs as we enables 3 retries

this is for api_server issue 

```
[edge-4a47aae248a3] Metrics collected at 2025-06-02T17:41:20.367836+00:00
[ERROR] 2025-06-02T17:41:20.409992+00:00: Cloud push attempt 1 failed: HTTPConnectionPool(host='34.229.115.74', port=5001): Max retries exceeded with url: /metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x102681cd0>: Failed to establish a new connection: [Errno 61] Connection refused'))
[ERROR] 2025-06-02T17:41:22.459507+00:00: Cloud push attempt 2 failed: HTTPConnectionPool(host='34.229.115.74', port=5001): Max retries exceeded with url: /metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1026823f0>: Failed to establish a new connection: [Errno 61] Connection refused'))
[ERROR] 2025-06-02T17:41:26.498968+00:00: Cloud push attempt 3 failed: HTTPConnectionPool(host='34.229.115.74', port=5001): Max retries exceeded with url: /metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10263b530>: Failed to establish a new connection: [Errno 61] Connection refused'))
[ERROR] 2025-06-02T17:41:26.499108+00:00: All cloud push attempts failed
^CTraceback (most recent call last): 
```
this is for InfluxDB issue 
```
{"timestamp": "2025-06-02T17:34:51.583277+00:00", "device_id": "edge-4a47aae248a3", "level": "INFO", "device_type": "edge-node", "metrics": {"timestamp": "2025-06-02T17:34:50.576508+00:00", "hostname": "Vishnus-Mac.local", "cpu_total": 15.7, "cpu_per_core": [31.4, 26.0, 24.0, 24.0, 0.0, 0.0, 0.0, 0.0], "memory_percent": 80.7, "memory_used": 3010101248, "memory_total": 8589934592, "disk_percent": 38.5, "disk_used": 14836686848, "disk_total": 245107195904, "heartbeat": 1}, "tags": {"location": "store-101", "zone": "east"}}
{"timestamp": "2025-06-02T17:34:51.682385+00:00", "device_id": "edge-4a47aae248a3", "level": "ERROR", "message": "Cloud push attempt 1 failed: 500 Server Error: INTERNAL SERVER ERROR for url: http://34.229.115.74:5001/metrics"}
{"timestamp": "2025-06-02T17:34:53.782047+00:00", "device_id": "edge-4a47aae248a3", "level": "ERROR", "message": "Cloud push attempt 2 failed: 500 Server Error: INTERNAL SERVER ERROR for url: http://34.229.115.74:5001/metrics"}
{"timestamp": "2025-06-02T17:34:57.896067+00:00", "device_id": "edge-4a47aae248a3", "level": "ERROR", "message": "Cloud push attempt 3 failed: 500 Server Error: INTERNAL SERVER ERROR for url: http://34.229.115.74:5001/metrics"}
{"timestamp": "2025-06-02T17:34:57.896656+00:00", "device_id": "edge-4a47aae248a3", "level": "ERROR", "message": "All cloud push attempts failed"}
```


#############################################################



### InFLuxDB Troubleshooting
```
sudo systemctl status influxdb
```

Should say active (running)


If not, run: sudo systemctl start influxdb


```
sudo journalctl -u influxdb -n 100 --no-pager

```
To access Influx 

on linux just type - influx
```
SHOW DATABASES;
USE metrics;
SHOW MEASUREMENTS;
SELECT * FROM system_metrics ORDER BY time DESC LIMIT 5;
```
![image](https://github.com/user-attachments/assets/b8da8ae3-a38b-4f92-a964-8db2d0572a0e)



If you see your data coming in, InfluxDB is receiving metrics correctly.

To check disk usage 

```
sudo du -sh /var/lib/influxdb

status - curl -I http://localhost:8086/ping

```




