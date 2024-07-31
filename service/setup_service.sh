#!/bin/bash

# Get the current working directory
CURRENT_DIR=$(pwd)

# Define the template and destination paths
TEMPLATE_FILE="$CURRENT_DIR/service/PythonScan.service.template"
SERVICE_FILE="/etc/systemd/system/PythonScan.service"

# Replace PLACEHOLDER with the current directory in the template
sed "s|PLACEHOLDER|$CURRENT_DIR|g" $TEMPLATE_FILE > /tmp/PythonScan.service

# Copy the modified service file to the systemd directory
sudo cp /tmp/PythonScan.service $SERVICE_FILE

# Reload systemd manager configuration
sudo systemctl daemon-reload

# Enable the service to start at boot
sudo systemctl enable PythonScan.service

# Start the service
sudo systemctl start PythonScan.service

# Check the status of the service
sudo systemctl status PythonScan.service