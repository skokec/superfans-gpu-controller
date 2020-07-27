# NVIDIA GPU-based FAN controller for SUPERMICRO server

This controller enables automatic adjustments of FANs in SUPERMICRO servers based on GPU temperature.  Only NVIDIA GPUs are supported since the tool uses nvidia-smi to parse the GPU temperature. FANs are controlled through IPMI tool (`impitool`) using the modified superfans (https://github.com/putnam/superfans) script.

# Requirements

* Linux (tested on Ubuntu 16.04.5)
* Python 3 / pip3
* nvidia drivers/tools (`nvidia-smi`)
* IPMI tool (`ipmitool`) with loaded module (`modprobe ipmi_devintf`)

Tested on SUPERMICRO 4029GP TRT2 with RTX 2080 Ti (nvidia 415.27 drivers). 

NOTE: Using this script on other systems requires manual calibration of a function that converts the FANs RPM values into %-based values (function `SUPERMICRO_4029GP_TRT2_RPM_to_percent()` in `supermicro.py`). Current values are hardcoded for SUPERMICRO 4029GP TRT2.

# Install

```bash
sudo apt-get install ipmitool && modprobe ipmi_devintf
sudo make install
```

By default python packages are installed using pip3 and superfans-gpu-controller.service is created (started and enabled at boot).

# Usage

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

## Manuall usage

Directly call python script (requires sudo access for `impitool`):
```bash
sudo python superfans_gpu_controller.py config.json
```

Print RPMs of all FANs grouped by zones:
```bash
sudo python superfans.py
```

# Settings

Settings are in /etc/superfans-gpu-controller.json for systemd and by default the config contains:

```python
{
    "fan_settings" : {"0": 20,
                    "60": 25,
                    "70": 30,
                    "80": 35,
                    "87": 40,
                    "90": 43}
}

```
This corresponds to following mapping of GPU temperature in °C to the percent of activated FAN (relative to max RPM as manually set for SUPERMICRO 4029GP TRT2):
 * 0°C => 20%
 * 60°C => 25%
 * 70°C => 30%
 * 80°C => 35%
 * 87°C => 40%
 * 90°C => 43%
 
At full workload using 4x RTX 2080 Ti this results in around 75°C - 80°C at GPU.

## TODO:
 * [x] split settings into seperate config file
 * [ ] enable linear increases between each setting point
 * [ ] enable online calibration of FANs (currenlty hardcoded for SUPERMICRO 4029GP TRT2!!)
 * [ ] enable robust detection of faulty FANs as outliers (using RANSAC-like algorithm)
