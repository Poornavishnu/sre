#!/bin/bash
set -e

echo "Installing system dependencies..."
sudo apt update && sudo apt install -y python3 python3-pip

echo "Installing Python requirements..."
pip3 install -r requirements.txt

echo "Ensuring logs and config directories exist..."
mkdir -p logs config

# Get full path to current directory
PROJECT_DIR=$(pwd)

echo "⚙️ Installing systemd service files..."

# Replace ExecStart path with current directory
sed "s|/home/pi/your_project|$PROJECT_DIR|g" monitor.service | sudo tee /etc/systemd/system/monitor.service > /dev/null
sed "s|/home/pi/your_project|$PROJECT_DIR|g" api.service | sudo tee /etc/systemd/system/api.service > /dev/null

# Reload systemd to apply changes
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "Enabling services to start on boot..."
sudo systemctl enable monitor.service
sudo systemctl enable api.service

echo "Starting services..."
sudo systemctl start monitor.service
sudo systemctl start api.service

echo "Setup complete. Services are running:"
systemctl status monitor.service --no-pager
systemctl status api.service --no-pager