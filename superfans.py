# superfans
# https://github.com/putnam/superfans
#
# 2019: modified by Domen Tabernik
#

import os, sys, subprocess, time, shutil, shlex

# list of FAN preset settings
FAN_PRESET_STANDARD=0
FAN_PRESET_FULL=1
FAN_PRESET_OPTIMAL=2
FAN_PRESET_HEAVYIO=4
FAN_PRESETS=[FAN_PRESET_STANDARD, FAN_PRESET_FULL, FAN_PRESET_OPTIMAL, FAN_PRESET_HEAVYIO]
#FAN_PRESETS_STR={
#  'standard' : FAN_PRESET_STANDARD,
#  'full' : FAN_PRESET_FULL,
#  'optimal' : FAN_PRESET_OPTIMAL,
#  'heavyio' : FAN_PRESET_HEAVYIO
#}
FAN_PRESETS_DESC={
  FAN_PRESET_STANDARD : "Standard (Temp controlled, target 50%)",
  FAN_PRESET_FULL : "Full (All fans at 100%)",
  FAN_PRESET_OPTIMAL : "Optimal (Temp controlled, target 30%)",
  FAN_PRESET_HEAVYIO : "Heavy IO (Temp controlled, CPU target 50%; Peripherals target 75%"
}

# list of FAN zones
FAN_ZONE_CPU1=0 # marked as FAN10 for CPU1 (right one)
FAN_ZONE_CPU2=1 # marked as FAN9 for CPU2 (left one)
FAN_ZONE_SYS2=2 # marked as FAN1-4 (right ones)
FAN_ZONE_SYS1=3 # marked as FAN5-8 (left ones)
FAN_ZONES=[FAN_ZONE_CPU1, FAN_ZONE_CPU2, FAN_ZONE_SYS2, FAN_ZONE_SYS1]
FAN_ZONES_STR={
  FAN_ZONE_CPU1:'cpu1',
  FAN_ZONE_CPU2:'cpu2',
  FAN_ZONE_SYS2:'system2',
  FAN_ZONE_SYS1:'system1',
}

# list of FANs and zone member association
FAN1 ='FAN1'
FAN2 ='FAN2'
FAN3 ='FAN3'
FAN4 ='FAN4'
FAN5 ='FAN5'
FAN6 ='FAN6'
FAN7 ='FAN7'
FAN8 ='FAN8'
FAN9 ='FAN9'
FAN10 ='FAN10'

FAN_ZONES_MEMBERS= {
  FAN_ZONE_CPU1:[FAN10],
  FAN_ZONE_CPU2:[FAN9],
  FAN_ZONE_SYS2:[FAN1,FAN2,FAN3,FAN4],
  FAN_ZONE_SYS1:[FAN5,FAN6,FAN7,FAN8],
}

# based on observations on SUPERMICRO_4029GP_TRT2 the
# SYS1 and SYS2 fans use the following linear equations to
# convert from RPM to % value
def SUPERMICRO_4029GP_TRT2_RPM_to_percent(rpm):
  return max(rpm * 0.0098 - 11.5479,0)

def set_fan_with_full_preset(config, speed, zone):
  """
  Set fan speed to a fixed %.
  Some chassis implement separate fan "zones" named CPU and Peripheral. To target specific zones, use the --zone option.
  """

  # Make sure fans are on Full setting, or else this won't stick for long
  s = get_preset(config)
  if s is False:
    print("Unable to get current fan status; exiting")
    return False

  if s != FAN_PRESET_FULL:
    print("The fan controller is currently not set to Full mode (required for manual fan settings, which will otherwise be adjusted by the BMC within minutes); setting it now.")
    set_preset(config, preset='full')
    print("Waiting 5 seconds to let fans spin up...")
    time.sleep(5)

  ok = True
  if zone == 'all' or zone == 'cpu':
    ok = ipmi_raw_cmd('0x30 0x70 0x66 0x01 0x00 0x%02x' % speed, **config)
  if ok and (zone == 'all' or zone == 'periph'):
    ok = ipmi_raw_cmd('0x30 0x70 0x66 0x01 0x01 0x%02x' % speed, **config)

  if ok:
    print("Set %s fans on %s to %d%%." % (zone, config['hostname'], speed))
    return True
  else:
    print("Unable to update fans.")
    return False

def set_fan(config, speed, zone):
  """
  Set fan speed to a fixed %.
  Will be changed by Server if not in FULL preset (need to periodically call this)
  """

  ok = ipmi_raw_cmd('0x30 0x70 0x66 0x01 0x%02x 0x%02x' % (zone, speed), **config)

  if ok:
    print("Set %s fans on %s to %d%%." % (FAN_ZONES_STR[zone], config['hostname'], speed))
    return True
  else:
    print("Unable to update fans.")
    return False

def get_fan(config, fan, in_rpm=False):
  """
  Get fan speed in % (for one or more fans).
  """
  if in_rpm:
    convert_fn = lambda x: x
  else:
    convert_fn = SUPERMICRO_4029GP_TRT2_RPM_to_percent
  
  fan_status_list = ipmi_fan_status(**config)

  if type(fan) == list:
    return_list = {}
    for f in fan:
      if fan_status_list.has_key(f):
        return_list[f] = convert_fn(fan_status_list[f])
    return return_list
  elif fan_status_list.has_key(fan):
    return convert_fn(fan_status_list[fan])
  else:
    return False


def _set_preset(config):
  """
  Retrieves fan controller preset & fan speed.
  """
  status = get_preset(config)
  if status is False:
    return False
  if status in FAN_PRESETS:
    s = FAN_PRESETS_DESC[status]
  else:
    s = "Unknown status code %d" % status
  # manual fan ctl     get(0)/set(1)  cpu(0)/periph(1)   duty(0-0x64)
  # 0x30 0x70 0x66     0x00           0x00               0x64
  fan_speed = ipmi_raw_cmd('0x30 0x70 0x66 0x00 0x00', **config)
  if fan_speed is False:
    return False
  fan_speed2 = ipmi_raw_cmd('0x30 0x70 0x66 0x00 0x01', **config)
  if fan_speed2 is False:
    return False

  print("Preset: %s" % s)
  print("Current fan speed (CPU Zone): %d%%" % int(fan_speed, 16))
  print("Current fan speed (Peripheral zone): %d%%" % int(fan_speed2, 16))
  return True


def set_preset(config, preset):
  if preset not in FAN_PRESETS:
    return False

  if ipmi_raw_cmd("0x30 0x45 0x01 0x0%d" % preset, **config):
    print("Updated preset on %s." % config['hostname'])
    return True

  return False

def ipmi_raw_cmd(raw_cmd, hostname = 'localhost', username=None, password=None, use_env=False):

  if hostname == 'localhost':
    if os.geteuid() != 0:
      print("In order to communicate with the kernel's IPMI module, you must be root.")
      sys.exit(1)
    cmd = 'ipmitool raw %s' % raw_cmd
  else:
    if use_env:
      cmd_pass = '-E'
    else:
      cmd_pass = '-P %s' % shlex.quote(password)
    cmd = 'ipmitool -I lanplus -U %s %s -H %s raw %s' % (shlex.quote(username), cmd_pass, hostname, raw_cmd)

  try:
    s = subprocess.check_output(cmd + " 2>&1", shell=True)
  except subprocess.CalledProcessError, ex:
    print("Error: Problem running ipmitool")
    print("Command: %s" % cmd)
    print("Return code: %d" % ex)
    return False

  out = s.strip()
  if out:
    return out
  else:
    return True

def ipmi_fan_status(hostname = 'localhost', username=None, password=None, use_env=False):
  cmd = 'ipmitool sensor | grep FAN'

  if hostname == 'localhost':
    if os.geteuid() != 0:
      print("In order to communicate with the kernel's IPMI module, you must be root.")
      sys.exit(1)
    cmd = 'ipmitool sensor | grep FAN '
  else:
    if use_env:
      cmd_pass = '-E'
    else:
      cmd_pass = '-P %s' % shlex.quote(password)
    cmd = 'ipmitool -I lanplus -U %s %s -H %s sensor | grep FAN' % (shlex.quote(username), cmd_pass, hostname)
  try:
    s = subprocess.check_output(cmd + " 2>&1", shell=True)
  except subprocess.CalledProcessError, ex:
    print("Error: Problem running ipmitool")
    print("Command: %s" % cmd)
    print("Return code: %d" % ex)
    return False

  fan_status_return = {}
  for fan_str in s.split("\n"):
    if len(fan_str.strip()) > 0:
      fan_stat = fan_str.split("|")
      fan_name = fan_stat[0].strip()
      try:
        fan_rpm = float(fan_stat[1].strip())
        fan_status_return[fan_name] = fan_rpm
      except ValueError:
        pass
  return fan_status_return

def get_preset(config):
  try:
    s = ipmi_raw_cmd('0x30 0x45 0x00', **config)
    if s is False:
      return False
    return int(s)
  except:
    return False

if __name__ == "__main__":
  
  superfan_config = dict(hostname= 'localhost')
  for zone_key in FAN_ZONES_MEMBERS.keys():
    current_fan_levels = get_fan(superfan_config, FAN_ZONES_MEMBERS[zone_key], in_rpm=True)
    print('FAN zone %s: %s' % (FAN_ZONES_STR[zone_key],",".join([str(p) for p in current_fan_levels.values()])))

