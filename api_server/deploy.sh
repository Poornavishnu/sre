#!/bin/bash
set -e  # Exit on first failure

APP_DIR="/opt/edge-server"
SERVICE_NAME="api_server"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"
SERVICE_FILE="$APP_DIR/api_server.service"

echo "Creating app directory at $APP_DIR"
sudo mkdir -p "$APP_DIR"
sudo cp -r . "$APP_DIR"

echo "Installing Python dependencies..."
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    pip3 install -r "$REQUIREMENTS_FILE"
else
    echo "requirements.txt not found at $REQUIREMENTS_FILE"
    exit 1
fi

echo "Deploying systemd service..."
if [[ -f "$SERVICE_FILE" ]]; then
    sudo cp "$SERVICE_FILE" /etc/systemd/system/"$SERVICE_NAME".service
else
    echo "Service file not found at $SERVICE_FILE"
    exit 1
fi

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Done! Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager