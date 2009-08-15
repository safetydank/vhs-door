#!/usr/bin/env python

# a q'n'd script to set the serial_device and video_device
# on bootup.  sometimes these nodes would get swapped
# around, this script just sets them to the first ones it
# finds.

from __future__ import with_statement
import os, logging, yaml, re
from StringIO import StringIO

YAML_CONFIG = '/etc/vhs.yaml'

class DeviceNotFoundError(Exception): pass

def find_device(template, N=10):
    for i in range(N):
        device_path = template % i
        if os.path.exists(device_path):
            return device_path
    else:
        raise DeviceNotFoundError(template)

if __name__ == '__main__':
    input = file(YAML_CONFIG).read()
    config = yaml.load(StringIO(input))

    rewrites = []
    for device, template in ( ('serial_device', '/dev/ttyUSB%d'),
                                ('video_device', '/dev/video%d') ):
        device_path = config.get(device)
        if not device_path or not os.path.exists(device_path):
            try:
                config[device] = find_device(template)
                rewrites.append((device, find_device(template)))
            except DeviceNotFoundError, e:
                logging.error(str(e))

    if rewrites:
        output = []
        for line in input.splitlines():
            for device, device_path in rewrites:
                line = re.sub(r'%s: (.*)$' % device, 
                               '%s: %s' % (device, device_path),   # lame
                               line)
            output.append(line + '\n')

        with file(YAML_CONFIG, 'w') as fp:
            fp.writelines(output)
    
