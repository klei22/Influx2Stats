#!/bin/bash

# Update package list and install dependencies
sudo apt-get update
sudo apt-get install -y wget gnupg

# Import the InfluxData repository GPG key
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -

# Add the InfluxData repository to your sources list
echo "deb https://repos.influxdata.com/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

# Update package list again to include the new repository
sudo apt-get update

# Install InfluxDB
sudo apt-get install -y influxdb

# Start the InfluxDB service
sudo systemctl start influxdb

# Enable InfluxDB to start on boot
sudo systemctl enable influxdb

# Verify the installation
sudo systemctl status influxdb

echo "InfluxDB installation and setup complete."
echo "You can access InfluxDB on port 8086 and use the 'influx' command to interact with it."

