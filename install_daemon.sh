#!/bin/sh

echo "Created '/etc/systemd/system/superfans-gpu-controller.service' service file"
echo "[Unit]
Description=GPU-based controller of SUPERMICRO server FANs
After=syslog.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=`pwd`
Environment=PYTHONUNBUFFERED=true
ExecStart=/usr/bin/python -u `pwd`/superfans_gpu_controller.py
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/superfans-gpu-controller.service
echo "\n"

echo "Registering superfans-gpu-controller.service"
systemctl enable superfans-gpu-controller.service
systemctl daemon-reload

echo "Enabled start at system startup"
systemctl enable superfans-gpu-controller

echo "Starting the service"
systemctl start superfans-gpu-controller
