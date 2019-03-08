# NVIDIA GPU-based FAN controller for SUPERMICRO server

This controller enables automatic adjustments of FANs in SUPERMICRO servers based on GPU temperature.  Only NVIDIA GPUs are supported since the tool uses nvidia-smi to parse the GPU temperature. FANs are controlled through IPMI tool (`impitool`) using the modified superfans (https://github.com/putnam/superfans) script.

# Requirements

* Linux (tested on Ubuntu 18.04)
* Python 2.7
* nvidia drivers/tools (`nvidia-smi`)
* IPMI tool (`impitool`) with loaded module (`modprobe ipmi_devintf`)

Tested on SUPERMICRO 4029GP TRT2 with RTX 2080 Ti (nvidia 415.27 drivers). 

NOTE: Using on other systems requires manual calibration function that converts FANs RPM into %-based values (in SUPERMICRO_4029GP_TRT2_RPM_to_percent()` function in `supermicro.py`). Current this is hardcoded for SUPERMICRO 4029GP TRT2.

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

Currently the settings are hardcoded into superfans_gpu_controller.py using the following table:
 * 0°C => 25%
 * 60°C => 30%
 * 70°C => 36%
 * 80°C => 40%
 * 85°C => 45%
 * 90°C => 50%
 
At full workload using 4x RTX 2080 Ti this results in around 75°C - 80°C at GPU.

## TODO:
 * split settings into seperate config file
 * enable linear increases between each setting point
 * enable online calibration of FANs (currenlty hardcoded for SUPERMICRO 4029GP TRT2!!)
