# NVIDIA GPU-based FAN controller for SUPERMICRO server

This controller enables automatic adjustments of FANs in SUPERMICRO servers based on GPU temperature.  Only NVIDIA GPUs are supported since the tool uses nvidia-smi to parse the GPU temperature. FANs are controlled through IPMI tool (`impitool`) using the modified superfans (https://github.com/putnam/superfans) script.

# Requirements

* Linux (tested on Ubuntu 18.04)
* Python 2.7
* nvidia drivers/tools (`nvidia-smi`)
* IPMI tool (`impitool`) with loaded module (`modprobe ipmi_devintf`)

Tested on SUPERMICRO 4029GP TRT2 with RTX 2080 Ti (nvidia 415.27 drivers).

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

Service is registered for start at system startup. Start and stop it using:
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
