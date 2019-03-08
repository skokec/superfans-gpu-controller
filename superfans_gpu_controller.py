# Superfans GPU controller
#
# author: Domen Tabernik
# 2019

import time, superfans, subprocess, signal, sys

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

def retrieve_nvidia_gpu_temperature():
    cmd = 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'

    s = subprocess.check_output(cmd + " 2>&1", shell=True)
    if len(s) <= 0:
        return False

    out = [int(x.strip()) for x in s.split("\n") if len(x.strip()) > 0]
    if out:
        return out
    else:
        return False

def superfans_gpu_controller(fan_settings, FAN_INCREASED_MIN_TIME=120, sleep_sec=2, gpu_moving_avg_num=5, fan_target_eps=2.0):
    """
    Controller function that monitors GPU temperature in constant loop and adjusts FAN speeds based on provided `fan_settings`.
    After the loop the default preset is restored.

    :param fan_settings: dictionary that maps the temperature in deg C to % of fan speed
    :param FAN_INCREASED_MIN_TIME: minimal time before a fan speed is again reduced (based on previous change) default=120
    :param sleep_sec: loop sleep time (default=2 sec)
    :param gpu_moving_avg_num: moving average for GPU i.e. the number of last measurements that are averaged (default=5)
    :param fan_target_eps: tolerance of fan target w.r.t. the the actual value in deg C (default=1.0)
    :return:
    """
    superfan_config = dict(hostname= 'localhost')

    # save default present before changing anything
    default_preset = superfans.get_preset(superfan_config)
    print('Started fan control using GPU temperature.')
    print('Using settings:')
    for k in sorted(fan_settings.keys()):
        print('\t%d C = %d ' % (k, fan_settings[k]) + "%")
    print('\n')

    try:
        FAN_MEMBERS = superfans.FAN_ZONES_MEMBERS[superfans.FAN_ZONE_SYS1] + \
                      superfans.FAN_ZONES_MEMBERS[superfans.FAN_ZONE_SYS2]

        # GPU moving average
        previous_target_fan = None
        previous_update_time = None

        prev_GPU_temp = []

        # ensure correct ending when SIGINT and SIGTERM are received
        k = GracefulKiller()
        while not k.kill_now:

            # get GPU temperature
            GPU_temp = retrieve_nvidia_gpu_temperature()

            prev_GPU_temp.append(GPU_temp)

            # continue until we have enough sampels for moving average
            if len(prev_GPU_temp) < gpu_moving_avg_num:
                continue

            # retain last 5 mesurements
            prev_GPU_temp = prev_GPU_temp[-gpu_moving_avg_num:]
            mean_GPU_temp = prev_GPU_temp[0]
            for gpu_temp in prev_GPU_temp[1:]:
                mean_GPU_temp = [x+y for x,y in zip(gpu_temp, mean_GPU_temp)]

            mean_GPU_temp = [x/len(prev_GPU_temp) for x in mean_GPU_temp]

            max_gpu_temp = max(mean_GPU_temp)

            for key_temp in sorted(fan_settings.keys())[::-1]:
                if key_temp <= max_gpu_temp:
                    target_fan = fan_settings[key_temp]
                    break


            current_fan_levels = superfans.get_fan(superfan_config, FAN_MEMBERS)
            current_update_time = time.time()
            diff_sys1_fan = [abs(current_fan_levels[FAN] - target_fan) for FAN in superfans.FAN_ZONES_MEMBERS[superfans.FAN_ZONE_SYS1]]
            diff_sys2_fan = [abs(current_fan_levels[FAN] - target_fan) for FAN in superfans.FAN_ZONES_MEMBERS[superfans.FAN_ZONE_SYS2]]

            disbale_update = False

            if previous_update_time is not None and previous_target_fan is not None:
                has_enough_time_elapsed = current_update_time - previous_update_time > FAN_INCREASED_MIN_TIME
                is_level_down_change = target_fan < previous_target_fan
                disbale_update = True if is_level_down_change and not has_enough_time_elapsed else False

            if not disbale_update:
                # Allow for 1% difference in target
                update_sys1_fan = any([d > fan_target_eps for d in diff_sys1_fan])
                update_sys2_fan = any([d > fan_target_eps for d in diff_sys2_fan])
                if update_sys1_fan:
                    superfans.set_fan(superfan_config, target_fan, superfans.FAN_ZONE_SYS1)

                if update_sys2_fan:
                    superfans.set_fan(superfan_config, target_fan, superfans.FAN_ZONE_SYS2)

                if update_sys1_fan or update_sys2_fan:
                    print('\tCurrent GPU measurements: %s' % ','.join(map(str,GPU_temp)))
                    print('\tMoving average GPU measurements: %s' % ','.join(map(str,mean_GPU_temp)))
                    print('\tTarget difference: SYS1 fan = %f; SYS2 fan = %f' % (max(diff_sys1_fan), max(diff_sys2_fan)))
                    print('\n')

                    previous_target_fan = target_fan
                    previous_update_time = current_update_time

            time.sleep(sleep_sec)
    finally:
        # revert back to default preset before finishing
        superfans.set_preset(superfan_config, default_preset)
        print('Reverted back to system default.')

if __name__  == "__main__":
    # fan settings = {[in deg C]: [% fan], ...}
    fan_settings = {0: 25,
                    60: 30,
                    70: 36,
                    80: 40,
                    85: 45,
                    90: 50}

    superfans_gpu_controller(fan_settings)