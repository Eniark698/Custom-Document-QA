#!/bin/bash

# Stop the service
sudo systemctl stop PythonScan.service

# Reload the systemd manager configuration
sudo systemctl daemon-reload

# Start the service
sudo systemctl start PythonScan.service

# Check the status of the service
sudo systemctl status PythonScan.service
