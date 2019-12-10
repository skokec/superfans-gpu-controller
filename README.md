# NVIDIA GPU-based FAN controller for SUPERMICRO server

This controller enables automatic adjustments of FANs in SUPERMICRO servers based on GPU temperature.  Only NVIDIA GPUs are supported since the tool uses nvidia-smi to parse the GPU temperature. FANs are controlled through IPMI tool (`impitool`) using the modified superfans (https://github.com/putnam/superfans) script.

# Requirements

* Linux (tested on Ubuntu 16.04.5)
* Python 2.7
* nvidia drivers/tools (`nvidia-smi`)
* IPMI tool (`impitool`) with loaded module (`modprobe ipmi_devintf`)

Tested on SUPERMICRO 4029GP TRT2 with RTX 2080 Ti (nvidia 415.27 drivers). 

NOTE: Using this script on other systems requires manual calibration of a function that converts the FANs RPM values into %-based values (function `SUPERMICRO_4029GP_TRT2_RPM_to_percent()` in `supermicro.py`). Current values are hardcoded for SUPERMICRO 4029GP TRT2.

# Usage

Directly call python script (requires sudo access for `impitool`):
```bash
sudo python superfans_gpu_controller.py
```

Or install systemd service (`superfans-gpu-controller.service`):

```bash
sudo chmod +x ./install_daemon.sh
sudo ./install_daemon.sh
```

Service is registered to start at system startup. Start and stop it using:
```bash
# start
sudo systemctl start superfans-gpu-controller

# stop
sudo systemctl stop superfans-gpu-controller

# check the status
sudo systemctl status superfans-gpu-controller

# view logs (with trailing)
sudo journalctl -f -u superfans-gpu-controller
```

# Settings

Currently the settings are hardcoded into `superfans_gpu_controller.py` using the following table:
 * 0°C => 20%
 * 60°C => 25%
 * 70°C => 30%
 * 80°C => 35%
 * 87°C => 40%
 * 90°C => 43%
 
At full workload using 4x RTX 2080 Ti this results in around 75°C - 80°C at GPU.

## TODO:
 * [ ] split settings into seperate config file
 * [ ] enable linear increases between each setting point
 * [ ] enable online calibration of FANs (currenlty hardcoded for SUPERMICRO 4029GP TRT2!!)
 * [ ] enable robust detection of faulty FANs as outliers (using RANSAC-like algorithm)
