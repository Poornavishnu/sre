#!/bin/bash
# Update and install necessary packages
apt-get update -y
apt-get install -y python3 python3-pip git curl

# Install Python dependencies
pip3 install flask==3.1.1 psutil==7.4.2 pyyaml==6.0.2 requests==2.31.3 pytest==8.4.0

# Clone or copy your Flask app
mkdir -p /opt/monitoring
cd /opt/monitoring
cat <<EOF > app.py
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return "SRE Monitoring Agent Running"
app.run(host='0.0.0.0', port=5001)
EOF

# Run Flask app in background
nohup python3 /opt/monitoring/app.py &

# Install InfluxDB
curl -sL https://repos.influxdata.com/influxdb.key | gpg --dearmor | tee /usr/share/keyrings/influxdb-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian stable main" | tee /etc/apt/sources.list.d/influxdb.list
apt-get update && apt-get install -y influxdb
systemctl enable influxdb
systemctl start influxdb

# Install Grafana
apt-get install -y software-properties-common
add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
apt-get update
apt-get install -y grafana
systemctl enable grafana-server
systemctl start grafana-server