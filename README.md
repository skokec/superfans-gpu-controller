# NVIDIA GPU-based FAN controller for SUPERMICRO server

This controller enables automatic adjustments of FANs in SUPERMICRO servers based on GPU temperature.  Only NVIDIA GPUs are supported since the tool uses nvidia-smi to parse the GPU temperature. FANs are controlled through IPMI tool (`impitool`) using the modified superfans (https://github.com/putnam/superfans/blob/master/superfans) script.

# Requirements

* Linux (tested on Ubuntu 16.04)
* Python 2.7
* nvidia drivers/tools (`nvidia-smi`)
* IPMI tool (`impitool`) with loaded module (`modprobe ipmi_devintf`)

Tested on SUPERMICRO 4029GP TRT2 with RTX 2080 Ti (nvidia 415.27 drivers).

# Usage

```bash
python superfans_gpu_controller.py
```

