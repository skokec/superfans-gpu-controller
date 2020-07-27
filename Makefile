all: superfans-gpu-controller superfans-gpu-controller.service
.PHONY: all superfans-gpu-controller-daemon install uninstall clean

service_dir=/etc/systemd/system
conf_dir=/etc
awk_script='BEGIN {FS="="; OFS="="}{if ($$1=="ExecStart") {$$2=exec_path} if (substr($$1,1,1) != "\#") {print $$0}}'

superfans-gpu-controller: superfans_gpu_controller.py setup.py
	pip3 install .

superfans-gpu-controller.service: superfans_gpu_controller.py
# awk is needed to replace the absolute path of mydaemon executable in the .service file
	awk -v exec_path='$(shell which superfans-gpu-controller) $(conf_dir)/superfans-gpu-controller.json' $(awk_script) superfans-gpu-controller.service.template > superfans-gpu-controller.service

install: $(service_dir) $(conf_dir) superfans-gpu-controller.service
	cp superfans-gpu-controller.json $(conf_dir)
	cp superfans-gpu-controller.service $(service_dir)
	-systemctl enable superfans-gpu-controller.service
	-systemctl enable superfans-gpu-controller

uninstall:
	-systemctl stop superfans-gpu-controller
	-rm -r $(service_dir)/superfans-gpu-controller.service
	-rm -r $(conf_dir)/superfans-gpu-controller.json

clean:
	-rm superfans-gpu-controller.service
